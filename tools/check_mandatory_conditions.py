#!/usr/bin/env python3
"""check_mandatory_conditions.py - RECONSTRUCTED reference implementation.

Enforces rulesets/mandatory_conditions.json at intake. The lost original
passed an 11-case self-test; this reconstruction ships its own self-test
covering the same specified behaviors. Re-run before any report cites it:
    python3 tools/check_mandatory_conditions.py                # self-test
    python3 tools/check_mandatory_conditions.py RULESET.json   # placeholder scan
    python3 tools/check_mandatory_conditions.py RULESET.json PROPOSAL.json
"""
import json, re, sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"<SK-ENT:")

def load_ruleset(path):
    return json.loads(Path(path).read_text())

def operative_placeholders(ruleset):
    """Placeholders in operative (non-underscore) fields only."""
    hits = []
    def walk(obj, keypath):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k.startswith("_"):
                    continue
                walk(v, keypath + [k])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, keypath + [str(i)])
        elif isinstance(obj, str) and PLACEHOLDER_RE.search(obj):
            hits.append("/".join(keypath) + " = " + obj)
    walk(ruleset, [])
    return hits

def check_proposal(triple, derivation_type, ruleset):
    """Returns list of violation strings; empty = passes the gate."""
    violations = []
    if not isinstance(triple, dict) or not isinstance(triple.get("subject"), str):
        violations.append(
            "malformed proposal: triple must be an object with a string "
            "'subject' (SCHEMA s3.1)")
        return violations
    conds = triple.get("conditions", [])
    if not isinstance(conds, list) or not all(
            isinstance(c, dict) and isinstance(c.get("property"), str)
            for c in conds):
        violations.append(
            "malformed proposal: each condition must be an object with a "
            "string 'property' (SCHEMA s3.4)")
        return violations
    if not isinstance(derivation_type, str):
        violations.append(
            "malformed proposal: derivation type must be a string (SCHEMA s4)")
        return violations
    dt_map = ruleset["derivation_type_rules"]
    if derivation_type not in dt_map:
        violations.append(
            f"unknown derivation type '{derivation_type}' — not in the "
            f"mandatory-conditions map; check the spelling against "
            f"rules/admissibility_map.json")
        return violations
    dt_rules = dt_map[derivation_type]
    if dt_rules is None:
        violations.append(
            f"derivation type '{derivation_type}' is BLOCKED by the "
            f"admissibility map; no intake path exists")
        return violations
    required = list(dt_rules)
    for rule in ruleset.get("subject_rules", []):
        if rule["subject"] == triple["subject"]:
            required += rule["requires"]
    present = {c["property"] for c in conds}
    for req in required:
        if req not in present:
            violations.append(
                f"required condition property {req} absent for subject "
                f"{triple['subject']} / derivation '{derivation_type}' "
                f"(mandatory_conditions ruleset)")
    return violations

