#!/usr/bin/env python3
"""
Satyakosh ledger engine — RECONSTRUCTED reference implementation.

STATUS: rebuilt 2026-07-15 after loss of the local copy, from SCHEMA.md
1.0.0-rc.1 and the locked decision record. Functionally specified by the
schema; NOT byte-identical to the lost original. The volume test
(stress/volume_test.py) and the mandatory-conditions self-test were
re-run on this reconstruction and their reports regenerated
(2026-07-16); both run in CI on every push, alongside the genesis seal
rehearsal, the Ring-2 expressiveness battery, and two fuzzers.

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
# UCUM code syntax: the ASCII characters UCUM's grammar can produce
# (case-sensitive codes, annotations in {}, powers, solidus). Anything
# else — angle brackets, spaces, control characters — is not a unit
# (issue #7 G5: '<<TBD>>' must never become an in-force code).
UCUM_CHAR_RE = re.compile(r"^[0-9A-Za-z%\[\]{}./*^()'_-]$")
FACT_ID_RE = re.compile(r"^SK-R([1-9]\d*)-([A-Z][A-Z0-9]*)-([0-9a-f]{12}|[0-9a-f]{16})$")
SUPERSEDES_RE = re.compile(
    r"^(SK-R[1-9]\d*-[A-Z][A-Z0-9]*-(?:[0-9a-f]{12}|[0-9a-f]{16}))@([1-9]\d*)$")

TERMINALITY = frozenset({"none", "expected", "scheduled"})

# Exact enumerations of sealed-record fields (SCHEMA s4, per the
# recovered original: truth_type was removed by the July 2026 taxonomy
# review; terminality replaces the boolean). Unknown fields are refused:
# any extra key would enter the hashed bytes and become a smuggling
# channel past the language-neutrality and ASCII tripwires.
FACT_FIELDS = frozenset({
    "record_type", "fact_id", "triple_hash", "version", "supersedes",
    "triple", "ring", "valid_from", "valid_until", "terminality",
    "sources", "derivation", "process_hash",
    "status", "created", "content_hash", "prev_record_hash"})
REQUIRED_FACT_FIELDS = FACT_FIELDS - {"content_hash", "prev_record_hash"}
TRIPLE_FIELDS = frozenset({"subject", "predicate", "object", "conditions"})
QUANTITY_FIELDS = frozenset({"type", "value", "unit", "exact", "uncertainty"})
CONDITION_FIELDS = frozenset({"property", "object"})
SOURCE_FIELDS = frozenset({"source", "edition", "retrieved"})
DERIVATION_FIELDS = frozenset({"type", "script", "derived_from"})

# v1 UCUM code whitelist (SCHEMA s11). Ring 1's founding scope needs a
# small closed set, matching the whitelist philosophy; UCUM codes are
# case-sensitive and verbatim (s7.2.6). Additions are code changes
# pre-genesis and accompany proposal review after.
UCUM_V1 = frozenset({
    "1", "m", "s", "g", "kg", "A", "K", "mol", "cd", "Hz", "N", "Pa",
    "kPa", "J", "W", "C", "V", "Ohm", "lm", "lx", "Cel", "eV",
    "m/s", "m/s2", "m2", "m3", "J.s", "J/K", "mol-1", "lm/W", "kg/m3"})
    # Closed by default (FD-29): exactly the founding-scope codes — no
    # Ring-1 seed uses %, a, or other Ring-2-corpus units, and they are
    # inert for v1 (Ring 2 is sealed out). UCUM_V1 is not a genesis-hashed
    # artifact, so codes are added at Ring-2 activation by governance
    # record. Ring-2 stress harnesses extend this set locally.

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

def _ascii_guard(record: dict, exempt=frozenset()):
    """Fact records must be pure ASCII in canonical form (SCHEMA s7.2.1).
    A non-ASCII byte in a fact record is an attack signature. Kept as a
    backstop behind the per-field checks: it catches anything a future
    field or free-text slot (e.g. source edition) lets through.
    `exempt`: characters legitimized by ascii_exemption governance
    records (the s7.2 tripwire-narrowing mechanism)."""
    raw = jcs(record)
    text = raw.decode("utf-8")
    for ch in text:
        if ord(ch) > 127 and ch not in exempt:
            raise ValidationError(
                f"SCHEMA s7.2: non-ASCII character U+{ord(ch):04X} in "
                f"fact canonical form — homoglyph/invisible-character "
                f"tripwire (not exempted by any governance record)")


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


def _validate_quantity(obj, where, ucum=None):
    """Shared s3.3 validation for the object and every condition value —
    conditions use the same typed union (s3.4). `ucum` is the whitelist
    in force at this chain position (defaults to the founding set)."""
    if ucum is None:
        ucum = UCUM_V1
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
    if unit not in ucum:
        raise ValidationError(
            f"SCHEMA s11: {where} unit {unit!r} is not in the UCUM "
            f"code whitelist in force")
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


def validate_fact(record: dict, registries: dict, rulesets: dict, *,
                  whitelist=None, ucum=None, ascii_exempt=frozenset()):
    """SCHEMA s11 structural + admissibility checks. Raises on violation.
    Chain-dependent rules (duplicates, supersession linkage,
    derived_from existence) live in Ledger.seal. The keyword arguments
    carry the rules IN FORCE at this chain position (genesis state plus
    preceding governance records, SCHEMA s10/P9); defaults are the
    founding state."""
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
            "SCHEMA s4: status must be 'sealed' at seal time — later "
            "states (superseded, retired) are expressed by later records, "
            "never written into a sealed record")
    if not isinstance(record["terminality"], str) or \
            record["terminality"] not in TERMINALITY:
        raise ValidationError(
            f"SCHEMA s4: terminality {record['terminality']!r} not in "
            f"{sorted(TERMINALITY)}")
    for f in ("valid_from", "valid_until"):
        v = record[f]
        if v is not None and (not isinstance(v, str) or not DATE_RE.match(v)):
            raise ValidationError(f"SCHEMA s7.2.2: {f} must be null or "
                                  f"YYYY-MM-DD, got {v!r}")
    if record["valid_from"] and record["valid_until"] and \
            record["valid_from"] > record["valid_until"]:
        raise ValidationError("SCHEMA s4: valid_from is after valid_until")
    # s4 semantics: 'scheduled' means dated expiry — the two travel together
    if (record["terminality"] == "scheduled") != \
            (record["valid_until"] is not None):
        raise ValidationError(
            "SCHEMA s4: terminality 'scheduled' requires valid_until, and "
            "a dated valid_until requires terminality 'scheduled'")
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
    preds = {p["id"]: p for p in registries["predicates"]["predicates"]}
    srcs = whitelist if whitelist is not None else \
        {s["id"]: s for s in registries["sources"]["sources"]}
    if triple["subject"] not in ents:
        raise ValidationError("SCHEMA s11: subject not in entity registry")
    if triple["predicate"] not in preds:
        raise ValidationError("SCHEMA s11: predicate not in registry")

    _validate_quantity(triple["object"], "object", ucum=ucum)

    # the predicate registry's object_types declaration is load-bearing
    # (s3.2): a predicate admitting only dates must never seal a quantity
    allowed_types = preds[triple["predicate"]].get("object_types")
    if allowed_types is not None and \
            triple["object"].get("type") not in allowed_types:
        raise ValidationError(
            f"registry: predicate {triple['predicate']} admits object "
            f"types {allowed_types}, got {triple['object'].get('type')!r}")

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
        _validate_quantity(c["object"], f"condition {c['property']} value",
                           ucum=ucum)
    sorted_conds = sorted(conds, key=lambda c: (c["property"], jcs(c["object"])))
    if conds != sorted_conds:
        raise ValidationError("SCHEMA s7.2.4: conditions not in canonical order")

    deriv = record["derivation"]
    if not isinstance(deriv, dict) or set(deriv) != DERIVATION_FIELDS or \
            not isinstance(deriv["type"], str):
        raise ValidationError(
            f"SCHEMA s4.1: derivation must have exactly the fields "
            f"{sorted(DERIVATION_FIELDS)} with a string type")
    if deriv["script"] is not None and (
            not isinstance(deriv["script"], str)
            or not HASH_RE.match(deriv["script"])):
        raise ValidationError(
            "SCHEMA s4.1: derivation.script must be null or the sha256 "
            "of the recipe at derivations/<triple_hash>.py")

    # rulesets in force must be placeholder-free before any fact can seal
    # (same guard validate_genesis applies; SCHEMA s9 / s11)
    for name, rs in rulesets.items():
        operative = {k: v for k, v in rs.items() if not k.startswith("_")}
        _placeholder_guard(operative, f"ruleset {name} (operative fields)")

    # mandatory conditions (map in force at chain position; v1: founding
    # map). Backstop behind the governance-seal structural check (issue
    # #7 G2): a structurally broken ruleset in force is a citable
    # refusal, never a KeyError escaping the seal-path error contract.
    mc = rulesets.get("mandatory_conditions")
    am = rulesets.get("admissibility_map")
    try:
        if mc is not None:
            _validate_ruleset_structure("mandatory_conditions", mc)
        if am is not None:
            _validate_ruleset_structure("admissibility_map", am)
    except ValidationError as e:
        raise ValidationError(
            f"ruleset in force is structurally invalid — governance "
            f"defect, no fact can seal until a corrective ruleset_change "
            f"seals: {e}")
    if mc is None or am is None:
        raise ValidationError(
            "rulesets in force must include mandatory_conditions and "
            "admissibility_map")
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
    # a source listed twice is meaningless (and, pre-Ring-2, a way to
    # inflate any future source count) — refuse duplicate entries (v1
    # hardening; issue #6)
    if len(set(src_ids)) != len(src_ids):
        raise ValidationError("SCHEMA s7.2.5: duplicate source entries")
    # per-derivation-type minimum DISTINCT-INSTITUTION counts: dormant
    # capability the Ring-2 activation record sets values for (issue #5
    # F3). RING2 s3.1 requires INDEPENDENT sources, so the count is over
    # distinct source IDs, never entries (issue #6). v1 founding ruleset
    # declares none, so the default of 1 applies.
    min_src = mc.get("source_count_rules", {}).get(
        record["derivation"]["type"], 1)
    if len(set(src_ids)) < min_src:
        raise ValidationError(
            f"rulesets/mandatory_conditions.json: derivation type "
            f"{record['derivation']['type']!r} requires >= {min_src} "
            f"distinct whitelisted sources, got {len(set(src_ids))}")
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
    df = record["derivation"]["derived_from"]
    if not isinstance(df, list) or not all(isinstance(x, str) for x in df):
        raise ValidationError(
            "SCHEMA s4.1: derived_from must be an array of fact IDs")
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

    _ascii_guard(record, exempt=ascii_exempt)


GENESIS_FIELDS = frozenset({
    "record_type", "inscription", "schema_version", "schema_hash",
    "pipeline_policy_version", "pipeline_policy_hash", "scope_hash",
    "admissibility_map_hash", "mandatory_conditions_hash",
    "predicates_founding_hash", "whitelist", "created",
    "content_hash", "prev_record_hash"})
INSCRIPTION_FIELDS = frozenset({
    "mission", "invocation", "invocation_source", "founder",
    "dedication", "founded"})


def validate_genesis(record: dict, rulesets: dict, registries: dict = None,
                     sources_file_agreement: bool = True):
    """SCHEMA s9. NFC UTF-8 (not ASCII); refuses placeholders anywhere,
    including operative fields of hash-enumerated rulesets.

    The genesis-declared artifact hashes BIND (issue #7 G3): the
    provided rulesets (and, when registries are given, the predicates
    registry) are hashed per the s9 doctrine — JSON hashes as JCS — and
    a mismatch refuses. The declared digests are enumeration, not
    decoration: a chain sealed under rulesets that do not match its own
    genesis is refused at seal and condemned by verify(full).

    The inline whitelist is authoritative (issue #7 G4): entries are
    structurally validated here, and when registries are given the
    sources file must agree with the inline enumeration on
    {id, publisher, rings} — a source present only in the file must
    never seal, because a verifier reconstructing from the chain alone
    would refuse it."""
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
    # founded is inscription prose (dual-calendar, FD-27) but must carry
    # exactly one Gregorian ISO date as the machine-readable anchor —
    # external corroboration (trademark priority) keys on it
    if len(re.findall(r"\d{4}-\d{2}-\d{2}", insc["founded"])) != 1:
        raise ValidationError(
            "SCHEMA s9: founded must contain exactly one Gregorian ISO "
            "date (YYYY-MM-DD) as the machine anchor")
    if not isinstance(record["created"], str) or \
            not TS_RE.match(record["created"]):
        raise ValidationError("SCHEMA s7.2.2: genesis created not UTC "
                              "timestamp form")
    for hf in ("schema_hash", "pipeline_policy_hash", "scope_hash",
               "admissibility_map_hash", "mandatory_conditions_hash",
               "predicates_founding_hash"):
        if not isinstance(record.get(hf), str) or not HASH_RE.match(record[hf]):
            raise ValidationError(f"SCHEMA s9: {hf} is not a sha256 hex digest")
    wl = record.get("whitelist")
    if not wl:
        raise ValidationError("SCHEMA s9: whitelist must be enumerated inline")
    if not isinstance(wl, list):
        raise ValidationError("SCHEMA s9: whitelist must be an array")
    seen_ids = set()
    for e in wl:
        if not isinstance(e, dict) or set(e) != {"id", "publisher", "rings"}:
            raise ValidationError(
                "SCHEMA s9: whitelist entries need exactly "
                "{id, publisher, rings}")
        if not isinstance(e["id"], str) or not SRC_RE.match(e["id"]):
            raise ValidationError(
                f"SCHEMA s9: malformed whitelist source ID {e['id']!r}")
        if e["id"] in seen_ids:
            raise ValidationError(
                f"SCHEMA s9: duplicate whitelist entry {e['id']}")
        seen_ids.add(e["id"])
        if not isinstance(e["publisher"], str) or not e["publisher"].strip():
            raise ValidationError("SCHEMA s9: whitelist publisher required")
        if not isinstance(e["rings"], list) or not e["rings"] or \
                not all(isinstance(r, int) and not isinstance(r, bool)
                        and r >= 1 for r in e["rings"]):
            raise ValidationError(
                "SCHEMA s9: whitelist rings must be a non-empty list of "
                "integers >= 1")
    # operative placeholders inside hash-enumerated rulesets
    for name, rs in rulesets.items():
        operative = {k: v for k, v in rs.items() if not k.startswith("_")}
        _placeholder_guard(operative, f"ruleset {name} (operative fields)")
    # the declared digests bind the provided artifacts (issue #7 G3):
    # JSON hashes as JCS per the s9 doctrine. Prose documents (SCHEMA.md,
    # PIPELINE_POLICY.md, SCOPE.md) hash as file bytes and are bound by
    # the standalone verifier, which has the repository; the engine binds
    # everything it is handed.
    bindings = [("mandatory_conditions_hash",
                 rulesets.get("mandatory_conditions"),
                 "rulesets/mandatory_conditions.json"),
                ("admissibility_map_hash",
                 rulesets.get("admissibility_map"),
                 "rules/admissibility_map.json")]
    if registries is not None:
        bindings.append(("predicates_founding_hash",
                         registries.get("predicates"),
                         "registries/predicates.json"))
    for field, artifact, basis in bindings:
        if artifact is None:
            raise ValidationError(
                f"SCHEMA s9: {basis} not provided — cannot bind {field}")
        if sha256_hex(jcs(artifact)) != record[field]:
            raise ValidationError(
                f"SCHEMA s9: {field} does not match sha256(JCS({basis})) "
                f"— the genesis-declared digest binds the artifact in "
                f"force; refusing to seal under rules the genesis does "
                f"not enumerate")
    # the sources file must agree with the inline enumeration (issue #7
    # G4) — the file carries descriptive extras (name, urls, labels);
    # the operative projection {id, publisher, rings} must be identical.
    # SEAL-TIME ONLY (sources_file_agreement=False on audit replay): once
    # genesis is on the chain the inline enumeration is authoritative and
    # the file is scenery — a file later regenerated to mirror
    # governance-added sources must not retroactively condemn the chain
    # (issue #7 follow-up finding: whitelist baseline drift)
    if registries is not None and sources_file_agreement:
        file_proj = {s["id"]: (s["publisher"], tuple(s["rings"]))
                     for s in registries["sources"]["sources"]}
        inline_proj = {e["id"]: (e["publisher"], tuple(e["rings"]))
                       for e in wl}
        if file_proj != inline_proj:
            diverging = sorted(
                set(file_proj) ^ set(inline_proj) |
                {k for k in set(file_proj) & set(inline_proj)
                 if file_proj[k] != inline_proj[k]})
            raise ValidationError(
                f"SCHEMA s9: registries/sources.json diverges from the "
                f"genesis inline whitelist on {diverging} — the inline "
                f"enumeration is authoritative; a source only in the "
                f"file must never seal")


# -------------------------------------------------------- governance (s10)

GOV_FIELDS = frozenset({
    "record_type", "governance_kind", "delta", "effective_from",
    "created", "content_hash", "prev_record_hash"})
GOV_KINDS = frozenset({
    "whitelist_change", "ruleset_change", "ucum_expansion",
    "ascii_exemption", "doc_supersession"})
GOV_DOCS = frozenset({"SCHEMA.md", "PIPELINE_POLICY.md", "SCOPE.md"})
RULESET_TARGETS = frozenset({"mandatory_conditions", "admissibility_map"})


def _validate_ruleset_structure(target: str, content: dict):
    """Issue #7 G2: a ruleset entering force must expose exactly the
    structure validate_fact indexes into. This is the canary — it
    exercises every lookup the seal path performs, so a garbage ruleset
    is refused citably at governance-seal time instead of discovered as
    a KeyError on the next fact (a witnessed liveness kill). Underscore-
    prefixed keys are non-operative commentary and unconstrained."""
    operative = {k for k in content if not k.startswith("_")}
    if target == "mandatory_conditions":
        allowed = {"semantics", "derivation_type_rules", "subject_rules",
                   "source_count_rules"}
        unknown = operative - allowed
        if unknown:
            raise ValidationError(
                f"SCHEMA s10: unknown operative key(s) {sorted(unknown)} "
                f"in mandatory_conditions content")
        dtr = content.get("derivation_type_rules")
        if not isinstance(dtr, dict):
            raise ValidationError(
                "SCHEMA s10: mandatory_conditions content must carry "
                "derivation_type_rules as an object — validate_fact "
                "indexes into it on every seal")
        for k, v in dtr.items():
            if not isinstance(k, str) or (v is not None and (
                    not isinstance(v, list) or
                    not all(isinstance(x, str) and ENT_RE.match(x)
                            for x in v))):
                raise ValidationError(
                    f"SCHEMA s10: derivation_type_rules[{k!r}] must be "
                    f"null or a list of SK-ENT condition property IDs")
        # "semantics" is descriptive commentary (prose/objects) that
        # validate_fact never indexes — allowed, unconstrained
        sr = content.get("subject_rules", [])
        if not isinstance(sr, list):
            raise ValidationError("SCHEMA s10: subject_rules must be a list")
        for rule in sr:
            if not isinstance(rule, dict) or \
                    not {"subject", "requires"} <= set(rule) or \
                    not set(rule) <= {"subject", "requires", "rationale"}:
                raise ValidationError(
                    "SCHEMA s10: subject_rules entries need {subject, "
                    "requires} (optional rationale)")
            if not isinstance(rule["subject"], str) or \
                    not ENT_RE.match(rule["subject"]):
                raise ValidationError(
                    "SCHEMA s10: subject_rules subject must be an SK-ENT ID")
            if not isinstance(rule["requires"], list) or \
                    not all(isinstance(x, str) and ENT_RE.match(x)
                            for x in rule["requires"]):
                raise ValidationError(
                    "SCHEMA s10: subject_rules requires must be a list of "
                    "SK-ENT condition property IDs")
        scr = content.get("source_count_rules", {})
        if not isinstance(scr, dict) or not all(
                isinstance(k, str) and isinstance(v, int)
                and not isinstance(v, bool) and v >= 1
                for k, v in scr.items()):
            raise ValidationError(
                "SCHEMA s10: source_count_rules must map derivation types "
                "to integer minimum distinct-source counts >= 1")
    elif target == "admissibility_map":
        unknown = operative - {"map"}
        if unknown:
            raise ValidationError(
                f"SCHEMA s10: unknown operative key(s) {sorted(unknown)} "
                f"in admissibility_map content")
        amap = content.get("map")
        if not isinstance(amap, dict) or not amap:
            raise ValidationError(
                "SCHEMA s10: admissibility_map content must carry a "
                "non-empty map object — validate_fact indexes into it on "
                "every seal")
        entry_key = re.compile(r"^(ring_[1-9]\d*|notes)$")
        for dtype, entry in amap.items():
            if not isinstance(dtype, str) or not isinstance(entry, dict):
                raise ValidationError(
                    f"SCHEMA s10: map[{dtype!r}] must be an object of "
                    f"ring verdicts")
            for k, v in entry.items():
                if not isinstance(k, str) or not entry_key.match(k) or \
                        not isinstance(v, str):
                    raise ValidationError(
                        f"SCHEMA s10: map[{dtype!r}] keys must be ring_N "
                        f"or notes with string values, got {k!r}")


def validate_governance(record: dict, state: dict):
    """SCHEMA s10: a witnessed change with a machine-readable delta.
    Validated against the rules currently in force (`state`) so a
    governance record can never no-op, double-apply, or reference
    something that is not there. Chain position governs when it binds;
    effective_from is the declared date of decision."""
    if record.get("record_type") != "governance":
        raise ValidationError("not a governance record")
    unknown = set(record) - GOV_FIELDS
    if unknown:
        raise ValidationError(
            f"SCHEMA s10: unknown field(s) {sorted(unknown)} in "
            f"governance record")
    missing = GOV_FIELDS - {"content_hash", "prev_record_hash"} - set(record)
    if missing:
        raise ValidationError(f"SCHEMA s10: missing field(s) {sorted(missing)}")
    kind = record["governance_kind"]
    if kind not in GOV_KINDS:
        raise ValidationError(
            f"SCHEMA s10: unknown governance_kind {kind!r} — kinds are "
            f"{sorted(GOV_KINDS)}")
    if not isinstance(record["effective_from"], str) or \
            not DATE_RE.match(record["effective_from"]):
        raise ValidationError(
            "SCHEMA s10: effective_from must be YYYY-MM-DD (chain "
            "position governs binding; this is the declared date)")
    if not isinstance(record["created"], str) or \
            not TS_RE.match(record["created"]):
        raise ValidationError("SCHEMA s7.2.2: created not UTC timestamp form")
    _placeholder_guard(record, "governance record")

    delta = record["delta"]
    if not isinstance(delta, dict) or not delta:
        raise ValidationError("SCHEMA s10: delta must be a non-empty object")
    # wider placeholder net for deltas (issue #7 G5): a delta is operative
    # by definition, and '<<' appears in no legitimate ruleset, source, or
    # unit — any angle-bracket marker ('<<TBD>>', '<<FIXME>>') is a
    # placeholder that must never enter force
    if "<<" in json.dumps(delta, ensure_ascii=False):
        raise ValidationError(
            "SCHEMA s10: placeholder-style marker '<<' in governance "
            "delta — refusing to seal")

    if kind == "ucum_expansion":
        codes = delta.get("add_codes")
        if set(delta) != {"add_codes"} or not isinstance(codes, list) \
                or not codes:
            raise ValidationError(
                "SCHEMA s10: ucum_expansion delta is {add_codes: [...]} "
                "(non-empty)")
        for c in codes:
            if not isinstance(c, str) or not c:
                raise ValidationError(
                    "SCHEMA s10: each UCUM code must be a non-empty string")
            # a non-ASCII code may enter only once each of its non-ASCII
            # characters is exempted (an ascii_exemption record must
            # precede it) — the tripwire is narrowed before, never by,
            # the code that needs it
            for ch in c:
                if ord(ch) > 127:
                    if ch not in state["ascii_exempt"]:
                        raise ValidationError(
                            f"SCHEMA s10: UCUM code {c!r} contains "
                            f"non-ASCII U+{ord(ch):04X} not yet exempted "
                            f"— seal an ascii_exemption record first")
                elif not UCUM_CHAR_RE.match(ch):
                    # issue #7 G5: codes get a syntax check, not just
                    # non-empty stringhood
                    raise ValidationError(
                        f"SCHEMA s10: {c!r} is not valid UCUM code "
                        f"syntax (character {ch!r})")
        if len(set(codes)) != len(codes):
            raise ValidationError("SCHEMA s10: duplicate codes in delta")
        already = set(codes) & state["ucum"]
        if already:
            raise ValidationError(
                f"SCHEMA s10: code(s) {sorted(already)} already in force "
                f"— a governance record never no-ops")

    elif kind == "ascii_exemption":
        chars = delta.get("exempt_chars")
        if set(delta) != {"exempt_chars"} or not isinstance(chars, list) \
                or not chars:
            raise ValidationError(
                "SCHEMA s10: ascii_exemption delta is {exempt_chars: "
                "[...]} (non-empty single characters)")
        for c in chars:
            if not isinstance(c, str) or len(c) != 1 or ord(c) < 128:
                raise ValidationError(
                    f"SCHEMA s10: exempt_chars entries must be single "
                    f"non-ASCII characters, got {c!r}")
        if set(chars) & state["ascii_exempt"]:
            raise ValidationError(
                "SCHEMA s10: character(s) already exempted — never no-op")

    elif kind == "whitelist_change":
        allowed_ops = {"add", "remove", "set_rings"}
        if not set(delta) <= allowed_ops:
            raise ValidationError(
                f"SCHEMA s10: whitelist_change delta ops are "
                f"{sorted(allowed_ops)}")
        wl = state["whitelist"]
        for e in delta.get("add", []):
            if not isinstance(e, dict) or \
                    set(e) != {"id", "publisher", "rings"}:
                raise ValidationError(
                    "SCHEMA s10: whitelist add entries need exactly "
                    "{id, publisher, rings}")
            if not isinstance(e["id"], str) or not SRC_RE.match(e["id"]):
                raise ValidationError("SCHEMA s10: malformed source ID")
            if e["id"] in wl:
                raise ValidationError(
                    f"SCHEMA s10: source {e['id']} already whitelisted")
            if not isinstance(e["rings"], list) or not e["rings"] or \
                    not all(isinstance(r, int) and not isinstance(r, bool)
                            and r >= 1 for r in e["rings"]):
                raise ValidationError(
                    "SCHEMA s10: rings must be a non-empty list of "
                    "integers >= 1")
        for sid in delta.get("remove", []):
            if sid not in wl:
                raise ValidationError(
                    f"SCHEMA s10: cannot remove {sid!r} — not whitelisted")
        for e in delta.get("set_rings", []):
            if not isinstance(e, dict) or set(e) != {"id", "rings"}:
                raise ValidationError(
                    "SCHEMA s10: set_rings entries need exactly {id, rings}")
            if e["id"] not in wl:
                raise ValidationError(
                    f"SCHEMA s10: cannot set rings for {e['id']!r} — "
                    f"not whitelisted")

    elif kind == "ruleset_change":
        if set(delta) != {"target", "content"}:
            raise ValidationError(
                "SCHEMA s10: ruleset_change delta is {target, content}")
        if delta["target"] not in RULESET_TARGETS:
            raise ValidationError(
                f"SCHEMA s10: ruleset target must be one of "
                f"{sorted(RULESET_TARGETS)}")
        content = delta["content"]
        if not isinstance(content, dict) or not content:
            raise ValidationError(
                "SCHEMA s10: ruleset content must be the full new "
                "ruleset object, inline (the chain stays self-contained)")
        operative = {k: v for k, v in content.items()
                     if not k.startswith("_")}
        _placeholder_guard(operative, "governance ruleset content")
        # issue #7 G2: the content must expose the structure the seal
        # path indexes into, or the next fact seal crashes uncitably
        _validate_ruleset_structure(delta["target"], content)

    elif kind == "doc_supersession":
        if set(delta) != {"document", "new_version", "new_hash"}:
            raise ValidationError(
                "SCHEMA s10: doc_supersession delta is "
                "{document, new_version, new_hash}")
        if delta["document"] not in GOV_DOCS:
            raise ValidationError(
                f"SCHEMA s10: document must be one of {sorted(GOV_DOCS)}")
        if not isinstance(delta["new_version"], str) or \
                not delta["new_version"].strip():
            raise ValidationError("SCHEMA s10: new_version required")
        if not isinstance(delta["new_hash"], str) or \
                not HASH_RE.match(delta["new_hash"]):
            raise ValidationError(
                "SCHEMA s10: new_hash must be 64 lowercase hex chars")


# ---------------------------------------------------------------- ledger

class Ledger:
    def __init__(self, path, registries: dict, rulesets: dict):
        self.path = Path(path) if path is not None else None
        self.registries = registries
        self.rulesets = rulesets
        # position-zero ruleset snapshot, taken BEFORE any governance
        # replay rebinds self.rulesets to end state. verify(full) must
        # replay from here, or records sealed before a ruleset_change
        # are judged by rules that did not exist yet (issue #7 G1).
        self._genesis_rulesets = dict(rulesets)
        self.records = []
        self.flags = []  # near-duplicate warnings (s11: warn, not a byte rule)
        self._init_indexes()
        if self.path is not None and self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.records = data["records"]
            for i, r in enumerate(self.records):
                # a hostile/corrupt store may hold bytes that trip the
                # canonicalizer (a float, a lone surrogate); indexing must
                # not crash — surface it as a clean, citable load error
                try:
                    self._index(r)
                    # replay genesis + governance so in-force state
                    # (whitelist, UCUM, exemptions, rulesets) matches
                    # the chain — the chain alone, never the files
                    if isinstance(r, dict) and \
                            r.get("record_type") == "genesis":
                        self._apply_genesis(r)
                    if isinstance(r, dict) and \
                            r.get("record_type") == "governance":
                        self._apply_governance(r)
                except ValidationError as e:
                    raise ValidationError(
                        f"ledger file corrupt at record {i} "
                        f"({r.get('fact_id', r.get('record_type'))}): {e}")
            stored = data.get("chain_head")
            if stored is not None and stored != self.chain_head():
                raise ValidationError(
                    "ledger file chain_head does not match the recomputed "
                    "chain head — file corrupt or tampered")

    def _init_indexes(self):
        self._by_id = {}        # fact_id -> {version: record}
        self._by_triple = {}    # triple_hash -> [record, ...]
        self._by_prefix12 = {}  # triple_hash[:12] -> {triple_hash, ...}
        self._superseded = set()  # {"fact_id@version", ...} named as targets
        self._np_units = {}     # near-dup key -> {unit, ...}
        # rules in force, evolved by governance records as they seal
        # (SCHEMA s10/P9): the ruleset governing any fact is genesis
        # state plus all preceding governance records — resolvable from
        # the chain alone.
        self._ucum = set(UCUM_V1)
        self._ascii_exempt = set()
        # pre-genesis default only: once genesis seals, _apply_genesis
        # replaces this with the genesis record's inline enumeration —
        # the chain-authoritative founding whitelist (issue #7 G4). The
        # file projection must match the inline one (validate_genesis),
        # so nothing can seal that a chain-alone verifier would refuse.
        base_wl = {s["id"]: s for s in
                   self.registries["sources"]["sources"]}
        self._whitelist = {k: dict(v) for k, v in base_wl.items()}

    def _apply_genesis(self, record):
        """The genesis record's inline whitelist becomes the in-force
        founding whitelist (issue #7 G4) — state reconstructible from
        the chain alone, invariant 6."""
        self._whitelist = {
            e["id"]: {"id": e["id"], "publisher": e["publisher"],
                      "rings": list(e["rings"])}
            for e in record["whitelist"]}

    def rules_in_force(self) -> dict:
        """The rules governing the next fact — a snapshot, for
        transparency and for validate_fact's keyword arguments."""
        return {
            "ucum": set(self._ucum),
            "ascii_exempt": set(self._ascii_exempt),
            "whitelist": {k: dict(v) for k, v in self._whitelist.items()},
            "rulesets": self.rulesets,
        }

    def _apply_governance(self, record):
        """Fold a validated governance record into the in-force state."""
        kind, delta = record["governance_kind"], record["delta"]
        if kind == "ucum_expansion":
            self._ucum.update(delta["add_codes"])
        elif kind == "ascii_exemption":
            self._ascii_exempt.update(delta["exempt_chars"])
        elif kind == "whitelist_change":
            for e in delta.get("add", []):
                self._whitelist[e["id"]] = {
                    "id": e["id"], "publisher": e["publisher"],
                    "rings": list(e["rings"])}
            for sid in delta.get("remove", []):
                self._whitelist.pop(sid, None)
            for e in delta.get("set_rings", []):
                self._whitelist[e["id"]]["rings"] = list(e["rings"])
        elif kind == "ruleset_change":
            self.rulesets = dict(self.rulesets)
            self.rulesets[delta["target"]] = delta["content"]
        # doc_supersession records the new hash on the chain; it changes
        # no in-memory validation state (the document itself is unsealed)

    def _np_key(self, triple):
        ct = canonical_triple(triple)
        return sha256_hex(jcs([ct["subject"], ct["predicate"],
                               ct["conditions"]]))

    def _index(self, r):
        if r.get("record_type") != "fact":
            return
        self._by_id.setdefault(r["fact_id"], {})[r["version"]] = r
        self._by_triple.setdefault(r["triple_hash"], []).append(r)
        self._by_prefix12.setdefault(r["triple_hash"][:12], set()).add(
            r["triple_hash"])
        if isinstance(r.get("supersedes"), str):
            self._superseded.add(r["supersedes"])
        # near-dup heuristic is quantity-specific (unit-converted
        # duplicates); entity/date objects have no unit — skip them so
        # Ring 2 activation cannot crash the index
        obj = r["triple"].get("object") if isinstance(r.get("triple"), dict) \
            else None
        if isinstance(obj, dict) and obj.get("type") == "quantity" \
                and "unit" in obj:
            self._np_units.setdefault(
                self._np_key(r["triple"]), set()).add(obj["unit"])

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

        # fact_id form is deterministic, not a free choice (SCHEMA s6):
        # the 12-char form is default; the 16-char form is permitted ONLY
        # when this triple's 12-char prefix actually collides with an
        # already-sealed DIFFERENT triple. Enforcing this removes the
        # accidental re-entry channel: a fully-superseded triple could
        # otherwise re-seal at version 1 under the 16-char form with no
        # supersedes link (FD-25).
        id_hex = FACT_ID_RE.match(fid).group(3)
        collision = bool(self._by_prefix12.get(th[:12], set()) - {th})
        if len(id_hex) == 16 and not collision:
            raise ValidationError(
                "SCHEMA s6: 16-char fact_id form is only permitted on a "
                "real 12-char prefix collision with a different triple; "
                "use the 12-char form")
        if len(id_hex) == 12 and collision:
            raise ValidationError(
                "SCHEMA s6: 12-char prefix collides with a different "
                "sealed triple — this fact must use the 16-char form")

        # derived_from must reference sealed facts; a reference to a
        # superseded fact is legitimate (you derive from the record you
        # derived from) but flagged so a verifier walking the graph knows
        # the target is no longer live (N8; warn, never refuse)
        for x in record["derivation"]["derived_from"]:
            versions = self._by_id.get(x)
            if not versions:
                raise ValidationError(
                    f"SCHEMA s11: derived_from references unknown fact {x}")
            latest = max(versions)
            if f"{x}@{latest}" in self._superseded:
                self.flags.append(
                    f"derived_from liveness: {fid} derives from {x}, whose "
                    f"latest version @{latest} is superseded — the "
                    f"dependency does not resolve to a live fact")

        # duplicate condition properties are LEGITIMATE (s3.4 min/max
        # range pairs) but also a mandatory-condition gaming vector when
        # values conflict (issue #5 F2) — flag for review, never refuse
        props = [c["property"] for c in record["triple"]["conditions"]]
        dup_props = sorted({p for p in props if props.count(p) > 1})
        if dup_props:
            self.flags.append(
                f"duplicate-condition-property flag: {fid} carries "
                f"multiple conditions on {dup_props} — legitimate for "
                f"ranges (s3.4); review must confirm the values do not "
                f"conflict")

        # near-duplicate flag (s11: same subject+predicate+conditions,
        # different unit -> human review; a warning, never a refusal;
        # quantity objects only — the heuristic is unit-based)
        rec_obj = record["triple"]["object"]
        other_units = set()
        if rec_obj.get("type") == "quantity":
            other_units = self._np_units.get(
                self._np_key(record["triple"]), set()) - {rec_obj["unit"]}
        if other_units:
            self.flags.append(
                f"near-duplicate flag: {fid} shares subject+predicate+"
                f"conditions with sealed fact(s) in unit(s) "
                f"{sorted(other_units)} — possible unit-converted duplicate")

    def seal(self, record: dict) -> dict:
        rt = record.get("record_type")
        if not self.records and rt != "genesis":
            raise ValidationError("SCHEMA s8: record 0 must be genesis")
        applied_gov = None
        if rt == "fact":
            validate_fact(record, self.registries, self.rulesets,
                          whitelist=self._whitelist, ucum=self._ucum,
                          ascii_exempt=self._ascii_exempt)
            self._check_chain_rules(record)
        elif rt == "genesis":
            if self.records:
                raise ValidationError("genesis must be record zero")
            validate_genesis(
                record, self.rulesets, self.registries,
                sources_file_agreement=not getattr(
                    self, "_audit_replay", False))
        elif rt == "governance":
            # SCHEMA s10/P9: validate the payload against the rules in
            # force at this chain position, then fold it in so every
            # later fact is judged by genesis state + preceding
            # governance records — resolvable from the chain alone.
            validate_governance(record, self.rules_in_force())
            applied_gov = record
        elif rt == "inscription":
            _placeholder_guard(record, "inscription record")
        else:
            raise ValidationError(f"unknown record_type {rt!r}")

        record = dict(record)
        record["prev_record_hash"] = (
            GENESIS_PREV if not self.records
            else self.records[-1]["content_hash"])
        record["content_hash"] = content_hash(record)
        self.records.append(record)
        self._index(record)
        if rt == "genesis":
            self._apply_genesis(record)
        if applied_gov is not None:
            self._apply_governance(record)
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
        against derived status, supersession linkage, genesis-first.

        verify() NEVER raises: auditing a hostile or corrupt store is its
        entire job, so bytes that would trip the canonicalizer (a stored
        float, a lone surrogate) are reported as findings, not crashes."""
        findings = []
        prev = GENESIS_PREV
        for i, r in enumerate(self.records):
            fid = r.get("fact_id", r.get("record_type")) \
                if isinstance(r, dict) else "<non-object>"
            # any exception here means the stored record is corrupt or
            # hostile — report it, never propagate (verify()'s contract)
            try:
                if r.get("prev_record_hash") != prev:
                    findings.append(f"record {i}: broken chain link")
                if content_hash(r) != r.get("content_hash"):
                    findings.append(f"TAMPERED: {fid} (record {i})")
                if r.get("record_type") == "fact":
                    if triple_hash(r["triple"]) != r["triple_hash"]:
                        findings.append(
                            f"TAMPERED TRIPLE: {fid} (record {i})")
            except Exception as e:  # noqa: BLE001 - see contract above
                findings.append(
                    f"CORRUPT record {i} ({fid}): "
                    f"{type(e).__name__}: {str(e)[:80]}")
            prev = r.get("content_hash") if isinstance(r, dict) else None

        if full:
            # the shadow replays from the POSITION-ZERO ruleset snapshot,
            # never from self.rulesets — by now that is end state (load
            # already folded every governance record), and replaying from
            # it judges pre-change records by rules that did not exist
            # when they sealed (issue #7 G1: a tightening ruleset_change
            # retroactively condemned history)
            shadow = Ledger(None, self.registries,
                            dict(self._genesis_rulesets))
            # audit replay: the genesis file-agreement guard is a
            # seal-time authoring check only — on audit, the inline
            # whitelist is authoritative and file drift is not a chain
            # defect (the --repo binding of the standalone verifier
            # reports file drift separately, with governance honored)
            shadow._audit_replay = True
            for i, r in enumerate(self.records):
                try:
                    body = {k: v for k, v in r.items() if k != "content_hash"}
                    shadow.seal(dict(body))
                except Exception as e:  # noqa: BLE001 - see contract above
                    fid = r.get("fact_id", r.get("record_type")) \
                        if isinstance(r, dict) else "<non-object>"
                    findings.append(f"INVALID record {i} ({fid}): "
                                    f"{type(e).__name__}: {str(e)[:80]}")
                    # keep the replay coherent so later records can still
                    # resolve supersedes/derived_from targets — but only if
                    # the record is well-formed enough to index
                    try:
                        shadow.records.append(dict(r))
                        shadow._index(r)
                    except Exception:  # noqa: BLE001
                        pass
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
