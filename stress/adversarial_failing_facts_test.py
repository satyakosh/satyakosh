#!/usr/bin/env python3
"""
Satyakosh Adversarial Failing-Facts Stress Test  (v2 — bounty-grade)
=====================================================================
Self-contained test file for Claude / any model / human review.

This file re-implements the *critical* validation gates from
Satyakosh SCHEMA 1.0.0-rc + ledger.py + rulesets so that anyone
can run it without the full repository.

It contains:
  - A minimal but faithful validator (expanded)
  - 24 deliberately failing facts covering distinct failure classes
  - 3 deliberately correct Ring-1 facts (sanity check)

Expected result when run:
  - All 24 adversarial facts must FAIL with a citable reason
  - The 3 correct facts must PASS

Run:
    python satyakosh_adversarial_failing_facts_test.py

Author: generated for Satyakosh Genesis Window adversarial review
        (bounty-level pass — looking for residual surface)
"""

from __future__ import annotations
import re
import json
from typing import Any

# ---------------------------------------------------------------------------
# Minimal re-implementation of the critical gates (SCHEMA + ledger.py)
# ---------------------------------------------------------------------------

VALUE_RE = re.compile(r"^(0|-?[1-9](\.\d+)?e(0|-?[1-9]\d*))$")
ENT_RE   = re.compile(r"^SK-ENT-\d{6}$")
PRED_RE  = re.compile(r"^SK-PRED-\d{6}$")
SRC_RE   = re.compile(r"^SK-SRC-\d{6}$")
DATE_RE  = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TS_RE    = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
HASH_RE  = re.compile(r"^[0-9a-f]{64}$")
FACT_ID_RE = re.compile(r"^SK-R([1-9]\d*)-([A-Z][A-Z0-9]*)-([0-9a-f]{12}|[0-9a-f]{16})$")

# Closed v1 UCUM whitelist taken from ledger.py
UCUM_V1 = {
    "1", "m", "s", "g", "kg", "A", "K", "mol", "cd", "Hz", "N", "Pa",
    "kPa", "J", "W", "C", "V", "Ohm", "lm", "lx", "Cel", "eV",
    "m/s", "m/s2", "m2", "m3", "J.s", "J/K", "mol-1", "lm/W", "kg/m3",
    "%", "a"
}

# Admissibility map (founding)
ADMISSIBILITY = {
    "si_exact_definition":       "SEAL",
    "defined_convention":        "SEAL",
    "mathematical_proof":        "SEAL",
    "laboratory_measurement":    "SEAL",
    "derived_exact":             "SEAL",
    "statistical_analysis":      "RING-2 PENDING",
    "documentary_evidence":      "RING-2 PENDING",
    "causal_inference":          "BLOCKED",
    "institutional_declaration": "BLOCKED",
}

# Mandatory conditions (subject rules)
MANDATORY_SUBJECT = {
    "SK-ENT-000005": ["SK-ENT-000006", "SK-ENT-000007"],  # boiling T of water
}

# Known entities / predicates / sources for the test
KNOWN_ENTS  = {
    "SK-ENT-000001", "SK-ENT-000002", "SK-ENT-000003", "SK-ENT-000004",
    "SK-ENT-000005", "SK-ENT-000006", "SK-ENT-000007", "SK-ENT-000008",
    "SK-ENT-000009", "SK-ENT-000010", "SK-ENT-000011", "SK-ENT-000012",
}
KNOWN_PREDS = {"SK-PRED-000001"}
KNOWN_SRCS  = {"SK-SRC-000001", "SK-SRC-000002", "SK-SRC-000003"}

# Exact field sets (unknown fields must be refused)
FACT_FIELDS = {
    "record_type", "fact_id", "triple_hash", "version", "supersedes",
    "triple", "ring", "valid_from", "valid_until", "terminality",
    "sources", "derivation", "process_hash",
    "status", "created", "content_hash", "prev_record_hash"
}


class ValidationError(Exception):
    pass


def is_ascii(s: str) -> bool:
    try:
        s.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