# ------------------------------------------------------------- self-test
def self_test():
    rs = {
        "derivation_type_rules": {
            "si_exact_definition": [], "laboratory_measurement": [],
            "statistical_analysis": ["SK-ENT-000008"],
            "causal_inference": None,
        },
        "subject_rules": [
            {"subject": "SK-ENT-000005",
             "requires": ["SK-ENT-000006", "SK-ENT-000007"]}
        ],
    }
    Q = lambda: {"type": "quantity", "value": "1e0", "unit": "1",
                 "exact": True, "uncertainty": None}
    cond = lambda p: {"property": p, "object": Q()}
    t = lambda subj, conds: {"subject": subj, "predicate": "SK-PRED-000001",
                             "object": Q(), "conditions": conds}
    cases = [
        # (name, triple, derivation, expect_pass)
        ("constant, no conditions", t("SK-ENT-000001", []), "si_exact_definition", True),
        ("measurement, condition-independent subject", t("SK-ENT-000003", []), "laboratory_measurement", True),
        ("boiling point, both conditions", t("SK-ENT-000005", [cond("SK-ENT-000006"), cond("SK-ENT-000007")]), "laboratory_measurement", True),
        ("boiling point, missing pressure", t("SK-ENT-000005", [cond("SK-ENT-000007")]), "laboratory_measurement", False),
        ("boiling point, missing scale", t("SK-ENT-000005", [cond("SK-ENT-000006")]), "laboratory_measurement", False),
        ("boiling point, no conditions", t("SK-ENT-000005", []), "laboratory_measurement", False),
        ("statistical without method", t("SK-ENT-000001", []), "statistical_analysis", False),
        ("statistical with method", t("SK-ENT-000001", [cond("SK-ENT-000008")]), "statistical_analysis", True),
        ("blocked derivation type", t("SK-ENT-000001", []), "causal_inference", False),
        ("unknown derivation type (typo)", t("SK-ENT-000001", []), "si_exact_defintion", False),
        ("extra unrelated condition ok", t("SK-ENT-000001", [cond("SK-ENT-000006")]), "si_exact_definition", True),
        ("boiling point, extra condition + both required", t("SK-ENT-000005", [cond("SK-ENT-000006"), cond("SK-ENT-000007"), cond("SK-ENT-000008")]), "laboratory_measurement", True),
        ("malformed: triple missing subject", {"conditions": []}, "si_exact_definition", False),
        ("malformed: non-dict condition entry", {"subject": "SK-ENT-000001", "conditions": ["oops"]}, "si_exact_definition", False),
    ]
    passed = 0
    for name, triple, dtype, expect_pass in cases:
        v = check_proposal(triple, dtype, rs)
        ok = (not v) == expect_pass
        print(("PASS" if ok else "FAIL"), "-", name, ("" if ok else f" -> {v}"))
        passed += ok
    # placeholder-guard cases
    with_ph = dict(rs); with_ph["subject_rules"] = [
        {"subject": "<SK-ENT: boiling temperature of water>", "requires": []}]
    g1 = len(operative_placeholders(with_ph)) == 1
    g2 = len(operative_placeholders(
        {"_notes": "<SK-ENT: commentary only>", "derivation_type_rules": {}})) == 0
    print("PASS" if g1 else "FAIL", "- placeholder guard fires on operative field")
    print("PASS" if g2 else "FAIL", "- placeholder guard silent on commentary")
    passed += g1 + g2
    total = len(cases) + 2
    print(f"\n{passed}/{total} cases passed")
    return passed == total

def main(argv):
    """CLI. No args: run the self-test.
    1 arg:  check a real ruleset file for operative placeholders.
    2 args: additionally gate a proposal file ({"triple": ..., "derivation":
            {"type": ...}}) against that ruleset. Exit 0 = passes."""
    if not argv:
        return 0 if self_test() else 1
    try:
        ruleset = load_ruleset(argv[0])
    except (OSError, json.JSONDecodeError) as e:
        print(f"cannot load ruleset {argv[0]}: {e}")
        return 2
    hits = operative_placeholders(ruleset)
    for h in hits:
        print("PLACEHOLDER (operative):", h)
    if hits:
        print(f"\n{len(hits)} operative placeholder(s) -- nothing can seal "
              f"against this ruleset until they are resolved")
    else:
        print("ruleset placeholder-free in operative fields")
    if len(argv) < 2:
        return 1 if hits else 0
    try:
        proposal = json.loads(Path(argv[1]).read_text())
        triple = proposal["triple"]
        dtype = proposal["derivation"]["type"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"cannot load proposal {argv[1]}: needs triple + "
              f"derivation.type ({e})")
        return 2
    violations = check_proposal(triple, dtype, ruleset)
    for v in violations:
        print("VIOLATION:", v)
    print("proposal passes the mandatory-conditions gate" if not violations
          else f"\n{len(violations)} violation(s) -- never enters review")
    return 1 if (hits or violations) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
