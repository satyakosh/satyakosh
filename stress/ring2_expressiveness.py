#!/usr/bin/env python3
"""Ring 2/3 expressiveness stress battery — pre-freeze dry-run.

The typed-union SHAPES (entity/date reserved types), the value grammar,
condition structure + tie-break, source-entry shape, canonicalization
rules, and the fact_id scheme all freeze at genesis. This battery
drafts representative Ring-2 and Ring-3 claims using the RESERVED
shapes and checks that the frozen machinery can carry them — without
activating anything.

HARD checks (exit 1 on failure — these are frozen surfaces):
  A. canonicalization of reserved shapes: deterministic, key-order-
     free, NFC-stable, condition sort + tie-break holds for
     entity/date-valued conditions
  B. identity semantics: precision/calendar/scoping distinctions yield
     distinct triple hashes (the conflict ladder depends on this)
  C. ASCII survival: every Ring-2 vocabulary sample (ISO 3166, BCP 47,
     ISO 8601 astronomical, InChI, UCUM) is pure ASCII in canonical
     form — the s7.2 tripwire survives Ring 2 activation
  D. refusal paths today: Ring-2/BLOCKED/attestation-shaped claims are
     refused by the CURRENT validator with citable errors

FINDINGS (reported, not failing): activation-era hazards and
decisions, each classified fix-now / additive-minor-later /
documented-limitation.

Run:  python3 stress/ring2_expressiveness.py
"""
import json
import random
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
import ledger as L


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


REG = {k: load(f"registries/{k}.json")
       for k in ("entities", "predicates", "sources")}
RS = {"mandatory_conditions": load("rulesets/mandatory_conditions.json"),
      "admissibility_map": load("rules/admissibility_map.json")}

HARD_FAILS = []
FINDINGS = []


def hard(name, ok, detail=""):
    print(("PASS" if ok else "FAIL"), "-", name, ("| " + detail if detail else ""))
    if not ok:
        HARD_FAILS.append(name)


def finding(sev, text):
    FINDINGS.append((sev, text))


def shuffled(d):
    items = list(d.items())
    random.Random(7).shuffle(items)
    return {k: (shuffled(v) if isinstance(v, dict) else v) for k, v in items}


# ------------------------------------------------------------------ shapes
DATE_DAY = {"type": "date", "value": "1947-08-15", "precision": "day",
            "calendar": "gregorian"}
DATE_YEAR = {"type": "date", "value": "1947", "precision": "year",
             "calendar": "gregorian"}
DATE_BCE = {"type": "date", "value": "-0562-01-01", "precision": "year",
            "calendar": "gregorian"}
DATE_JULIAN = {"type": "date", "value": "1642-12-25", "precision": "day",
               "calendar": "julian"}
ENT_ID = {"type": "entity", "id": "SK-ENT-000901"}
ENT_CODE = {"type": "entity", "standard": "iso3166-1a2", "code": "IN"}
Q = lambda v, u: {"type": "quantity", "value": v, "unit": u,
                  "exact": False, "uncertainty": None}


def triple(subj, pred, obj, conds=None):
    t = {"subject": subj, "predicate": pred, "object": obj,
         "conditions": conds or []}
    t["conditions"] = sorted(
        t["conditions"], key=lambda c: (c["property"], L.jcs(c["object"])))
    return t


# representative Ring-2/3 claims, reserved shapes only
CLAIMS = {
    "event date (day)": triple("SK-ENT-000001", "SK-PRED-000001", DATE_DAY),
    "event date (year)": triple("SK-ENT-000901", "SK-PRED-000002", DATE_YEAR),
    "event date (BCE, astronomical)": triple(
        "SK-ENT-000902", "SK-PRED-000002", DATE_BCE),
    "event date (julian calendar)": triple(
        "SK-ENT-000903", "SK-PRED-000002", DATE_JULIAN),
    "authorship (work -> person)": triple(
        "SK-ENT-000002", "SK-PRED-000001", ENT_ID),
    "ISO code assignment": triple(
        "SK-ENT-000905", "SK-PRED-000004", ENT_CODE),
    "census literacy (method + epoch conditions)": triple(
        "SK-ENT-000906", "SK-PRED-000001", Q("7.404e1", "%"),
        [{"property": "SK-ENT-000008", "object": ENT_ID},
         {"property": "SK-ENT-000907", "object": DATE_YEAR}]),
    "reference value (counting convention)": triple(
        "SK-ENT-000908", "SK-PRED-000001", Q("2.06e2", "1"),
        [{"property": "SK-ENT-000909", "object": ENT_ID}]),
    "jurisdiction-scoped claim": triple(
        "SK-ENT-000910", "SK-PRED-000001", Q("1.4e9", "1"),
        [{"property": "SK-ENT-000911", "object": ENT_CODE}]),
    "min/max range pair (same property, entity tie-break)": triple(
        "SK-ENT-000912", "SK-PRED-000001", Q("5e1", "Cel"),
        [{"property": "SK-ENT-000913", "object": ENT_ID},
         {"property": "SK-ENT-000913", "object": ENT_CODE}]),
    "ITS-90 as entity-valued condition (the Tier 3 case)": triple(
        "SK-ENT-000005", "SK-PRED-000001", Q("9.9974e1", "Cel"),
        [{"property": "SK-ENT-000006",
          "object": {"type": "quantity", "value": "1.01325e2", "unit": "kPa",
                     "exact": True, "uncertainty": None}},
         {"property": "SK-ENT-000007", "object": ENT_ID}]),
}


