#!/usr/bin/env python3
"""Compute the six founding-document hashes enumerated by the genesis
record (SCHEMA s9). Report-only: prints hashes, never edits files.

Hash conventions, per the genesis draft's own placeholder descriptions:
  schema_hash               sha256 of SCHEMA.md file bytes
  pipeline_policy_hash      sha256 of PIPELINE_POLICY.md file bytes
  scope_hash                sha256 of SCOPE.md file bytes
  admissibility_map_hash    sha256 of JCS(rules/admissibility_map.json)
  mandatory_conditions_hash sha256 of rulesets/mandatory_conditions.json
                            file bytes
  predicates_founding_hash  UNSETTLED convention (file bytes vs JCS) --
                            both printed; founder must lock one before
                            the freeze

The tool refuses to present freeze-ready output while the mandatory-
conditions ruleset carries operative placeholders (same rule ledger.py
enforces at seal time).

Run:  python3 tools/genesis_hashes.py
"""
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
sys.path.insert(0, str(REPO / "tools"))
import ledger as L
from check_mandatory_conditions import operative_placeholders


def file_sha256(rel):
    return hashlib.sha256((REPO / rel).read_bytes()).hexdigest()


def jcs_sha256(rel):
    obj = json.loads((REPO / rel).read_text(encoding="utf-8"))
    return L.sha256_hex(L.jcs(obj))


def main():
    print("Founding-document hashes (current working bytes, NOT frozen):\n")
    rows = [
        ("schema_hash", file_sha256("SCHEMA.md"), "SCHEMA.md file bytes"),
        ("pipeline_policy_hash", file_sha256("PIPELINE_POLICY.md"),
         "PIPELINE_POLICY.md file bytes"),
        ("scope_hash", file_sha256("SCOPE.md"), "SCOPE.md file bytes"),
        ("admissibility_map_hash", jcs_sha256("rules/admissibility_map.json"),
         "JCS(rules/admissibility_map.json)"),
        ("mandatory_conditions_hash",
         file_sha256("rulesets/mandatory_conditions.json"),
         "rulesets/mandatory_conditions.json file bytes"),
    ]
    for name, digest, basis in rows:
        print(f"  {name}\n    {digest}  <- {basis}")
    print("  predicates_founding_hash  [CONVENTION NOT LOCKED - founder "
          "must choose]")
    print(f"    {file_sha256('registries/predicates.json')}  "
          f"<- if file bytes")
    print(f"    {jcs_sha256('registries/predicates.json')}  "
          f"<- if JCS(registries/predicates.json)")

    mc = json.loads((REPO / "rulesets/mandatory_conditions.json")
                    .read_text(encoding="utf-8"))
    hits = operative_placeholders(mc)
    print()
    if hits:
        print(f"NOT FREEZE-READY: {len(hits)} operative placeholder(s) in "
              f"rulesets/mandatory_conditions.json:")
        for h in hits:
            print("  -", h)
        print("Resolve them (and founder-review every founding document) "
              "before treating any hash above as final.")
        return 1
    print("mandatory-conditions ruleset is placeholder-free; hashes above "
          "are candidates for the freeze after founder review.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
