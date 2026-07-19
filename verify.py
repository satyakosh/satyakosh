#!/usr/bin/env python3
"""Satyakosh standalone chain verifier.

One file, standard library only, and deliberately independent of
ledger.py: everything here is re-derived from SCHEMA.md (s7 canonical
serialization, s8 chain mechanics), so agreement between this tool and
the reference engine is evidence, not tautology. Anyone can download
this single file and check any published chain without trusting the
maintainers.

Usage:
    python verify.py CHAIN.json                 verify the whole chain
    python verify.py CHAIN.json --fact FACT_ID  one fact + its status
    python verify.py CHAIN.json --json          machine-readable output

Exit codes: 0 chain intact | 1 findings | 2 cannot read input.

Verification performed (SCHEMA s7/s8/s11):
  - every record's content_hash re-derived from its canonical bytes
    (RFC 8785-style: NFC strings, sorted keys, compact separators,
    UTF-8; content_hash and prev_record_hash excluded from the body)
  - every fact's triple_hash re-derived from the canonical triple
    (conditions sorted by property, tie-broken by the condition
    object's canonical bytes) and checked against the fact_id prefix
  - the prev_record_hash linkage walked from record 0 (genesis, 64
    zeros) and the chain head re-derived and compared to the stored one
  - supersession status DERIVED from the chain (a record is superseded
    iff a later record names it in `supersedes`) -- never trusted from
    any stored field
Hostile input never crashes the verifier: malformed records become
findings (CORRUPT/INVALID), mirroring the reference engine's contract.
"""
import argparse
import hashlib
import json
import sys
import unicodedata

GENESIS_PREV = "0" * 64


# ------------------------------------------------ canonical bytes (s7)
def _nfc(o):
    if isinstance(o, str):
        return unicodedata.normalize("NFC", o)
    if isinstance(o, list):
        return [_nfc(x) for x in o]
    if isinstance(o, dict):
        return {_nfc(k): _nfc(v) for k, v in o.items()}
    return o


def _no_floats(o):
    if isinstance(o, float):
        raise ValueError("JSON float in canonical form (s7.1)")
    if isinstance(o, list):
        for x in o:
            _no_floats(x)
    elif isinstance(o, dict):
        for v in o.values():
            _no_floats(v)


def jcs(o):
    _no_floats(o)
    return json.dumps(_nfc(o), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def content_hash(record):
    body = {k: v for k, v in record.items()
            if k not in ("content_hash", "prev_record_hash")}
    return sha(jcs(body))


def triple_hash(triple):
    t = dict(triple)
    t["conditions"] = sorted(
        t.get("conditions", []),
        key=lambda c: (c["property"], jcs(c["object"])))
    return sha(jcs(t))


# ------------------------------------------------ verification (s8/s11)
def verify_chain(records):
    findings = []
    prev = GENESIS_PREV
    link = GENESIS_PREV
    if not records:
        findings.append("EMPTY: chain has no records")
    elif records[0].get("record_type") != "genesis":
        findings.append("INVALID record 0: not a genesis record (s8)")
    for i, r in enumerate(records):
        rid = r.get("fact_id", r.get("record_type", "?")) \
            if isinstance(r, dict) else "?"
        if not isinstance(r, dict):
            findings.append(f"CORRUPT record {i}: not an object")
            continue
        try:
            if r.get("prev_record_hash") != prev:
                findings.append(f"BROKEN LINK at record {i} ({rid}): "
                                f"prev_record_hash does not match the "
                                f"preceding record")
            ch = content_hash(r)
            if ch != r.get("content_hash"):
                findings.append(f"TAMPERED record {i} ({rid}): stored "
                                f"content_hash does not match its bytes")
            if r.get("record_type") == "fact":
                th = triple_hash(r["triple"])
                if th != r.get("triple_hash"):
                    findings.append(f"TAMPERED TRIPLE record {i} ({rid})")
                fid = r.get("fact_id", "")
                suffix = fid.rsplit("-", 1)[-1] if isinstance(fid, str) else ""
                if not th.startswith(suffix):
                    findings.append(f"INVALID record {i} ({rid}): fact_id "
                                    f"suffix is not a prefix of triple_hash")
            prev = r.get("content_hash")
            link = sha((str(r.get("content_hash")) + link).encode(
                "ascii", errors="replace"))
        except Exception as e:  # noqa: BLE001 -- hostile input -> finding
            findings.append(f"CORRUPT record {i} ({rid}): "
                            f"{type(e).__name__}: {e}")
            prev = r.get("content_hash")
    return findings, link


def derive_status(records, fact_id):
    """Supersession state, derived from the chain alone."""
    versions = {}
    superseded_by = {}
    for r in records:
        if not isinstance(r, dict) or r.get("record_type") != "fact":
            continue
        if r.get("fact_id") == fact_id:
            versions[r.get("version")] = r
        sup = r.get("supersedes")
        if isinstance(sup, str) and "@" in sup:
            superseded_by[sup] = f"{r.get('fact_id')}@{r.get('version')}"
    if not versions:
        return None
    latest = max(versions)
    key = f"{fact_id}@{latest}"
    return {
        "fact_id": fact_id,
        "versions": sorted(versions),
        "latest_version": latest,
        "record": versions[latest],
        "status": "superseded" if key in superseded_by else "live",
        "superseded_by": superseded_by.get(key),
    }


def main():
    ap = argparse.ArgumentParser(description="Verify a Satyakosh chain.")
    ap.add_argument("chain", help="path to the published chain JSON")
    ap.add_argument("--fact", help="verify and report one fact_id")
    ap.add_argument("--json", action="store_true",
                    help="machine-readable output")
    args = ap.parse_args()

    try:
        with open(args.chain, encoding="utf-8") as f:
            data = json.load(f)
        records = data["records"]
        stored_head = data.get("chain_head")
    except Exception as e:  # noqa: BLE001
        print(f"cannot read chain file: {type(e).__name__}: {e}",
              file=sys.stderr)
        return 2

    findings, head = verify_chain(records)
    if stored_head is not None and stored_head != head:
        findings.append("CHAIN HEAD MISMATCH: stored head does not match "
                        "the recomputed head")

    fact_report = None
    if args.fact:
        fact_report = derive_status(records, args.fact)
        if fact_report is None:
            findings.append(f"FACT NOT FOUND: {args.fact}")

    if args.json:
        out = {"records": len(records), "chain_head": head,
               "intact": not findings, "findings": findings}
        if fact_report:
            out["fact"] = {k: v for k, v in fact_report.items()
                           if k != "record"}
            out["fact"]["triple"] = fact_report["record"].get("triple")
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"records: {len(records)}")
        print(f"chain head (recomputed): {head}")
        if fact_report:
            fr = fact_report
            print(f"fact {fr['fact_id']}: versions {fr['versions']}, "
                  f"latest v{fr['latest_version']}, status {fr['status']}"
                  + (f" (superseded by {fr['superseded_by']})"
                     if fr["superseded_by"] else ""))
            trip = fr["record"].get("triple", {})
            obj = trip.get("object", {})
            print(f"  triple: {trip.get('subject')} "
                  f"-[{trip.get('predicate')}]-> "
                  f"{obj.get('value')} {obj.get('unit', '')} "
                  f"({len(trip.get('conditions', []))} condition(s))")
        if findings:
            print(f"\nNOT INTACT -- {len(findings)} finding(s):")
            for f in findings:
                print("  -", f)
        else:
            print("\nCHAIN INTACT -- every byte accounted for.")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