def validate_quantity(obj: dict, where: str = "object") -> None:
    if not isinstance(obj, dict):
        raise ValidationError(f"SCHEMA s3.3: {where} must be a typed union object")
    if obj.get("type") != "quantity":
        raise ValidationError(
            f"SCHEMA s3.3: v1 gate admits type 'quantity' only ({where}); "
            f"got {obj.get('type')!r}"
        )
    val = obj.get("value")
    if not isinstance(val, str) or not VALUE_RE.match(val):
        raise ValidationError(f"SCHEMA s7.3: {where} value {val!r} violates the grammar")
    unit = obj.get("unit")
    if not isinstance(unit, str) or not unit:
        raise ValidationError(f"SCHEMA s3.3: {where} unit required")
    if unit not in UCUM_V1:
        raise ValidationError(
            f"SCHEMA s11: {where} unit {unit!r} is not in the v1 UCUM code whitelist"
        )
    if not isinstance(obj.get("exact"), bool):
        raise ValidationError(f"SCHEMA s3.3: {where} exact must be boolean")
    unc = obj.get("uncertainty")
    if unc is not None:
        if not isinstance(unc, str) or not VALUE_RE.match(unc):
            raise ValidationError(f"SCHEMA s7.3: {where} uncertainty violates the grammar")
        if unc.startswith("-"):
            raise ValidationError(f"SCHEMA s3.3: {where} uncertainty must be non-negative")
        if obj["exact"]:
            raise ValidationError(
                f"SCHEMA s3.3: {where} is exact — cannot carry uncertainty"
            )


