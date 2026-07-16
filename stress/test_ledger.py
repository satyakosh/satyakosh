#!/usr/bin/env python3
"""Deterministic test suite for ledger.py (SCHEMA s8/s9/s11 behaviors).

Positive-path cases run against an in-memory copy of the founding
rulesets with the four placeholder entity IDs resolved to the suggested
(founder-unconfirmed) registry IDs; nothing here touches the real files.

Run:  python3 stress/test_ledger.py
"""
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
import ledger as L


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


REGISTRIES = {"entities": load("registries/entities.json"),
              "predicates": load("registries/predicates.json"),
              "sources": load("registries/sources.json")}
RAW_RULESETS = {"mandatory_conditions": load("rulesets/mandatory_conditions.json"),
                "admissibility_map": load("rules/admissibility_map.json")}


def resolved_rulesets():
    """The founding rulesets as committed (placeholder-free since the
    founder confirmed the entity IDs on 2026-07-17)."""
    return copy.deepcopy(RAW_RULESETS)


def placeholder_rulesets():
    """Synthetic placeholder-bearing copy for the refusal test."""
    rs = copy.deepcopy(RAW_RULESETS)
    rs["mandatory_conditions"]["subject_rules"][0]["subject"] = \
        "<SK-ENT: boiling temperature of water>"
    return rs


def make_genesis():
    g = load("genesis_record.draft.json")
    for k, v in list(g.items()):
        if isinstance(v, str) and "PLACEHOLDER" in v:
            g[k] = "e" * 64 if k.endswith("_hash") else "2026-07-18T00:00:00Z"
    g["inscription"]["mission"] = "Test mission prose (synthetic genesis)."
    return g


def make_fact(value="2.99792458e8", subject="SK-ENT-000001", conds=None,
              dtype="si_exact_definition", supersedes=None):
    triple = {"subject": subject, "predicate": "SK-PRED-000001",
              "object": {"type": "quantity", "value": value, "unit": "m/s",
                         "exact": True, "uncertainty": None},
              "conditions": conds or []}
    th = L.triple_hash(triple)
    return {"record_type": "fact", "fact_id": f"SK-R1-PHYS-{th[:12]}",
            "triple_hash": th, "version": 1, "supersedes": supersedes,
            "triple": triple, "ring": 1, "truth_type": "always",
            "valid_from": None, "valid_until": None,
            "valid_until_expected": False,
            "sources": [{"source": "SK-SRC-000001", "edition": "CODATA 2022",
                         "retrieved": "2026-07-01"}],
            "derivation": {"type": dtype},
            "process_hash": "a" * 64, "status": "sealed",
            "created": "2026-07-18T00:00:00Z"}


RESULTS = []


def check(name, fn, expect_reject, expect_msg=""):
    try:
        fn()
        ok, actual = not expect_reject, "sealed"
    except L.ValidationError as e:
        actual = f"reject: {str(e)[:58]}"
        ok = expect_reject and (expect_msg in str(e))
    except Exception as e:  # noqa: BLE001 - a crash is always a failure
        ok, actual = False, f"CRASH {type(e).__name__}: {str(e)[:50]}"
    RESULTS.append((ok, name, actual))


def run():
    led = L.Ledger(Path("unused.json"), REGISTRIES, resolved_rulesets())

    # SCHEMA s8: record 0 must be genesis
    check("fact as record 0 refused", lambda: led.seal(make_fact()),
          True, "record 0 must be genesis")
    check("genesis seals as record 0", lambda: led.seal(make_genesis()), False)
    check("valid fact seals after genesis", lambda: led.seal(make_fact()), False)

    # SCHEMA s11: duplicate detection is an exact hash lookup
    check("duplicate triple refused", lambda: led.seal(make_fact()),
          True, "duplicate triple_hash")
    f = make_fact()
    f["version"] = 2
    f["supersedes"] = f["fact_id"] + "@1"
    check("metadata supersession of same triple allowed",
          lambda: led.seal(f), False)
    check("different triple still seals",
          lambda: led.seal(make_fact(value="1e0")), False)

    # mandatory conditions (resolved test ruleset)
    Q = {"type": "quantity", "value": "1.01325e2", "unit": "kPa",
         "exact": True, "uncertainty": None}
    both = sorted([{"property": "SK-ENT-000006", "object": Q},
                   {"property": "SK-ENT-000007", "object": Q}],
                  key=lambda c: c["property"])
    check("boiling pt w/o conditions refused", lambda: led.seal(
        make_fact(subject="SK-ENT-000005", dtype="laboratory_measurement")),
        True, "required condition")
    check("boiling pt with both conditions seals", lambda: led.seal(
        make_fact(subject="SK-ENT-000005", conds=both,
                  dtype="laboratory_measurement")), False)

    # placeholder-bearing rulesets refuse every fact seal
    led_ph = L.Ledger(Path("unused2.json"), REGISTRIES,
                      placeholder_rulesets())
    led_ph.records = led.records[:1]
    check("fact refused while ruleset has placeholders",
          lambda: led_ph.seal(make_fact()), True, "placeholder")

    # malformed input -> citable rejection, never a crash
    def drop(path):
        f = make_fact()
        d = f
        for k in path[:-1]:
            d = d[k]
        del d[path[-1]]
        if "triple" in path:
            try:
                f["triple_hash"] = L.triple_hash(f["triple"])
                f["fact_id"] = "SK-R1-PHYS-" + f["triple_hash"][:12]
            except Exception:
                pass
        return f
    for path in (["triple", "object", "value"], ["triple", "subject"],
                 ["triple", "object"], ["derivation", "type"]):
        check(f"missing {'.'.join(path)} -> ValidationError",
              lambda p=path: led.seal(drop(p)), True)

    def bad_cond():
        f = make_fact(value="7e0")
        f["triple"]["conditions"] = ["oops"]
        led.seal(f)
    check("non-dict condition -> ValidationError", bad_cond,
          True, "malformed condition entry")

    # canonical-form rejections
    def with_val(v):
        f = make_fact()
        f["triple"]["object"]["value"] = v
        f["triple_hash"] = L.triple_hash(f["triple"])
        f["fact_id"] = "SK-R1-PHYS-" + f["triple_hash"][:12]
        led.seal(f)
    check("grammar: plain integer refused",
          lambda: with_val("299792458"), True, "grammar")

    def homoglyph():
        f = make_fact(value="5e0")
        f["triple"]["object"]["unit"] = "m/ѕ"  # Cyrillic s
        f["triple_hash"] = L.triple_hash(f["triple"])
        f["fact_id"] = "SK-R1-PHYS-" + f["triple_hash"][:12]
        led.seal(f)
    check("homoglyph unit refused", homoglyph, True, "non-ASCII")

    # admissibility
    check("blocked derivation refused", lambda: led.seal(
        make_fact(value="2e0", dtype="causal_inference")), True)
    check("unknown derivation refused", lambda: led.seal(
        make_fact(value="3e0", dtype="si_exact_defintion")), True)

    # tamper detection
    led.records[1]["triple"]["object"]["value"] = "9e9"
    findings = led.verify()
    RESULTS.append((any("TAMPERED" in x for x in findings),
                    "tamper detection", f"{len(findings)} finding(s)"))

    fails = sum(1 for ok, _, _ in RESULTS if not ok)
    w = max(len(n) for _, n, _ in RESULTS)
    for ok, name, actual in RESULTS:
        print(("PASS" if ok else "FAIL"), "-", name.ljust(w), "|", actual)
    print(f"\n{len(RESULTS) - fails}/{len(RESULTS)} cases passed")
    return fails == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
