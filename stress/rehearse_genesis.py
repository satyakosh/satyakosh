#!/usr/bin/env python3
"""Genesis seal rehearsal — the full ceremony on a STAGING chain.

Runs everything the real freeze-day seal will run, against the
committed working bytes, without ever touching a real chain:

  1. compute the six founding-document hashes (FD-12 conventions)
  2. fill a COPY of genesis_record.draft.json (staging timestamp)
  3. seal it as record 0 via ledger.py; verify() and verify(full=True)
  4. recompute content_hash and the chain head with an INDEPENDENT
     second implementation — pure stdlib, no ledger.py import — the
     "second person" of the ceremony. Both paths must agree.

Deterministic (fixed staging timestamp): the staged chain head changes
only when committed bytes change. Runs in CI so freeze-readiness is
proven continuously, not discovered on freeze day.

Run:  python3 stress/rehearse_genesis.py
"""
import copy
import hashlib
import json
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
import ledger as L

STAGING_CREATED = "2026-07-18T00:00:00Z"


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


# ---------- step 1: the six hashes, FD-12 conventions ----------------
def compute_hashes():
    def file_sha(rel):
        return hashlib.sha256((REPO / rel).read_bytes()).hexdigest()

    def jcs_sha(rel):
        return L.sha256_hex(L.jcs(load(rel)))

    return {
        "schema_hash": file_sha("SCHEMA.md"),
        "pipeline_policy_hash": file_sha("PIPELINE_POLICY.md"),
        "scope_hash": file_sha("SCOPE.md"),
        "admissibility_map_hash": jcs_sha("rules/admissibility_map.json"),
        "mandatory_conditions_hash": jcs_sha("rulesets/mandatory_conditions.json"),
        "predicates_founding_hash": jcs_sha("registries/predicates.json"),
    }


# ---------- step 4: the independent second implementation ------------
# Pure stdlib, no ledger.py: re-derives canonical bytes from the spec
# (SCHEMA s7): NFC-normalize strings, JCS-style dump (sorted keys,
# compact separators, UTF-8), SHA-256; content_hash excludes the two
# chain fields; chain_link = SHA-256(content ‖ prev) over hex.
def _nfc(o):
    if isinstance(o, str):
        return unicodedata.normalize("NFC", o)
    if isinstance(o, list):
        return [_nfc(x) for x in o]
    if isinstance(o, dict):
        return {_nfc(k): _nfc(v) for k, v in o.items()}
    return o


def independent_content_hash(record):
    body = {k: v for k, v in record.items()
            if k not in ("content_hash", "prev_record_hash")}
    raw = json.dumps(_nfc(body), sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def independent_chain_head(records):
    link = "0" * 64
    for r in records:
        link = hashlib.sha256(
            (r["content_hash"] + link).encode("ascii")).hexdigest()
    return link


def main():
    failures = []

    # step 2: fill a copy of the draft
    g = load("genesis_record.draft.json")
    staged = copy.deepcopy(g)
    for k, v in compute_hashes().items():
        assert "PLACEHOLDER" in str(staged.get(k)), \
            f"{k} in the draft is no longer a placeholder"
        staged[k] = v
    staged["created"] = STAGING_CREATED
    del staged["content_hash"]  # computed by seal

    # inscription must already be final — no placeholder may remain
    leftover = [k for k, v in staged.items()
                if isinstance(v, str) and "PLACEHOLDER" in v]
    if leftover:
        failures.append(f"non-freeze-time placeholders remain: {leftover}")

    # step 3: seal on a staging chain
    registries = {k: load(f"registries/{k}.json")
                  for k in ("entities", "predicates", "sources")}
    rulesets = {"mandatory_conditions": load("rulesets/mandatory_conditions.json"),
                "admissibility_map": load("rules/admissibility_map.json")}
    led = L.Ledger(None, registries, rulesets)
    try:
        sealed = led.seal(staged)
    except L.ValidationError as e:
        print(f"REHEARSAL FAIL: genesis refused to seal: {e}")
        return 1
    for name, findings in (("verify()", led.verify()),
                           ("verify(full)", led.verify(full=True))):
        if findings:
            failures.append(f"{name} reported: {findings[:2]}")

    # step 4: independent recomputation (no ledger.py)
    ind_content = independent_content_hash(sealed)
    if ind_content != sealed["content_hash"]:
        failures.append(
            f"content_hash mismatch: ledger {sealed['content_hash'][:16]} "
            f"vs independent {ind_content[:16]}")
    ind_head = independent_chain_head(led.records)
    eng_head = led.chain_head()
    if ind_head != eng_head:
        failures.append(
            f"chain head mismatch: ledger {eng_head[:16]} vs "
            f"independent {ind_head[:16]}")

    if failures:
        print("REHEARSAL FAIL:")
        for f in failures:
            print("  -", f)
        return 1
    print("REHEARSAL PASS - genesis seals cleanly on staging")
    print(f"  staged content_hash: {sealed['content_hash']}")
    print(f"  staged chain head:   {eng_head}")
    print(f"  independent second implementation agrees on both")
    print("  (staging timestamp; real values bind at the real seal)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