def validate_fact(record: dict) -> None:
    """Minimal but faithful implementation of the main gates."""
    if record.get("record_type") != "fact":
        raise ValidationError("not a fact record")

    # Unknown fields (smuggling channel)
    unknown = set(record) - FACT_FIELDS
    if unknown:
        raise ValidationError(
            f"SCHEMA s4: unknown field(s) {sorted(unknown)} in fact record"
        )

    # Basic required fields (subset that this minimal validator checks)
    required = ["fact_id", "triple", "ring", "derivation", "sources", "status", "created"]
    for f in required:
        if f not in record:
            raise ValidationError(f"SCHEMA s4: missing field {f}")

    if record["status"] != "sealed":
        raise ValidationError("SCHEMA s4: status must be 'sealed' at seal time")

    ring = record.get("ring")
    if not isinstance(ring, int) or isinstance(ring, bool) or ring < 1:
        raise ValidationError(f"SCHEMA s4: ring must be integer >= 1, got {ring!r}")
    if ring != 1:
        raise ValidationError(
            f"Ring {ring} is not active in founding scope (only Ring 1 is SEAL today)"
        )

    # Triple
    triple = record["triple"]
    if not isinstance(triple, dict):
        raise ValidationError("SCHEMA s3: triple must be object")
    for k in ("subject", "predicate", "object", "conditions"):
        if k not in triple:
            raise ValidationError(f"SCHEMA s3: triple missing {k}")

    subj = triple["subject"]
    pred = triple["predicate"]
    if not isinstance(subj, str) or not ENT_RE.match(subj) or subj not in KNOWN_ENTS:
        raise ValidationError("SCHEMA s11: subject not in entity registry")
    if not isinstance(pred, str) or not PRED_RE.match(pred) or pred not in KNOWN_PREDS:
        raise ValidationError("SCHEMA s11: predicate not in registry")

    validate_quantity(triple["object"], "object")

    # Conditions
    conds = triple["conditions"]
    if not isinstance(conds, list):
        raise ValidationError("SCHEMA s3.4: conditions must be array")
    present_props = set()
    for c in conds:
        if not isinstance(c, dict) or "property" not in c or "object" not in c:
            raise ValidationError("SCHEMA s3.4: malformed condition")
        prop = c["property"]
        if not isinstance(prop, str) or not ENT_RE.match(prop) or prop not in KNOWN_ENTS:
            raise ValidationError(f"SCHEMA s11: condition property {prop} unknown")
        validate_quantity(c["object"], f"condition {prop}")
        present_props.add(prop)

    # Mandatory subject rules
    if subj in MANDATORY_SUBJECT:
        for req in MANDATORY_SUBJECT[subj]:
            if req not in present_props:
                raise ValidationError(
                    f"rulesets/mandatory_conditions.json: required condition "
                    f"property {req} absent — never enters review"
                )

    # Sources
    sources = record["sources"]
    if not isinstance(sources, list) or not sources:
        raise ValidationError("SCHEMA s4: sources must be a non-empty array")
    for s in sources:
        if not isinstance(s, dict):
            raise ValidationError("SCHEMA s4: each source must be an object")
        sid = s.get("source")
        if not isinstance(sid, str) or not SRC_RE.match(sid) or sid not in KNOWN_SRCS:
            raise ValidationError(f"SCHEMA s11: source {sid} not whitelisted")
        edition = s.get("edition")
        if not isinstance(edition, str) or not edition.strip():
            raise ValidationError("SCHEMA s4: source edition required and non-empty")

    # Derivation / admissibility
    deriv = record["derivation"]
    if not isinstance(deriv, dict):
        raise ValidationError("SCHEMA s4.1: derivation must be object")
    dtype = deriv.get("type")
    if dtype not in ADMISSIBILITY:
        raise ValidationError(f"unknown derivation.type {dtype!r}")
    verdict = ADMISSIBILITY[dtype]
    if verdict != "SEAL":
        raise ValidationError(
            f"rules/admissibility_map.json: derivation type {dtype!r} is "
            f"{verdict} (not SEAL for ring 1)"
        )

    if dtype == "derived_exact" and not deriv.get("derived_from"):
        raise ValidationError("SCHEMA s11: derived_exact requires non-empty derived_from")

    # valid_from / valid_until consistency
    vf = record.get("valid_from")
    vu = record.get("valid_until")
    if vf is not None and (not isinstance(vf, str) or not DATE_RE.match(vf)):
        raise ValidationError(f"SCHEMA s7.2.2: valid_from must be null or YYYY-MM-DD")
    if vu is not None and (not isinstance(vu, str) or not DATE_RE.match(vu)):
        raise ValidationError(f"SCHEMA s7.2.2: valid_until must be null or YYYY-MM-DD")
    if vf and vu and vf > vu:
        raise ValidationError("SCHEMA s4: valid_from is after valid_until")

    term = record.get("terminality")
    if term is not None:
        if term not in ("none", "expected", "scheduled"):
            raise ValidationError(f"SCHEMA s4: invalid terminality {term!r}")
        if (term == "scheduled") != (vu is not None):
            raise ValidationError(
                "SCHEMA s4: terminality 'scheduled' requires valid_until, "
                "and a dated valid_until requires terminality 'scheduled'"
            )

    # ASCII tripwire (fact records must be pure ASCII)
    raw = json.dumps(record, ensure_ascii=False)
    if not is_ascii(raw):
        raise ValidationError(
            "SCHEMA s7.2: non-ASCII byte in fact canonical form — "
            "homoglyph/invisible-character tripwire"
        )

    # Fact ID form (basic)
    fid = record["fact_id"]
    if not isinstance(fid, str) or not FACT_ID_RE.match(fid):
        raise ValidationError(f"SCHEMA s6: fact_id {fid!r} malformed")
    m = FACT_ID_RE.match(fid)
    if int(m.group(1)) != ring:
        raise ValidationError(
            f"SCHEMA s6: fact_id ring segment R{m.group(1)} != record ring {ring}"
        )


# ---------------------------------------------------------------------------
# The adversarial facts  (24 distinct failure classes)
# ---------------------------------------------------------------------------

