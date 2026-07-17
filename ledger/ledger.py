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
number-serialization complexity entirely. jcs() ENFORCES the no-float
rule (a float anywhere is a citable rejection), so json.dumps with
sort_keys and compact separators (ensure_ascii=False) produces
JCS-conformant bytes for all records this module accepts. This
equivalence is cross-checked against an independent RFC 8785
implementation in stress/test_canonical_properties.py and remains a
Genesis Window review target.

Supersession semantics (v1): sealed records are never edited, so a
record's stored `status` is always "sealed". A record X@n is
*effectively* superseded iff a later sealed record carries
`supersedes: "X@n"` — superseded-ness is derived from the chain, never
written back. The duplicate rule ("no duplicate triple_hash among
non-superseded facts", SCHEMA s11) is enforced against that derived
state at seal time and re-checked by verify(full=True).
"""

import hashlib
import json
import os
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
FACT_ID_RE = re.compile(r"^SK-R([1-9]\d*)-([A-Z][A-Z0-9]*)-([0-9a-f]{12}|[0-9a-f]{16})$")
SUPERSEDES_RE = re.compile(
    r"^(SK-R[1-9]\d*-[A-Z][A-Z0-9]*-(?:[0-9a-f]{12}|[0-9a-f]{16}))@([1-9]\d*)$")

TRUTH_TYPES = frozenset({"always", "conditional", "seasonal", "periodic"})

# Exact enumerations of sealed-record fields (SCHEMA s4). Unknown fields
# are refused: any extra key would enter the hashed bytes and become a
# smuggling channel past the language-neutrality and ASCII tripwires.
FACT_FIELDS = frozenset({
    "record_type", "fact_id", "triple_hash", "version", "supersedes",
    "triple", "ring", "truth_type", "valid_from", "valid_until",
    "valid_until_expected", "sources", "derivation", "process_hash",
    "status", "created", "content_hash", "prev_record_hash"})
REQUIRED_FACT_FIELDS = FACT_FIELDS - {"content_hash", "prev_record_hash"}
TRIPLE_FIELDS = frozenset({"subject", "predicate", "object", "conditions"})
QUANTITY_FIELDS = frozenset({"type", "value", "unit", "exact", "uncertainty"})
CONDITION_FIELDS = frozenset({"property", "object"})
SOURCE_FIELDS = frozenset({"source", "edition", "retrieved"})

# v1 UCUM code whitelist (SCHEMA s11). Ring 1's founding scope needs a
# small closed set, matching the whitelist philosophy; UCUM codes are
# case-sensitive and verbatim (s7.2.6). Additions are code changes
# pre-genesis and accompany proposal review after.
UCUM_V1 = frozenset({
    "1", "m", "s", "g", "kg", "A", "K", "mol", "cd", "Hz", "N", "Pa",
    "kPa", "J", "W", "C", "V", "Ohm", "lm", "lx", "Cel", "eV",
    "m/s", "m/s2", "m2", "m3", "J.s", "J/K", "mol-1", "lm/W", "kg/m3"})

SEALABLE_DERIVATIONS = {
    "si_exact_definition", "defined_convention", "mathematical_proof",
    "laboratory_measurement", "derived_exact",
}


class ValidationError(Exception):
    """Raised with a citable reason (SCHEMA s11 / SCOPE / ruleset)."""


def nfc(obj):
    """Recursively NFC-normalize all strings (SCHEMA s7.2.1)."""
    if isinstance(obj, str):
        return unicodedata.normalize("NFC", obj)
    if isinstance(obj, list):
        return [nfc(x) for x in obj]
    if isinstance(obj, dict):
        return {nfc(k): nfc(v) for k, v in obj.items()}
    return obj


def _reject_floats(obj, path="$"):
    """SCHEMA s7.1: no JSON floats exist anywhere in sealed records.
    Enforced at serialization so a float can never reach the hash — a
    float serializes differently across JCS implementations (json.dumps
    '1.0' vs RFC 8785 '1') and would silently fork the chain."""
    if isinstance(obj, float):
        raise ValidationError(
            f"SCHEMA s7.1: JSON float at {path} — floats are forbidden "
            f"in canonical form (use the s7.3 string grammar)")
    if isinstance(obj, list):
        for i, v in enumerate(obj):
            _reject_floats(v, f"{path}[{i}]")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _reject_floats(v, f"{path}.{k}")


def jcs(obj) -> bytes:
    """Canonical bytes. See module docstring for the JCS equivalence."""
    _reject_floats(obj)
    try:
        return json.dumps(nfc(obj), sort_keys=True, separators=(",", ":"),
                          ensure_ascii=False).encode("utf-8")
    except UnicodeEncodeError:
        raise ValidationError(
            "SCHEMA s7.2: invalid Unicode (lone surrogate) in canonical "
            "form — refusing to serialize")


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

def _ascii_guard(record: dict):
    """Fact records must be pure ASCII in canonical form (SCHEMA s7.2.1).
    A non-ASCII byte in a fact record is an attack signature. Kept as a
    backstop behind the per-field checks: it catches anything a future
    field or free-text slot (e.g. source edition) lets through."""
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


def _require_int(value, name, minimum=1):
    if not isinstance(value, int) or isinstance(value, bool) or \
            value < minimum:
        raise ValidationError(
            f"SCHEMA s4: {name} must be an integer >= {minimum}, "
            f"got {value!r}")


def _validate_quantity(obj, where):
    """Shared s3.3 validation for the object and every condition value —
    conditions use the same typed union (s3.4)."""
    if not isinstance(obj, dict):
        raise ValidationError(
            f"SCHEMA s3.3: {where} must be a typed union object")
    unknown = set(obj) - QUANTITY_FIELDS
    if unknown:
        raise ValidationError(
            f"SCHEMA s3.3: unknown field(s) {sorted(unknown)} in {where}")
    missing = QUANTITY_FIELDS - set(obj)
    if missing:
        raise ValidationError(
            f"SCHEMA s3.3: missing field(s) {sorted(missing)} in {where}")
    if obj["type"] != "quantity":
        raise ValidationError(
            f"SCHEMA s3.3: v1 gate admits type 'quantity' only ({where})")
    val = obj["value"]
    if not isinstance(val, str) or not VALUE_RE.match(val):
        raise ValidationError(
            f"SCHEMA s7.3: {where} value {val!r} violates the grammar")
    unit = obj["unit"]
    if not isinstance(unit, str) or not unit:
        raise ValidationError(
            f"SCHEMA s3.3: {where} unit required ('1' if dimensionless)")
    if unit not in UCUM_V1:
        raise ValidationError(
            f"SCHEMA s11: {where} unit {unit!r} is not in the v1 UCUM "
            f"code whitelist")
    if not isinstance(obj["exact"], bool):
        raise ValidationError(f"SCHEMA s3.3: {where} exact must be boolean")
    unc = obj["uncertainty"]
    if unc is not None:
        if not isinstance(unc, str) or not VALUE_RE.match(unc):
            raise ValidationError(
                f"SCHEMA s7.3: {where} uncertainty violates the grammar")
        if unc.startswith("-"):
            raise ValidationError(
                f"SCHEMA s3.3: {where} uncertainty must be non-negative")
        if obj["exact"]:
            raise ValidationError(
                f"SCHEMA s3.3: {where} is exact — an exact quantity "
                f"cannot carry uncertainty")


def validate_fact(record: dict, registries: dict, rulesets: dict):
    """SCHEMA s11 structural + admissibility checks. Raises on violation.
    Chain-dependent rules (duplicates, supersession linkage,
    derived_from existence) live in Ledger.seal."""
    if record.get("record_type") != "fact":
        raise ValidationError("validate_fact called on non-fact record")
    unknown = set(record) - FACT_FIELDS
    if unknown:
        raise ValidationError(
            f"SCHEMA s4: unknown field(s) {sorted(unknown)} in fact record")
    missing = REQUIRED_FACT_FIELDS - set(record)
    if missing:
        raise ValidationError(
            f"SCHEMA s4: missing field(s) {sorted(missing)}")

    # scalar fields
    _require_int(record["version"], "version")
    _require_int(record["ring"], "ring")
    if record["status"] != "sealed":
        raise ValidationError(
            "SCHEMA s4: status must be 'sealed' at seal time — "
            "superseded-ness is expressed by a later superseding record, "
            "never written into a sealed record")
    if not isinstance(record["truth_type"], str) or \
            record["truth_type"] not in TRUTH_TYPES:
        raise ValidationError(
            f"SCHEMA s4: truth_type {record['truth_type']!r} not in "
            f"{sorted(TRUTH_TYPES)}")
    for f in ("valid_from", "valid_until"):
        v = record[f]
        if v is not None and (not isinstance(v, str) or not DATE_RE.match(v)):
            raise ValidationError(f"SCHEMA s7.2.2: {f} must be null or "
                                  f"YYYY-MM-DD, got {v!r}")
    if record["valid_from"] and record["valid_until"] and \
            record["valid_from"] > record["valid_until"]:
        raise ValidationError("SCHEMA s4: valid_from is after valid_until")
    if not isinstance(record["valid_until_expected"], bool):
        raise ValidationError("SCHEMA s4: valid_until_expected must be boolean")
    sup = record["supersedes"]
    if sup is not None and (not isinstance(sup, str)
                            or not SUPERSEDES_RE.match(sup)):
        raise ValidationError(
            f"SCHEMA s6: supersedes must be null or 'fact_id@version', "
            f"got {sup!r}")
    ph = record["process_hash"]
    if not isinstance(ph, str) or not HASH_RE.match(ph):
        raise ValidationError(
            "SCHEMA s7.2.3: process_hash must be 64 lowercase hex chars")
    if not isinstance(record["created"], str) or \
            not TS_RE.match(record["created"]):
        raise ValidationError("SCHEMA s7.2.2: created not UTC timestamp form")

    # triple
    triple = record["triple"]
    if not isinstance(triple, dict):
        raise ValidationError("SCHEMA s3: triple must be an object")
    if set(triple) != TRIPLE_FIELDS:
        raise ValidationError(
            f"SCHEMA s3: triple must have exactly the fields "
            f"{sorted(TRIPLE_FIELDS)}")
    if not isinstance(triple["subject"], str) or \
            not ENT_RE.match(triple["subject"]):
        raise ValidationError("SCHEMA s3.1: malformed or missing subject ID")
    if not isinstance(triple["predicate"], str) or \
            not PRED_RE.match(triple["predicate"]):
        raise ValidationError("SCHEMA s3.2: malformed or missing predicate ID")

    ents = {e["id"] for e in registries["entities"]["entities"]}
    preds = {p["id"] for p in registries["predicates"]["predicates"]}
    srcs = {s["id"]: s for s in registries["sources"]["sources"]}
    if triple["subject"] not in ents:
        raise ValidationError("SCHEMA s11: subject not in entity registry")
    if triple["predicate"] not in preds:
        raise ValidationError("SCHEMA s11: predicate not in registry")

    _validate_quantity(triple["object"], "object")

    conds = triple["conditions"]
    if not isinstance(conds, list):
        raise ValidationError("SCHEMA s3.4: conditions must be an array")
    for c in conds:
        if not isinstance(c, dict) or set(c) != CONDITION_FIELDS:
            raise ValidationError("SCHEMA s3.4: malformed condition entry")
        if not isinstance(c["property"], str) or not ENT_RE.match(c["property"]):
            raise ValidationError("SCHEMA s3.4: malformed condition property")
        if c["property"] not in ents:
            raise ValidationError(
                f"SCHEMA s11: condition property {c['property']} not in "
                f"entity registry")
        _validate_quantity(c["object"], f"condition {c['property']} value")
    sorted_conds = sorted(conds, key=lambda c: (c["property"], jcs(c["object"])))
    if conds != sorted_conds:
        raise ValidationError("SCHEMA s7.2.4: conditions not in canonical order")

    if not isinstance(record["derivation"], dict) or \
            not isinstance(record["derivation"].get("type"), str):
        raise ValidationError("SCHEMA s4: derivation must carry a type")

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

    # sources: non-empty, complete, sorted, whitelisted for ring
    sources = record["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValidationError(
            "SCHEMA s4: sources must be a non-empty array — a fact "
            "without sources cannot show its working (MISSION principle 2)")
    for s in sources:
        if not isinstance(s, dict) or set(s) != SOURCE_FIELDS:
            raise ValidationError(
                f"SCHEMA s4: each source needs exactly the fields "
                f"{sorted(SOURCE_FIELDS)}")
        if not isinstance(s["source"], str) or not SRC_RE.match(s["source"]):
            raise ValidationError("SCHEMA s4: malformed source ID")
        if not isinstance(s["edition"], str) or not s["edition"].strip():
            raise ValidationError("SCHEMA s4: source edition required")
        if not isinstance(s["retrieved"], str) or \
                not DATE_RE.match(s["retrieved"]):
            raise ValidationError(
                "SCHEMA s7.2.2: source retrieved must be YYYY-MM-DD")
    src_ids = [s["source"] for s in sources]
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
    verdict = adm.get(f"ring_{record['ring']}") if adm else None
    if verdict != "SEAL":
        raise ValidationError(
            f"rules/admissibility_map.json: derivation type {dtype!r} is "
            f"not SEAL for ring {record['ring']}")
    df = record["derivation"].get("derived_from")
    if df is not None and (not isinstance(df, list) or
                           not all(isinstance(x, str) for x in df)):
        raise ValidationError(
            "SCHEMA s4: derived_from must be an array of fact IDs")
    if dtype == "derived_exact" and not df:
        raise ValidationError(
            "SCHEMA s11: derived_exact requires non-empty derived_from")

    # id/hash cross-checks
    th = triple_hash(triple)
    if record["triple_hash"] != th:
        raise ValidationError("SCHEMA s11: triple_hash mismatch")
    fid = record["fact_id"]
    m = FACT_ID_RE.match(fid) if isinstance(fid, str) else None
    if not m:
        raise ValidationError(
            f"SCHEMA s6: fact_id {fid!r} does not match "
            f"SK-R<ring>-<DOMAIN>-<12|16 hex>")
    if int(m.group(1)) != record["ring"]:
        raise ValidationError(
            f"SCHEMA s6: fact_id ring segment R{m.group(1)} != record "
            f"ring {record['ring']}")
    if not th.startswith(m.group(3)):
        raise ValidationError("SCHEMA s6: fact_id suffix != triple_hash prefix")

    _ascii_guard(record)


GENESIS_FIELDS = frozenset({
    "record_type", "inscription", "schema_version", "schema_hash",
    "pipeline_policy_version", "pipeline_policy_hash", "scope_hash",
    "admissibility_map_hash", "mandatory_conditions_hash",
    "predicates_founding_hash", "whitelist", "created",
    "content_hash", "prev_record_hash"})
INSCRIPTION_FIELDS = frozenset({
    "mission", "invocation", "invocation_source", "founder",
    "dedication", "founded"})


def validate_genesis(record: dict, rulesets: dict):
    """SCHEMA s9. NFC UTF-8 (not ASCII); refuses placeholders anywhere,
    including operative fields of hash-enumerated rulesets."""
    if record.get("record_type") != "genesis":
        raise ValidationError("not a genesis record")
    if record.get("prev_record_hash") != GENESIS_PREV:
        raise ValidationError("SCHEMA s8: genesis prev_record_hash must be 64 zeros")
    unknown = set(record) - GENESIS_FIELDS
    if unknown:
        raise ValidationError(
            f"SCHEMA s9: unknown field(s) {sorted(unknown)} in genesis record")
    missing = GENESIS_FIELDS - {"content_hash"} - set(record)
    if missing:
        raise ValidationError(f"SCHEMA s9: missing field(s) {sorted(missing)}")
    _placeholder_guard(record, "genesis record")
    insc = record["inscription"]
    if not isinstance(insc, dict) or set(insc) != INSCRIPTION_FIELDS:
        raise ValidationError(
            f"SCHEMA s9: inscription must have exactly the fields "
            f"{sorted(INSCRIPTION_FIELDS)}")
    for f in sorted(INSCRIPTION_FIELDS):
        if not isinstance(insc.get(f), str) or not insc[f].strip():
            raise ValidationError(f"SCHEMA s9: empty inscription field {f!r}")
    if not DATE_RE.match(insc["founded"]):
        raise ValidationError("SCHEMA s9: founded must be YYYY-MM-DD")
    if not isinstance(record["created"], str) or \
            not TS_RE.match(record["created"]):
        raise ValidationError("SCHEMA s7.2.2: genesis created not UTC "
                              "timestamp form")
    for hf in ("schema_hash", "pipeline_policy_hash", "scope_hash",
               "admissibility_map_hash", "mandatory_conditions_hash",
               "predicates_founding_hash"):
        if not isinstance(record.get(hf), str) or not HASH_RE.match(record[hf]):
            raise ValidationError(f"SCHEMA s9: {hf} is not a sha256 hex digest")
    if not record.get("whitelist"):
        raise ValidationError("SCHEMA s9: whitelist must be enumerated inline")
    # operative placeholders inside hash-enumerated rulesets
    for name, rs in rulesets.items():
        operative = {k: v for k, v in rs.items() if not k.startswith("_")}
        _placeholder_guard(operative, f"ruleset {name} (operative fields)")


# ---------------------------------------------------------------- ledger

class Ledger:
    def __init__(self, path, registries: dict, rulesets: dict):
        self.path = Path(path) if path is not None else None
        self.registries = registries
        self.rulesets = rulesets
        self.records = []
        self.flags = []  # near-duplicate warnings (s11: warn, not a byte rule)
        self._init_indexes()
        if self.path is not None and self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.records = data["records"]
            for r in self.records:
                self._index(r)
            stored = data.get("chain_head")
            if stored is not None and stored != self.chain_head():
                raise ValidationError(
                    "ledger file chain_head does not match the recomputed "
                    "chain head — file corrupt or tampered")

    def _init_indexes(self):
        self._by_id = {}        # fact_id -> {version: record}
        self._by_triple = {}    # triple_hash -> [record, ...]
        self._superseded = set()  # {"fact_id@version", ...} named as targets
        self._np_units = {}     # near-dup key -> {unit, ...}

    def _np_key(self, triple):
        ct = canonical_triple(triple)
        return sha256_hex(jcs([ct["subject"], ct["predicate"],
                               ct["conditions"]]))

    def _index(self, r):
        if r.get("record_type") != "fact":
            return
        self._by_id.setdefault(r["fact_id"], {})[r["version"]] = r
        self._by_triple.setdefault(r["triple_hash"], []).append(r)
        if isinstance(r.get("supersedes"), str):
            self._superseded.add(r["supersedes"])
        self._np_units.setdefault(self._np_key(r["triple"]), set()).add(
            r["triple"]["object"]["unit"])

    def _check_chain_rules(self, record):
        """Chain-position rules: (fact_id, version) uniqueness, the
        supersession transaction (SCHEMA s6), the duplicate rule against
        derived live status (s11), derived_from existence, and the
        near-duplicate flag."""
        fid, ver, th = record["fact_id"], record["version"], record["triple_hash"]
        if ver in self._by_id.get(fid, {}):
            raise ValidationError(f"SCHEMA s6: {fid}@{ver} is already sealed")

        sup, target = record["supersedes"], None
        if sup is not None:
            tfid, tver = sup.rsplit("@", 1)
            tver = int(tver)
            versions = self._by_id.get(tfid)
            if not versions or tver not in versions:
                raise ValidationError(
                    f"SCHEMA s6: supersedes target {sup} is not on the chain")
            if tver != max(versions):
                raise ValidationError(
                    f"SCHEMA s6: only the latest version of {tfid} "
                    f"(@{max(versions)}) can be superseded")
            if sup in self._superseded:
                raise ValidationError(
                    f"SCHEMA s6: {sup} is already superseded")
            target = versions[tver]
            if th == target["triple_hash"]:
                # metadata-only supersession: same identity, next version
                if fid != tfid or ver != tver + 1:
                    raise ValidationError(
                        "SCHEMA s6: metadata supersession must keep the "
                        "fact_id and increment version by exactly 1")
            else:
                # triple-changing supersession: new identity, fresh version
                if fid == tfid:
                    raise ValidationError(
                        "SCHEMA s6: a changed triple yields a new "
                        "triple_hash and hence a new fact_id")
                if ver != 1:
                    raise ValidationError(
                        "SCHEMA s6: a new-triple fact starts at version 1")
        elif ver != 1:
            raise ValidationError(
                "SCHEMA s6: a fact without supersedes starts at version 1")

        # duplicate detection against derived live status
        for r in self._by_triple.get(th, []):
            if f"{r['fact_id']}@{r['version']}" in self._superseded:
                continue
            if target is not None and r is target:
                continue
            raise ValidationError(
                f"SCHEMA s11: duplicate triple_hash of non-superseded "
                f"fact {r['fact_id']}@{r['version']}")

        # derived_from must reference sealed facts
        for x in record["derivation"].get("derived_from") or []:
            if x not in self._by_id:
                raise ValidationError(
                    f"SCHEMA s11: derived_from references unknown fact {x}")

        # near-duplicate flag (s11: same subject+predicate+conditions,
        # different unit -> human review; a warning, never a refusal)
        other_units = self._np_units.get(self._np_key(record["triple"]),
                                         set()) - {record["triple"]["object"]["unit"]}
        if other_units:
            self.flags.append(
                f"near-duplicate flag: {fid} shares subject+predicate+"
                f"conditions with sealed fact(s) in unit(s) "
                f"{sorted(other_units)} — possible unit-converted duplicate")

    def seal(self, record: dict) -> dict:
        rt = record.get("record_type")
        if not self.records and rt != "genesis":
            raise ValidationError("SCHEMA s8: record 0 must be genesis")
        if rt == "fact":
            validate_fact(record, self.registries, self.rulesets)
            self._check_chain_rules(record)
        elif rt == "genesis":
            if self.records:
                raise ValidationError("genesis must be record zero")
            validate_genesis(record, self.rulesets)
        elif rt in ("governance", "inscription"):
            # NOTE: the governance engine (payload validation + chain-
            # position ruleset resolution, SCHEMA s10/P9) is not yet
            # implemented; it must exist before the first governance
            # record seals. Tracked in GENESIS_AMENDMENTS.md.
            _placeholder_guard(record, f"{rt} record")
        else:
            raise ValidationError(f"unknown record_type {rt!r}")

        record = dict(record)
        record["prev_record_hash"] = (
            GENESIS_PREV if not self.records
            else self.records[-1]["content_hash"])
        record["content_hash"] = content_hash(record)
        self.records.append(record)
        self._index(record)
        return record

    def chain_head(self) -> str:
        link = GENESIS_PREV
        for r in self.records:
            link = chain_link(r["content_hash"], link)
        return link

    def verify(self, full: bool = False) -> list:
        """Returns a list of findings; empty list = chain intact.

        Default mode is tamper-evidence: hash links and content hashes.
        full=True additionally replays every record through seal-time
        validation (fraud-evidence): field validity, duplicate rule
        against derived status, supersession linkage, genesis-first."""
        findings = []
        prev = GENESIS_PREV
        for i, r in enumerate(self.records):
            if r.get("prev_record_hash") != prev:
                findings.append(f"record {i}: broken chain link")
            if content_hash(r) != r.get("content_hash"):
                fid = r.get("fact_id", r.get("record_type"))
                findings.append(f"TAMPERED: {fid} (record {i})")
            if r.get("record_type") == "fact":
                if triple_hash(r["triple"]) != r["triple_hash"]:
                    findings.append(
                        f"TAMPERED TRIPLE: {r['fact_id']} (record {i})")
            prev = r.get("content_hash")

        if full:
            shadow = Ledger(None, self.registries, self.rulesets)
            for i, r in enumerate(self.records):
                body = {k: v for k, v in r.items() if k != "content_hash"}
                try:
                    shadow.seal(dict(body))
                except ValidationError as e:
                    findings.append(
                        f"INVALID record {i} "
                        f"({r.get('fact_id', r.get('record_type'))}): {e}")
                    # keep the replay coherent so later records can still
                    # resolve supersedes/derived_from targets
                    shadow.records.append(dict(r))
                    shadow._index(r)
        return findings

    def save(self):
        # explicit UTF-8 (platform defaults like cp1252 corrupt the
        # genesis record's NFC UTF-8) and atomic replace (a crash
        # mid-write must never corrupt the canonical store)
        payload = json.dumps(
            {"chain_head": self.chain_head(), "records": self.records},
            indent=2, ensure_ascii=False)
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        tmp.write_text(payload, encoding="utf-8")
        os.replace(tmp, self.path)


if __name__ == "__main__":
    print("Satyakosh ledger engine (reconstructed reference implementation)")
    print("Run volume_test.py / self-tests before relying on any output.")
