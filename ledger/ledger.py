#!/usr/bin/env python3
"""
Satyakosh ledger engine — RECONSTRUCTED reference implementation.

STATUS: rebuilt 2026-07-15 after loss of the local copy, from SCHEMA.md
1.0.0-rc.1 and the locked decision record. Functionally specified by the
schema; NOT byte-identical to the lost original. The volume test
(volume_test.py) and the mandatory-conditions self-test must be re-run
and their reports regenerated before any Genesis Window claim cites them.

Canonicalization note: RFC 8785 (JCS) reduces, for Satyakosh's data shape,
to: lexicographically sorted keys, minimal escaping, UTF-8, no
insignificant whitespace — because the schema forbids JSON floats
everywhere (the only numbers are small integers), which removes JCS's
number-serialization complexity entirely. json.dumps with sort_keys and
compact separators (ensure_ascii=False) therefore produces JCS-conformant
bytes for all valid Satyakosh records. This equivalence is itself a
Genesis Window review target.
"""

import hashlib
import json
import re
import unicodedata
from pathlib import Path

GENESIS_PREV = "0" * 64
PLACEHOLDER_RE = re.compile(r"<<?PLACEHOLDER|<SK-ENT:|<sha256|YYYY-MM|<UTC|<your|<the ")

VALUE_RE = re.compile(r"^(0|-?[1-9](\.\d+)?e(0|-?[1-9]\d*))$")
ENT_RE = re.compile(r"^SK-ENT-\d{6}$")
PRED_RE = re.compile(r"^SK-PRED-\d{6}$")
SRC_RE = re.compile(r"^SK-SRC-\d{6}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TS_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")

SEALABLE_DERIVATIONS = {
    "si_exact_definition", "defined_convention", "mathematical_proof",
    "laboratory_measurement", "derived_exact",
}


def nfc(obj):
    """Recursively NFC-normalize all strings (SCHEMA s7.2.1)."""
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, list):
        return [nfc(x) for x in obj]
    if isinstance(obj, dict):
        return {nfc(k): nfc(v) for k, v in obj.items()}
    return obj