FAILING_FACTS = [

    # ----- Value grammar -----
    {
        "name": "01_value_plain_integer",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaaa",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "299792458",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "s7.3"
    },
    {
        "name": "02_value_plus_exponent",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-bbbbbbbbbbbb",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e+8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "s7.3"
    },
    {
        "name": "03_value_uppercase_E",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-cccccccccccc",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458E8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "s7.3"
    },
    {
        "name": "04_value_leading_zero_exponent",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-dddddddddddd",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "1e03",
                    "unit": "1",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "mathematical_proof", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "s7.3"
    },
    {
        "name": "05_value_trailing_dot",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-eeeeeeeeeeee",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "1.e3",
                    "unit": "1",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "mathematical_proof", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "s7.3"
    },

    # ----- Exact / uncertainty -----
    {
        "name": "06_exact_with_uncertainty",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-ffffffffffff",
            "triple": {
                "subject": "SK-ENT-000002",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "6.62607015e-34",
                    "unit": "J.s",
                    "exact": True,
                    "uncertainty": "1e-42"
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "exact"
    },
    {
        "name": "07_negative_uncertainty",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-111111111111",
            "triple": {
                "subject": "SK-ENT-000003",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "6.67430e-11",
                    "unit": "m3",
                    "exact": False,
                    "uncertainty": "-1.5e-15"
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "laboratory_measurement", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "non-negative"
    },

    # ----- UCUM -----
    {
        "name": "08_bad_ucum_unit",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-222222222222",
            "triple": {
                "subject": "SK-ENT-000003",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "6.67430e-11",
                    "unit": "m3.kg-1.s-2",
                    "exact": False,
                    "uncertainty": "1.5e-15"
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "laboratory_measurement", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "UCUM"
    },

    # ----- Mandatory conditions -----
    {
        "name": "09_missing_mandatory_conditions",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-333333333333",
            "triple": {
                "subject": "SK-ENT-000005",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "3.7315e2",
                    "unit": "K",
                    "exact": False,
                    "uncertainty": "1e-2"
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "laboratory_measurement", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000002", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "mandatory_conditions"
    },

    # ----- Admissibility -----
    {
        "name": "10_statistical_on_ring1",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-444444444444",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "statistical_analysis", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "RING-2 PENDING"
    },
    {
        "name": "11_causal_blocked",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-555555555555",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "1e0",
                    "unit": "1",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "causal_inference", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "BLOCKED"
    },
    {
        "name": "12_institutional_blocked",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-666666666666",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "1e0",
                    "unit": "1",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "institutional_declaration", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "BLOCKED"
    },

    # ----- derived_exact -----
    {
        "name": "13_derived_exact_empty",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-777777777777",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {
                "type": "derived_exact",
                "script": None,
                "derived_from": []
            },
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "derived_from"
    },

    # ----- ASCII / homoglyph -----
    {
        "name": "14_non_ascii_zwsp",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-888888888888",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022\u200b", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "non-ASCII"
    },

    # ----- Sources -----
    {
        "name": "15_empty_sources",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-999999999999",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "sources"
    },
    {
        "name": "16_empty_edition",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaab",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "   ", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "edition"
    },

    # ----- Object type gate (Ring 2 reserved) -----
    {
        "name": "17_object_type_entity",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaac",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "entity",
                    "id": "SK-ENT-000002"
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "defined_convention", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "quantity"
    },
    {
        "name": "18_object_type_date",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaad",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "date",
                    "value": "1947-08-15",
                    "precision": "day",
                    "calendar": "gregorian"
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "documentary_evidence", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "quantity"
    },

    # ----- Validity window / terminality -----
    {
        "name": "19_valid_from_after_until",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaae",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "valid_from": "2026-01-01",
            "valid_until": "2020-01-01",
            "terminality": "scheduled",
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "valid_from"
    },
    {
        "name": "20_terminality_mismatch",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaaf",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "valid_until": "2030-01-01",
            "terminality": "none",
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "terminality"
    },

    # ----- Fact ID / ring consistency -----
    {
        "name": "21_fact_id_wrong_ring_segment",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R2-PHYS-aaaaaaaaaaag",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "fact_id"
    },

    # ----- Unknown field (smuggling) -----
    {
        "name": "22_unknown_extra_field",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaah",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z",
            "extra_smuggled_field": "this should be refused"
        },
        "expected_reason_contains": "unknown field"
    },

    # ----- Condition property unknown -----
    {
        "name": "23_unknown_condition_property",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaai",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": [
                    {
                        "property": "SK-ENT-999999",
                        "object": {
                            "type": "quantity",
                            "value": "1e0",
                            "unit": "1",
                            "exact": True,
                            "uncertainty": None
                        }
                    }
                ]
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "condition property"
    },

    # ----- Ring 0 / invalid ring -----
    {
        "name": "24_ring_zero",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-aaaaaaaaaaaj",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 0,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        },
        "expected_reason_contains": "ring"
    },
]


# Three correct facts (sanity check – must PASS)
CORRECT_FACTS = [
    {
        "name": "CORRECT_si_exact_c",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-9f3a2c81d4e0",
            "triple": {
                "subject": "SK-ENT-000001",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "2.99792458e8",
                    "unit": "m/s",
                    "exact": True,
                    "uncertainty": None
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "si_exact_definition", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        }
    },
    {
        "name": "CORRECT_lab_G_allowed_unit",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-a1b2c3d4e5f6",
            "triple": {
                "subject": "SK-ENT-000003",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "6.67430e-11",
                    "unit": "m3",
                    "exact": False,
                    "uncertainty": "1.5e-15"
                },
                "conditions": []
            },
            "ring": 1,
            "derivation": {"type": "laboratory_measurement", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000001", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        }
    },
    {
        "name": "CORRECT_boiling_with_mandatory_conditions",
        "record": {
            "record_type": "fact",
            "fact_id": "SK-R1-PHYS-b2c3d4e5f6a7",
            "triple": {
                "subject": "SK-ENT-000005",
                "predicate": "SK-PRED-000001",
                "object": {
                    "type": "quantity",
                    "value": "3.7315e2",
                    "unit": "K",
                    "exact": False,
                    "uncertainty": "1e-2"
                },
                "conditions": [
                    {
                        "property": "SK-ENT-000006",
                        "object": {
                            "type": "quantity",
                            "value": "1.01325e5",
                            "unit": "Pa",
                            "exact": True,
                            "uncertainty": None
                        }
                    },
                    {
                        "property": "SK-ENT-000007",
                        "object": {
                            "type": "quantity",
                            "value": "1e0",
                            "unit": "1",
                            "exact": True,
                            "uncertainty": None
                        }
                    }
                ]
            },
            "ring": 1,
            "derivation": {"type": "laboratory_measurement", "script": None, "derived_from": []},
            "sources": [{"source": "SK-SRC-000002", "edition": "2022", "retrieved": "2026-07-01"}],
            "status": "sealed",
            "created": "2026-07-19T00:00:00Z"
        }
    },
]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main() -> int:
    print("=" * 72)
    print("Satyakosh Adversarial Failing-Facts Stress Test  (v2 — bounty-grade)")
    print("=" * 72)
    print()

    failed_as_expected = 0
    unexpectedly_passed = 0
    correct_passed = 0
    correct_failed = 0

    print("--- ADVERSARIAL FACTS (must FAIL) ---")
    for item in FAILING_FACTS:
        name = item["name"]
        record = item["record"]
        try:
            validate_fact(record)
            print(f"  [UNEXPECTED PASS] {name}")
            unexpectedly_passed += 1
        except ValidationError as e:
            reason = str(e)
            ok = item["expected_reason_contains"].lower() in reason.lower()
            status = "FAIL (good)" if ok else f"FAIL but unexpected reason"
            print(f"  [{status}] {name}")
            print(f"       → {reason}")
            if ok:
                failed_as_expected += 1
        print()

    print("--- CORRECT FACTS (must PASS) ---")
    for item in CORRECT_FACTS:
        name = item["name"]
        try:
            validate_fact(item["record"])
            print(f"  [PASS] {name}")
            correct_passed += 1
        except ValidationError as e:
            print(f"  [UNEXPECTED FAIL] {name}: {e}")
            correct_failed += 1
        print()

    print("=" * 72)
    print("SUMMARY")
    print(f"  Adversarial facts that correctly failed : {failed_as_expected} / {len(FAILING_FACTS)}")
    print(f"  Adversarial facts that unexpectedly passed: {unexpectedly_passed}")
    print(f"  Correct facts that passed               : {correct_passed} / {len(CORRECT_FACTS)}")
    print(f"  Correct facts that failed               : {correct_failed}")
    print("=" * 72)

    if (failed_as_expected == len(FAILING_FACTS) and
            correct_passed == len(CORRECT_FACTS) and
            unexpectedly_passed == 0 and
            correct_failed == 0):
        print("RESULT: ALL CHECKS PASSED — validator behaves as expected.")
        return 0
    else:
        print("RESULT: SOME CHECKS FAILED — review the output above.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