def main():
    print("=" * 68)
    print("A. Canonicalization of reserved shapes (frozen machinery)")
    print("=" * 68)
    for name, t in CLAIMS.items():
        try:
            h1 = L.triple_hash(t)
            h2 = L.triple_hash(shuffled(t))          # key order must not matter
            t_shuf = dict(t)
            t_shuf["conditions"] = list(reversed(t["conditions"]))
            h3 = L.triple_hash(t_shuf)               # condition order must not matter
            raw = L.jcs(L.canonical_triple(t))
            ascii_ok = all(b < 128 for b in raw)
            hard(f"A: {name}", h1 == h2 == h3 and ascii_ok,
                 f"hash {h1[:10]} stable; ascii={ascii_ok}")
        except Exception as e:  # noqa: BLE001
            hard(f"A: {name}", False, f"{type(e).__name__}: {e}")

    print("=" * 68)
    print("B. Identity semantics (the conflict ladder depends on these)")
    print("=" * 68)
    hard("B: day vs year precision are distinct triples",
         L.triple_hash(CLAIMS["event date (day)"]) !=
         L.triple_hash(CLAIMS["event date (year)"]))
    d_greg = triple("SK-ENT-000903", "SK-PRED-000002",
                    {**DATE_JULIAN, "calendar": "gregorian"})
    hard("B: julian vs gregorian calendar are distinct triples",
         L.triple_hash(CLAIMS["event date (julian calendar)"]) !=
         L.triple_hash(d_greg))
    hard("B: entity-by-id vs entity-by-code are distinct objects",
         L.jcs(ENT_ID) != L.jcs(ENT_CODE))
    hard("B: 12-char prefixes of all battery claims are collision-free",
         len({L.triple_hash(t)[:12] for t in CLAIMS.values()}) == len(CLAIMS))
    hard("B: ring-2 fact_id form parses",
         bool(L.FACT_ID_RE.match("SK-R2-HIST-" + "a1b2c3d4e5f6")))

    print("=" * 68)
    print("C. ASCII survival of Ring-2 vocabularies (s7.2 tripwire)")
    print("=" * 68)
    vocab = {"ISO 3166": "IN", "BCP 47": "hi-Deva-IN",
             "ISO 8601 astronomical": "-0562-01-01",
             "InChI": "InChI=1S/H2O/h1H2", "UCUM percent": "%",
             "UCUM year": "a", "calendar enum": "julian"}
    for name, s in vocab.items():
        hard(f"C: {name} is pure ASCII", s.isascii(), repr(s))

    print("=" * 68)
    print("D. Refusal paths under the CURRENT validator (must hold today)")
    print("=" * 68)

    def staged_ledger():
        g = load("genesis_record.draft.json")
        for k, v in list(g.items()):
            if isinstance(v, str) and "PLACEHOLDER" in v:
                g[k] = "e" * 64 if k.endswith("_hash") else "2026-07-18T00:00:00Z"
        led = L.Ledger(None, REG, RS)
        led.seal(g)
        return led

    def fact(t, ring=1, dtype="si_exact_definition"):
        th = L.triple_hash(t)
        return {"record_type": "fact", "fact_id": f"SK-R{ring}-HIST-{th[:12]}",
                "triple_hash": th, "version": 1, "supersedes": None,
                "triple": t, "ring": ring, "valid_from": None,
                "valid_until": None, "terminality": "none",
                "sources": [{"source": "SK-SRC-000001", "edition": "x",
                             "retrieved": "2026-07-01"}],
                "derivation": {"type": dtype, "script": None,
                               "derived_from": []},
                "process_hash": "a" * 64, "status": "sealed",
                "created": "2026-07-18T00:00:00Z"}

    refusals = [
        ("date-object fact refused (v1 quantity gate)",
         fact(CLAIMS["event date (day)"])),
        ("entity-object fact refused (v1 quantity gate)",
         fact(CLAIMS["authorship (work -> person)"])),
        ("ring-2 statistical fact refused (whitelist/admissibility)",
         fact(triple("SK-ENT-000001", "SK-PRED-000001", Q("7.404e1", "kPa")),
              ring=2, dtype="statistical_analysis")),
        ("institutional 'current PM'-shaped claim refused (BLOCKED)",
         fact(triple("SK-ENT-000001", "SK-PRED-000001", Q("1e0", "1")),
              dtype="institutional_declaration")),
        ("documentary evidence refused pre-Ring-2 (RING2_PENDING)",
         fact(triple("SK-ENT-000001", "SK-PRED-000001", Q("1e0", "1")),
              dtype="documentary_evidence")),
    ]
    for name, rec in refusals:
        led = staged_ledger()
        try:
            led.seal(rec)
            hard(f"D: {name}", False, "SEALED - refusal path missing")
        except L.ValidationError as e:
            hard(f"D: {name}", True, f"citable: {str(e)[:48]}")
        except Exception as e:  # noqa: BLE001
            hard(f"D: {name}", False, f"CRASH {type(e).__name__}")

    print("=" * 68)
    print("E. Activation-era probes -> findings")
    print("=" * 68)
    # E1: near-duplicate index vs unit-less objects
    led = L.Ledger(None, REG, RS)
    probe = {"record_type": "fact", "fact_id": "SK-R2-HIST-" + "0" * 12,
             "triple_hash": "0" * 64, "version": 1, "supersedes": None,
             "triple": CLAIMS["event date (day)"]}
    try:
        led._index(probe)
        print("  E1: _index tolerates a unit-less (date) object")
    except Exception as e:  # noqa: BLE001
        finding("FIX-NOW", f"Ledger._index crashes on unit-less objects "
                f"({type(e).__name__}) - near-dup key assumes "
                f"object.unit; guard to quantity objects before Ring 2")
        print(f"  E1: CONFIRMED - _index raises {type(e).__name__} on a "
              f"date-object fact")
    # E2: record-level date regex vs BCE
    if not L.DATE_RE.match("-0562-01-01"):
        finding("ADDITIVE-MINOR", "DATE_RE (record-level dates: valid_from/"
                "until, retrieved) cannot express BCE/astronomical years; "
                "the reserved date OBJECT spec allows them - the activation "
                "validator needs its own pattern (additive minor at Ring 2)")
        print("  E2: CONFIRMED - DATE_RE has no astronomical-year form")
    # E3: source edition strictness
    finding("ADDITIVE-MINOR", "SOURCE entries require non-empty edition; "
            "Ring-2 archival sources may have none. Admitting edition:null "
            "is a byte-affecting additive minor at activation - no "
            "pre-freeze action, but record the intent")
    print("  E3: noted - source edition strictness vs archival sources")
    # E4: precision ladder granularity
    finding("DOCUMENTED-LIMITATION", "precision enum (day|month|year|decade|"
            "century) has no 'range': a two-day source disagreement widens "
            "to month under the conflict ladder. Deliberate coarseness; "
            "revisit only if Ring 2 practice demands it (additive enum "
            "value via governance)")
    print("  E4: noted - two-day disagreements widen to month")
    # E5: UCUM whitelist coverage
    missing = [u for u in ("%", "a", "d") if u not in L.UCUM_V1]
    if missing:
        finding("BY-DESIGN", f"UCUM_V1 lacks Ring-2-likely codes {missing} - "
                f"the whitelist expands with proposals (FD-9); no freeze "
                f"impact")
        print(f"  E5: noted - UCUM whitelist will need {missing} at Ring 2")

    print("=" * 68)
    print(f"HARD: {'ALL PASS' if not HARD_FAILS else HARD_FAILS}")
    print(f"FINDINGS ({len(FINDINGS)}):")
    for sev, text in FINDINGS:
        print(f"  [{sev}] {text}")
    fixnow = [f for s, f in FINDINGS if s == "FIX-NOW"]
    return 1 if (HARD_FAILS or fixnow) else 0


if __name__ == "__main__":
    sys.exit(main())