def jcs(obj) -> bytes:
    """Canonical bytes. See module docstring for the JCS equivalence."""
    return json.dumps(nfc(obj), sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def triple_hash(triple: dict) -> str:
    return sha256_hex(jcs(canonical_triple(triple)))


def canonical_triple(triple: dict) -> dict:
    """Apply content normalization: condition sort + tie-break, s7.2.4."""
    t = dict(triple)
    conds = t.get("conditions", [])
    t["conditions"] = sorted(
        conds, key=lambda c: (c["property"], jcs(c["object"])))
    return t


def content_hash(record: dict) -> str:
    body = {k: v for k, v in record.items()
            if k not in ("content_hash", "prev_record_hash")}
    return sha256_hex(jcs(body))


def chain_link(curr_content_hash: str, prev_link: str) -> str:
    return sha256_hex((curr_content_hash + prev_link).encode("ascii"))


# ---------------------------------------------------------------- validation

class ValidationError(Exception):
    """Raised with a citable reason (SCHEMA s11 / SCOPE / ruleset)."""


def _ascii_guard(record: dict):
    """Fact records must be pure ASCII in canonical form (SCHEMA s7.2.1).
    A non-ASCII byte in a fact record is an attack signature."""
    raw = jcs(record)
    try:
        raw.decode("ascii")
    except UnicodeDecodeError as e:
        raise ValidationError(
            f"SCHEMA s7.2: non-ASCII byte in fact canonical form at "
            f"offset {e.start} — homoglyph/invisible-character tripwire")


def _placeholder_guard(obj, context: str):
    raw = json.dumps(obj, ensure_ascii=False)
    m = PLACEHOLDER_RE.search(raw)
    if m:
        raise ValidationError(
            f"SCHEMA s9: placeholder marker {m.group(0)!r} in {context} — "
            f"refusing to seal")


def validate_fact(record: dict, registries: dict, rulesets: dict):
    """SCHEMA s11 structural + admissibility checks. Raises on violation."""
    for field in ("record_type", "fact_id", "triple_hash", "version",
                  "triple", "ring", "truth_type", "sources", "derivation",
                  "process_hash", "status", "created"):
        if field not in record:
            raise ValidationError(f"SCHEMA s4: missing field {field!r}")
    if record["record_type"] != "fact":
        raise ValidationError("validate_fact called on non-fact record")

    triple = record["triple"]
    if not isinstance(triple, dict):
        raise ValidationError("SCHEMA s3: triple must be an object")
    if not isinstance(triple.get("subject"), str) or \
            not ENT_RE.match(triple["subject"]):
        raise ValidationError("SCHEMA s3.1: malformed or missing subject ID")
    if not isinstance(triple.get("predicate"), str) or \
            not PRED_RE.match(triple["predicate"]):
        raise ValidationError("SCHEMA s3.2: malformed or missing predicate ID")

    ents = {e["id"] for e in registries["entities"]["entities"]}
    preds = {p["id"] for p in registries["predicates"]["predicates"]}
    srcs = {s["id"]: s for s in registries["sources"]["sources"]}
    if triple["subject"] not in ents:
        raise ValidationError("SCHEMA s11: subject not in entity registry")
    if triple["predicate"] not in preds:
        raise ValidationError("SCHEMA s11: predicate not in registry")

    obj = triple.get("object")
    if not isinstance(obj, dict):
        raise ValidationError("SCHEMA s3.3: object must be a typed union object")
    if obj.get("type") != "quantity":
        raise ValidationError(
            "SCHEMA s3.3: v1 gate admits object type 'quantity' only")
    val = obj.get("value")
    if not isinstance(val, str) or not VALUE_RE.match(val):
        raise ValidationError(
            f"SCHEMA s7.3: value {val!r} violates the grammar")
    unc = obj.get("uncertainty")
    if unc is not None and (not isinstance(unc, str)
                            or not VALUE_RE.match(unc)):
        raise ValidationError("SCHEMA s7.3: uncertainty violates grammar")
    if not isinstance(obj.get("exact"), bool):
        raise ValidationError("SCHEMA s3.3: exact must be boolean")
    if not obj.get("unit"):
        raise ValidationError("SCHEMA s3.3: unit required ('1' if dimensionless)")

    conds = triple.get("conditions", [])
    if not isinstance(conds, list):
        raise ValidationError("SCHEMA s3.4: conditions must be an array")
    for c in conds:
        if not isinstance(c, dict) or not isinstance(c.get("property"), str) \
                or not isinstance(c.get("object"), dict):
            raise ValidationError("SCHEMA s3.4: malformed condition entry")
        if not ENT_RE.match(c["property"]):
            raise ValidationError("SCHEMA s3.4: malformed condition property")
        if c["object"].get("type") != "quantity":
            raise ValidationError("SCHEMA s3.3: v1 condition values are quantity only")
    sorted_conds = sorted(conds, key=lambda c: (c["property"], jcs(c["object"])))
    if conds != sorted_conds:
        raise ValidationError("SCHEMA s7.2.4: conditions not in canonical order")

    if not isinstance(record["derivation"], dict) or \
            not isinstance(record["derivation"].get("type"), str):
        raise ValidationError("SCHEMA s4: derivation must carry a type")
    if not isinstance(record["sources"], list) or not all(
            isinstance(s, dict) and isinstance(s.get("source"), str)
            for s in record["sources"]):
        raise ValidationError("SCHEMA s4: malformed sources array")

    # rulesets in force must be placeholder-free before any fact can seal
    # (same guard validate_genesis applies; SCHEMA s9 / s11)
    for name, rs in rulesets.items():
        operative = {k: v for k, v in rs.items() if not k.startswith("_")}
        _placeholder_guard(operative, f"ruleset {name} (operative fields)")

    # mandatory conditions (map in force at chain position; v1: founding map)
    mc = rulesets["mandatory_conditions"]
    required = list(mc["derivation_type_rules"].get(
        record["derivation"]["type"]) or [])
    for rule in mc.get("subject_rules", []):
        if rule["subject"] == triple["subject"]:
            required += rule["requires"]
    present = {c["property"] for c in conds}
    for req in required:
        if req not in present:
            raise ValidationError(
                f"rulesets/mandatory_conditions.json: required condition "
                f"property {req} absent — never enters review")

    # sources: sorted, whitelisted for ring
    src_ids = [s["source"] for s in record["sources"]]
    if src_ids != sorted(src_ids):
        raise ValidationError("SCHEMA s7.2.5: sources not sorted")
    for sid in src_ids:
        if sid not in srcs:
            raise ValidationError(f"SCHEMA s11: source {sid} not whitelisted")
        if record["ring"] not in srcs[sid]["rings"]:
            raise ValidationError(
                f"SCHEMA s11: source {sid} not whitelisted for ring "
                f"{record['ring']}")

    # admissibility map
    dtype = record["derivation"]["type"]
    adm = rulesets["admissibility_map"]["map"].get(dtype)
    if adm is None or adm[f"ring_{record['ring']}"] != "SEAL":
        raise ValidationError(
            f"rules/admissibility_map.json: derivation type {dtype!r} is "
            f"not SEAL for ring {record['ring']}")
    if dtype == "derived_exact" and not record["derivation"].get("derived_from"):
        raise ValidationError(
            "SCHEMA s11: derived_exact requires non-empty derived_from")

    # id/hash cross-checks
    th = triple_hash(triple)
    if record["triple_hash"] != th:
        raise ValidationError("SCHEMA s11: triple_hash mismatch")
    if not isinstance(record["fact_id"], str) or (
            not record["fact_id"].endswith(th[:12]) and
            not record["fact_id"].endswith(th[:16])):
        raise ValidationError("SCHEMA s6: fact_id suffix != triple_hash prefix")
    if not isinstance(record["created"], str) or \
            not TS_RE.match(record["created"]):
        raise ValidationError("SCHEMA s7.2.2: created not UTC timestamp form")

    _ascii_guard(record)


def validate_genesis(record: dict, rulesets: dict):
    """SCHEMA s9. NFC UTF-8 (not ASCII); refuses placeholders anywhere,
    including operative fields of hash-enumerated rulesets."""
    if record.get("record_type") != "genesis":
        raise ValidationError("not a genesis record")
    if record.get("prev_record_hash") != GENESIS_PREV:
        raise ValidationError("SCHEMA s8: genesis prev_record_hash must be 64 zeros")
    _placeholder_guard(record, "genesis record")
    insc = record["inscription"]
    for f in ("mission", "invocation", "invocation_source", "founder",
              "dedication", "founded"):
        if not insc.get(f, "").strip():
            raise ValidationError(f"SCHEMA s9: empty inscription field {f!r}")
    if not DATE_RE.match(insc["founded"]):
        raise ValidationError("SCHEMA s9: founded must be YYYY-MM-DD")
    for hf in ("schema_hash", "pipeline_policy_hash", "scope_hash",
               "admissibility_map_hash", "mandatory_conditions_hash",
               "predicates_founding_hash"):
        if not HASH_RE.match(record.get(hf, "")):
            raise ValidationError(f"SCHEMA s9: {hf} is not a sha256 hex digest")
    if not record.get("whitelist"):
        raise ValidationError("SCHEMA s9: whitelist must be enumerated inline")
    # operative placeholders inside hash-enumerated rulesets
    for name, rs in rulesets.items():
        operative = {k: v for k, v in rs.items() if not k.startswith("_")}
        _placeholder_guard(operative, f"ruleset {name} (operative fields)")


# ---------------------------------------------------------------- ledger

class Ledger:
    def __init__(self, path: Path, registries: dict, rulesets: dict):
        self.path = Path(path)
        self.registries = registries
        self.rulesets = rulesets
        self.records = []
        if self.path.exists():
            self.records = json.loads(self.path.read_text())["records"]

    def seal(self, record: dict) -> dict:
        rt = record.get("record_type")
        if not self.records and rt != "genesis":
            raise ValidationError("SCHEMA s8: record 0 must be genesis")
        if rt == "fact":
            validate_fact(record, self.registries, self.rulesets)
            # duplicate detection is an exact hash lookup (SCHEMA s11):
            # same canonical triple may only re-enter as a supersession
            sup = (record.get("supersedes") or "").split("@")[0]
            for r in self.records:
                if (r.get("record_type") == "fact"
                        and r.get("status") != "superseded"
                        and r.get("triple_hash") == record["triple_hash"]
                        and r.get("fact_id") != sup):
                    raise ValidationError(
                        f"SCHEMA s11: duplicate triple_hash of "
                        f"non-superseded fact {r['fact_id']}")
        elif rt == "genesis":
            if self.records:
                raise ValidationError("genesis must be record zero")
            validate_genesis(record, self.rulesets)
        elif rt in ("governance", "inscription"):
            _placeholder_guard(record, f"{rt} record")
        else:
            raise ValidationError(f"unknown record_type {rt!r}")

        record = dict(record)
        record["prev_record_hash"] = (
            GENESIS_PREV if not self.records
            else self.records[-1]["content_hash"])
        record["content_hash"] = content_hash(record)
        self.records.append(record)
        return record

    def chain_head(self) -> str:
        link = GENESIS_PREV
        for r in self.records:
            link = chain_link(r["content_hash"], link)
        return link

    def verify(self) -> list:
        """Returns list of tamper findings; empty list = chain intact."""
        findings = []
        prev = GENESIS_PREV
        for i, r in enumerate(self.records):
            if r["prev_record_hash"] != prev:
                findings.append(f"record {i}: broken chain link")
            if content_hash(r) != r["content_hash"]:
                fid = r.get("fact_id", r.get("record_type"))
                findings.append(f"TAMPERED: {fid} (record {i})")
            if r.get("record_type") == "fact":
                if triple_hash(r["triple"]) != r["triple_hash"]:
                    findings.append(
                        f"TAMPERED TRIPLE: {r['fact_id']} (record {i})")
            prev = r["content_hash"]
        return findings

    def save(self):
        self.path.write_text(json.dumps(
            {"chain_head": self.chain_head(), "records": self.records},
            indent=2, ensure_ascii=False))


if __name__ == "__main__":
    print("Satyakosh ledger engine (reconstructed reference implementation)")
    print("Run volume_test.py / self-tests before relying on any output.")
