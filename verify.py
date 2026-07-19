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
    python verify.py CHAIN.json --repo DIR      additionally bind the
        genesis-declared founding-document hashes and inline whitelist
        against the repository files at DIR (s9: prose documents hash as
        file bytes, JSON documents as their JCS serialization; a later
        doc_supersession or ruleset_change governance record updates the
        expected hash for its document)

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


def verify_repo_bindings(records, repo):
    """Bind the genesis-declared digests to the repository's actual
    files (s9; issue #7 G3/G4). The declared hashes are enumeration
    with teeth: a repo whose rulesets do not hash to what its own
    genesis declares is not the repo the chain was sealed under.

    Chain governance is honored: the latest doc_supersession for a
    prose document, or ruleset_change for a JSON ruleset, replaces the
    expected hash — the chain, not the file, is authoritative.
    Findings-only; hostile input never crashes (same contract as
    verify_chain)."""
    import os.path
    findings = []
    genesis = records[0] if records and isinstance(records[0], dict) and \
        records[0].get("record_type") == "genesis" else None
    if genesis is None:
        return ["REPO BINDING SKIPPED: record 0 is not a genesis record"]

    # fold governance: latest supersession/change per document wins
    doc_hash = {}      # prose filename -> superseding hash
    ruleset_new = {}   # ruleset target -> superseding content
    saw_wl_change = False
    for r in records[1:]:
        if not isinstance(r, dict) or r.get("record_type") != "governance":
            continue
        kind, delta = r.get("governance_kind"), r.get("delta")
        if not isinstance(delta, dict):
            continue
        if kind == "doc_supersession":
            doc_hash[delta.get("document")] = delta.get("new_hash")
        elif kind == "ruleset_change":
            ruleset_new[delta.get("target")] = delta.get("content")
        elif kind == "whitelist_change":
            saw_wl_change = True

    def check(label, declared, actual_fn):
        try:
            actual = actual_fn()
        except Exception as e:  # noqa: BLE001 -- missing/hostile file
            findings.append(f"REPO BINDING: cannot read {label}: "
                            f"{type(e).__name__}: {e}")
            return
        if actual != declared:
            findings.append(
                f"REPO BINDING MISMATCH: {label} hashes to {actual[:16]}"
                f"..., but the chain declares {str(declared)[:16]}... — "
                f"the file is not the one the chain binds")

    def file_sha(rel):
        with open(os.path.join(repo, rel), "rb") as f:
            return sha(f.read())

    def jcs_sha(rel):
        with open(os.path.join(repo, rel), encoding="utf-8") as f:
            return sha(jcs(json.load(f)))

    prose = [("SCHEMA.md", "schema_hash"),
             ("PIPELINE_POLICY.md", "pipeline_policy_hash"),
             ("SCOPE.md", "scope_hash")]
    for fname, field in prose:
        declared = doc_hash.get(fname, genesis.get(field))
        check(fname, declared, lambda rel=fname: file_sha(rel))

    rulesets = [("rules/admissibility_map.json", "admissibility_map",
                 "admissibility_map_hash"),
                ("rulesets/mandatory_conditions.json", "mandatory_conditions",
                 "mandatory_conditions_hash")]
    for rel, target, field in rulesets:
        if target in ruleset_new:
            declared = sha(jcs(ruleset_new[target]))
        else:
            declared = genesis.get(field)
        check(rel, declared, lambda r=rel: jcs_sha(r))

    check("registries/predicates.json",
          genesis.get("predicates_founding_hash"),
          lambda: jcs_sha("registries/predicates.json"))

    # inline whitelist vs sources file ({id, publisher, rings}
    # projection). Only meaningful while no whitelist_change has sealed:
    # after one, the chain alone carries the in-force whitelist.
    if not saw_wl_change:
        try:
            with open(os.path.join(repo, "registries/sources.json"),
                      encoding="utf-8") as f:
                srcs = json.load(f)["sources"]
            file_proj = {s["id"]: (s["publisher"], tuple(s["rings"]))
                         for s in srcs}
            inline_proj = {e["id"]: (e["publisher"], tuple(e["rings"]))
                           for e in genesis.get("whitelist", [])}
            if file_proj != inline_proj:
                findings.append(
                    "REPO BINDING MISMATCH: registries/sources.json "
                    "diverges from the genesis inline whitelist — the "
                    "inline enumeration is authoritative (s9)")
        except Exception as e:  # noqa: BLE001
            findings.append(f"REPO BINDING: cannot read "
                            f"registries/sources.json: "
                            f"{type(e).__name__}: {e}")
    return findings


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
    ap.add_argument("--repo", help="repository directory: bind the "
                    "genesis-declared document hashes and inline "
                    "whitelist against its files (s9)")
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
    if args.repo:
        findings.extend(verify_repo_bindings(records, args.repo))

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
