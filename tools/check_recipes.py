#!/usr/bin/env python3
"""check_recipes.py — derivation.script artifact check (intake + CI).

Closes the "seal but broken" path the G1 re-read named: a proposal or
sealed fact whose `derivation.script` names a recipe that is missing
from derivations/ or whose bytes have drifted from the pinned SHA-256.
ledger.py deliberately validates bytes, not the filesystem (SCHEMA
s4.1 note); this tool is the filesystem half, run at intake and in CI.

Scope (deliberate): existence + hash. "Runs clean" is a REVIEW-step
duty (the reviewer executes the recipe per the review-file format) —
executing arbitrary recipe files in CI is not attempted here, and that
limitation is recorded in GENESIS_AMENDMENTS.

Usage:
    python3 tools/check_recipes.py                    # self-test
    python3 tools/check_recipes.py FILE.json [...]    # check file(s)
    python3 tools/check_recipes.py --repo DIR FILE.json

FILE.json may be a chain ({"records": [...]}), a proposal list, or a
single proposal object ({"triple": ..., "derivation": ...}). Entries
whose derivation.script is null are out of scope (no recipe pinned).
Exit codes: 0 all pinned recipes present and matching | 1 violations.
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
import ledger as L


def _iter_items(doc):
    """Yield every {triple, derivation} carrier in a chain, list, or
    single proposal."""
    if isinstance(doc, dict) and isinstance(doc.get("records"), list):
        for r in doc["records"]:
            if isinstance(r, dict) and r.get("record_type") == "fact":
                yield r
    elif isinstance(doc, list):
        for r in doc:
            if isinstance(r, dict):
                yield r
    elif isinstance(doc, dict):
        yield doc


def check_file(path, repo):
    """Returns a list of violation strings; empty = clean."""
    violations = []
    try:
        doc = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — hostile input -> violation
        return [f"{path}: cannot read/parse: {type(e).__name__}: {e}"]
    n_pinned = 0
    for item in _iter_items(doc):
        deriv = item.get("derivation")
        if not isinstance(deriv, dict) or deriv.get("script") is None:
            continue
        n_pinned += 1
        label = item.get("fact_id") or item.get("label_hint") or "<proposal>"
        script = deriv["script"]
        if not isinstance(script, str) or not L.HASH_RE.match(script):
            violations.append(
                f"{label}: derivation.script is not a sha256 hex digest")
            continue
        triple = item.get("triple")
        try:
            th = L.triple_hash(triple)
        except Exception as e:  # noqa: BLE001
            violations.append(
                f"{label}: cannot compute triple_hash for recipe lookup: "
                f"{type(e).__name__}: {e}")
            continue
        recipe = Path(repo) / "derivations" / f"{th}.py"
        if not recipe.exists():
            violations.append(
                f"{label}: derivation.script pinned but recipe file "
                f"derivations/{th}.py is MISSING — a fact must never "
                f"seal pointing at an absent recipe")
            continue
        actual = hashlib.sha256(recipe.read_bytes()).hexdigest()
        if actual != script:
            violations.append(
                f"{label}: recipe derivations/{th}.py has DRIFTED — "
                f"bytes hash to {actual[:16]}..., sealed pin is "
                f"{script[:16]}...")
    return violations


def self_test():
    import tempfile
    tmp = Path(tempfile.mkdtemp(prefix="check_recipes_"))
    (tmp / "derivations").mkdir()
    triple = {"subject": "SK-ENT-000001", "predicate": "SK-PRED-000001",
              "object": {"type": "quantity", "value": "1e0", "unit": "m",
                         "exact": True, "uncertainty": None},
              "conditions": []}
    th = L.triple_hash(triple)
    recipe = tmp / "derivations" / f"{th}.py"
    recipe.write_bytes(b"# recipe\nprint('derive')\n")
    good_hash = hashlib.sha256(recipe.read_bytes()).hexdigest()

    def prop(script):
        return {"triple": triple,
                "derivation": {"type": "derived_exact", "script": script,
                               "derived_from": ["SK-R1-PHYS-aaaaaaaaaaaa"]}}

    cases = [
        ("null script out of scope", prop(None), 0),
        ("pinned + present + matching passes", prop(good_hash), 0),
        ("pinned but MISSING recipe fails",
         {**prop(good_hash),
          "triple": {**triple, "conditions": [
              {"property": "SK-ENT-000006",
               "object": {"type": "quantity", "value": "2e0", "unit": "m",
                          "exact": True, "uncertainty": None}}]}}, 1),
        ("drifted bytes fail", prop("f" * 64), 1),
        ("malformed script digest fails", prop("nothex"), 1),
    ]
    fails = 0
    for name, proposal, expect in cases:
        f = tmp / "p.json"
        f.write_text(json.dumps(proposal), encoding="utf-8")
        got = len(check_file(f, tmp))
        ok = got == expect
        fails += not ok
        print(("PASS" if ok else "FAIL"), "-", name,
              f"({got} violation(s), expected {expect})")
    # chain form: a records wrapper is walked the same way
    chain = {"records": [{"record_type": "fact", "fact_id": "SK-R1-X-abc",
                          **prop(good_hash)},
                         {"record_type": "genesis"}]}
    f = tmp / "c.json"
    f.write_text(json.dumps(chain), encoding="utf-8")
    ok = check_file(f, tmp) == []
    fails += not ok
    print(("PASS" if ok else "FAIL"), "- chain wrapper walked, clean")
    print(f"\n{6 - fails}/6 cases passed")
    return fails == 0


def main(argv):
    if not argv:
        return 0 if self_test() else 1
    repo = REPO
    if argv[0] == "--repo":
        repo = Path(argv[1])
        argv = argv[2:]
    all_v = []
    for path in argv:
        all_v.extend(check_file(path, repo))
    if all_v:
        print(f"RECIPE CHECK FAILED — {len(all_v)} violation(s):")
        for v in all_v:
            print("  -", v)
        return 1
    print("recipe check clean: every pinned derivation.script has a "
          "present, byte-matching recipe file")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
