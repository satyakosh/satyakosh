#!/usr/bin/env python3
"""make_conformance_vectors.py — language-agnostic conformance vectors.

Generates conformance/vectors.json: input bytes -> expected canonical
bytes, hashes, chain heads, and intact/not-intact verdicts, so that a
verifier written in ANY language can prove byte-level agreement with
the reference implementation without reading a line of Python. The
chain format is three open standards (JSON, RFC 8785 canonicalization
under the no-floats rule, SHA-256); these vectors are the executable
form of that claim.

Deterministic: fixed timestamps, no randomness — regeneration is
byte-identical, so CI can regenerate and diff (--check) to guarantee
the committed vectors never drift from the reference implementation.

Run:  python3 tools/make_conformance_vectors.py           # (re)write
      python3 tools/make_conformance_vectors.py --check   # CI: diff
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
import ledger as L

OUT = REPO / "conformance" / "vectors.json"
T = "2026-07-20T00:00:00Z"  # fixed timestamp for all vector records


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def jcs_case(name, obj, note=None):
    b = L.jcs(obj)
    c = {"name": name, "input": obj, "jcs_utf8_hex": b.hex(),
         "sha256": L.sha256_hex(b)}
    if note:
        c["note"] = note
    return c


def make_genesis(REG, RS):
    g = load("genesis_record.draft.json")
    for k, v in list(g.items()):
        if isinstance(v, str) and "PLACEHOLDER" in v:
            g[k] = "e" * 64 if k.endswith("_hash") else T
    g["mandatory_conditions_hash"] = L.sha256_hex(
        L.jcs(RS["mandatory_conditions"]))
    g["admissibility_map_hash"] = L.sha256_hex(L.jcs(RS["admissibility_map"]))
    g["predicates_founding_hash"] = L.sha256_hex(L.jcs(REG["predicates"]))
    g["inscription"]["mission"] = "Conformance vector chain."
    return g


def make_fact(value, conds=None, created=T):
    obj = {"type": "quantity", "value": value, "unit": "m/s",
           "exact": True, "uncertainty": None}
    triple = {"subject": "SK-ENT-000001", "predicate": "SK-PRED-000001",
              "object": obj, "conditions": conds or []}
    th = L.triple_hash(triple)
    return {"record_type": "fact", "fact_id": f"SK-R1-PHYS-{th[:12]}",
            "triple_hash": th, "version": 1, "supersedes": None,
            "triple": triple, "ring": 1, "valid_from": None,
            "valid_until": None, "terminality": "none",
            "sources": [{"source": "SK-SRC-000001", "edition": "2022",
                         "retrieved": "2026-07-20"}],
            "derivation": {"type": "si_exact_definition", "script": None,
                           "derived_from": []},
            "process_hash": "a" * 64, "status": "sealed", "created": created}


def main(check=False):
    REG = {k: load(f"registries/{k}.json")
           for k in ("entities", "predicates", "sources")}
    RS = {"mandatory_conditions": load("rulesets/mandatory_conditions.json"),
          "admissibility_map": load("rules/admissibility_map.json")}

    vectors = {
        "conformance_version": "1.0.0",
        "_contract": (
            "An implementation CONFORMS if: (1) for every jcs / "
            "triple_hash / content_hash / chain_link case it reproduces "
            "the expected bytes and digests exactly; (2) for every "
            "chain case it reproduces chain_head and the intact "
            "verdict. Finding MESSAGE TEXT is not part of the contract "
            "— hostile input may surface under different labels across "
            "languages (e.g. a stored JSON float is a citable "
            "canonicalization refusal in Python but may parse "
            "integer-losslessly elsewhere and surface as a hash "
            "mismatch); the intact verdict must agree. Strings are "
            "NFC-normalized before serialization; object keys sort by "
            "Unicode CODE POINT (not UTF-16 code unit); numbers in "
            "canonical form are integers only."),
        "jcs": [], "triple_hash": [], "content_hash": [],
        "chain_link": [], "chains": []}

    # ---------------- jcs: canonical-bytes cases ----------------
    V = vectors["jcs"]
    V.append(jcs_case("empty object", {}))
    V.append(jcs_case("key sorting", {"b": 1, "a": 2, "aa": 3},
                      "lexicographic by code point"))
    V.append(jcs_case("nested + arrays preserve order",
                      {"z": [3, 1, 2], "a": {"y": None, "x": True}}))
    V.append(jcs_case("integers only",
                      {"small": 0, "neg": -7, "big": 999999999},
                      "floats are refused everywhere (s7.1); no vector "
                      "contains one"))
    V.append(jcs_case("string escaping",
                      {"k": "quote\" backslash\\ newline\n tab\t"},
                      "JSON minimal escaping; controls escaped, all "
                      "else literal UTF-8"))
    V.append(jcs_case("non-ASCII passthrough (UTF-8, not \\u)",
                      {"k": "सत्यकोश"},
                      "ensure_ascii=false equivalent: multibyte UTF-8 "
                      "bytes, never \\u escapes"))
    V.append(jcs_case("NFC normalization",
                      {"k": "é"},
                      "input is decomposed e + COMBINING ACUTE; "
                      "canonical bytes are the NFC composed form "
                      "U+00E9 — same bytes as {\"k\":\"é\"}"))
    V.append(jcs_case("NFC composed control", {"k": "é"},
                      "must byte-match the decomposed case above"))
    V.append(jcs_case("unicode key sorting", {"é": 1, "z": 2},
                      "U+00E9 > 'z' by code point: z sorts first"))

    # ---------------- triple_hash ----------------
    q = {"type": "quantity", "value": "1e0", "unit": "1",
         "exact": True, "uncertainty": None}
    q2 = {"type": "quantity", "value": "2e0", "unit": "1",
          "exact": True, "uncertainty": None}
    unsorted_triple = {
        "subject": "SK-ENT-000005", "predicate": "SK-PRED-000001",
        "object": {"type": "quantity", "value": "9.9974e1", "unit": "Cel",
                   "exact": False, "uncertainty": "1e-3"},
        "conditions": [
            {"property": "SK-ENT-000007", "object": q},
            {"property": "SK-ENT-000006", "object": q}]}
    vectors["triple_hash"].append({
        "name": "condition sorting by property",
        "note": ("conditions arrive unsorted; canonical form sorts by "
                 "property, then by the condition object's canonical "
                 "bytes"),
        "triple": unsorted_triple,
        "canonical_jcs_utf8_hex": L.jcs(
            L.canonical_triple(unsorted_triple)).hex(),
        "triple_hash": L.triple_hash(unsorted_triple)})
    tie_triple = {
        "subject": "SK-ENT-000001", "predicate": "SK-PRED-000001",
        "object": q, "conditions": [
            {"property": "SK-ENT-000006", "object": q2},
            {"property": "SK-ENT-000006", "object": q}]}
    vectors["triple_hash"].append({
        "name": "same-property tie-break by object bytes",
        "triple": tie_triple,
        "canonical_jcs_utf8_hex": L.jcs(
            L.canonical_triple(tie_triple)).hex(),
        "triple_hash": L.triple_hash(tie_triple)})

    # ---------------- content_hash ----------------
    fact = make_fact("2.99792458e8")
    vectors["content_hash"].append({
        "name": "fact record (content_hash and prev_record_hash "
                "excluded from the hashed body)",
        "record": fact,
        "content_hash": L.content_hash(fact)})

    # ---------------- chain_link ----------------
    vectors["chain_link"].append({
        "name": "head fold step",
        "note": "link = sha256(ascii(content_hash + prev_link))",
        "content_hash": L.content_hash(fact),
        "prev_link": "0" * 64,
        "link": L.chain_link(L.content_hash(fact), "0" * 64)})

    # ---------------- full chains ----------------
    led = L.Ledger(None, REG, RS)
    led.seal(make_genesis(REG, RS))
    led.seal(make_fact("2.99792458e8"))
    led.seal({"record_type": "governance", "governance_kind":
              "ucum_expansion", "delta": {"add_codes": ["d"]},
              "effective_from": "2026-07-20", "created": T})
    led.seal(make_fact("6.02214076e23"))
    clean = {"chain_head": led.chain_head(),
             "records": json.loads(json.dumps(led.records))}
    vectors["chains"].append({
        "name": "clean chain (genesis + fact + governance + fact)",
        "chain": clean, "expect": {"intact": True, "chain_head":
                                   led.chain_head()}})

    tampered = json.loads(json.dumps(clean))
    tampered["records"][1]["triple"]["object"]["value"] = "9.99e9"
    vectors["chains"].append({
        "name": "tampered triple value",
        "note": ("triple bytes no longer match triple_hash and the "
                 "record bytes no longer match content_hash"),
        "chain": tampered, "expect": {"intact": False}})

    broken = json.loads(json.dumps(clean))
    broken["records"][2]["prev_record_hash"] = "f" * 64
    vectors["chains"].append({
        "name": "broken link",
        "chain": broken, "expect": {"intact": False}})

    lied = json.loads(json.dumps(clean))
    lied["records"][3]["content_hash"] = "b" * 64
    vectors["chains"].append({
        "name": "recomputed-hash lie (stored content_hash replaced)",
        "chain": lied, "expect": {"intact": False}})

    headless = json.loads(json.dumps(clean))
    headless["chain_head"] = "c" * 64
    vectors["chains"].append({
        "name": "stored chain_head mismatch",
        "chain": headless, "expect": {"intact": False}})

    notfirst = {"chain_head": None,
                "records": json.loads(json.dumps(clean["records"][1:2]))}
    vectors["chains"].append({
        "name": "genesis not first",
        "chain": notfirst, "expect": {"intact": False}})

    out = json.dumps(vectors, indent=2, ensure_ascii=False) + "\n"
    if check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != out:
            print("CONFORMANCE VECTORS DRIFTED from the reference "
                  "implementation — regenerate and review:")
            print("  python tools/make_conformance_vectors.py")
            return 1
        print(f"conformance vectors match the reference implementation "
              f"({len(vectors['jcs'])} jcs, "
              f"{len(vectors['triple_hash'])} triple, "
              f"{len(vectors['chains'])} chains)")
        return 0
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(out, encoding="utf-8")
    print(f"wrote {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(check="--check" in sys.argv[1:]))
