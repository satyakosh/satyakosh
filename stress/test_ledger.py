#!/usr/bin/env python3
"""Deterministic test suite for ledger.py (SCHEMA s6/s8/s9/s11).

Includes the K-series: negative cases for every gap confirmed in the
2026-07-17 external adversarial review (duplicate-via-supersedes,
unvalidated fields, condition-value gaps, float divergence, etc.) so
none of them can silently reopen.

Positive-path cases run against the founding rulesets as committed.
Nothing here touches the real files.

Run:  python3 stress/test_ledger.py
"""
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
import ledger as L


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


REGISTRIES = {"entities": load("registries/entities.json"),
              "predicates": load("registries/predicates.json"),
              "sources": load("registries/sources.json")}
RAW_RULESETS = {"mandatory_conditions": load("rulesets/mandatory_conditions.json"),
                "admissibility_map": load("rules/admissibility_map.json")}


def rulesets():
    return copy.deepcopy(RAW_RULESETS)


def placeholder_rulesets():
    """Synthetic placeholder-bearing copy for the refusal test."""
    rs = rulesets()
    rs["mandatory_conditions"]["subject_rules"][0]["subject"] = \
        "<SK-ENT: boiling temperature of water>"
    return rs


def make_genesis():
    g = load("genesis_record.draft.json")
    for k, v in list(g.items()):
        if isinstance(v, str) and "PLACEHOLDER" in v:
            g[k] = "e" * 64 if k.endswith("_hash") else "2026-07-18T00:00:00Z"
    g["inscription"]["mission"] = "Test mission prose (synthetic genesis)."
    return g


def make_fact(value="2.99792458e8", subject="SK-ENT-000001", conds=None,
              dtype="si_exact_definition", **over):
    triple = {"subject": subject, "predicate": "SK-PRED-000001",
              "object": {"type": "quantity", "value": value, "unit": "m/s",
                         "exact": True, "uncertainty": None},
              "conditions": conds or []}
    rec = {"record_type": "fact", "fact_id": None,
           "triple_hash": None, "version": 1, "supersedes": None,
           "triple": triple, "ring": 1,
           "valid_from": None, "valid_until": None,
           "terminality": "none",
           "sources": [{"source": "SK-SRC-000001", "edition": "CODATA 2022",
                        "retrieved": "2026-07-01"}],
           "derivation": {"type": dtype, "script": None,
                          "derived_from": []},
           "process_hash": "a" * 64, "status": "sealed",
           "created": "2026-07-18T00:00:00Z"}
    rec.update(over)
    if rec["triple_hash"] is None:
        rec["triple_hash"] = L.triple_hash(rec["triple"])
    if rec["fact_id"] is None:
        rec["fact_id"] = f"SK-R1-PHYS-{rec['triple_hash'][:12]}"
    return rec


RESULTS = []


def check(name, fn, expect_reject, expect_msg=""):
    try:
        fn()
        ok, actual = not expect_reject, "sealed"
    except L.ValidationError as e:
        actual = f"reject: {str(e)[:64]}"
        ok = expect_reject and (expect_msg in str(e))
    except Exception as e:  # noqa: BLE001 - a crash is always a failure
        ok, actual = False, f"CRASH {type(e).__name__}: {str(e)[:50]}"
    RESULTS.append((ok, name, actual))


def run():
    led = L.Ledger(None, REGISTRIES, rulesets())

    # ---------------- chain bootstrap (SCHEMA s8/s9)
    check("fact as record 0 refused", lambda: led.seal(make_fact()),
          True, "record 0 must be genesis")
    check("genesis seals as record 0", lambda: led.seal(make_genesis()), False)
    check("valid fact seals after genesis", lambda: led.seal(make_fact()), False)
    g_bad = make_genesis()
    g_bad["created"] = "whenever"
    led_g = L.Ledger(None, REGISTRIES, rulesets())
    check("genesis with garbage created refused", lambda: led_g.seal(g_bad),
          True, "timestamp")
    g_noiso = make_genesis()
    g_noiso["inscription"]["founded"] = \
        "Ashadha Krishna Saptami, Vikram Samvat 2083"
    check("genesis founded without ISO anchor refused",
          lambda: L.Ledger(None, REGISTRIES, rulesets()).seal(g_noiso),
          True, "ISO")
    g_twoiso = make_genesis()
    g_twoiso["inscription"]["founded"] = "2026-07-07 or maybe 2026-07-08"
    check("genesis founded with two ISO dates refused",
          lambda: L.Ledger(None, REGISTRIES, rulesets()).seal(g_twoiso),
          True, "exactly one")

    # ---------------- duplicates & supersession (SCHEMA s6/s11)
    base_id = make_fact()["fact_id"]
    check("resealing same fact_id@version refused",
          lambda: led.seal(make_fact()), True, "already sealed")
    th16 = make_fact()["triple_hash"][:16]
    check("same triple under 16-hex fact_id refused (duplicate rule)",
          lambda: led.seal(make_fact(fact_id=f"SK-R1-PHYS-{th16}")),
          True, "duplicate triple_hash")
    check("K1: dup via self-referencing supersedes at version 1 refused",
          lambda: led.seal(make_fact(fact_id=f"SK-R1-PHYS-{th16}",
                                     supersedes=base_id + "@1")),
          True, "")
    check("supersedes nonexistent target refused",
          lambda: led.seal(make_fact(version=2,
                                     supersedes="SK-R1-PHYS-" + "0" * 12 + "@1")),
          True, "not on the chain")
    check("metadata supersession skipping versions refused",
          lambda: led.seal(make_fact(version=5, supersedes=base_id + "@1")),
          True, "increment version by exactly 1")
    check("metadata supersession v1->v2 allowed",
          lambda: led.seal(make_fact(version=2, supersedes=base_id + "@1")),
          False)
    check("double supersession of same version refused",
          lambda: led.seal(make_fact(version=2, supersedes=base_id + "@1")),
          True, "")
    check("superseding a non-latest version refused",
          lambda: led.seal(make_fact(version=3, supersedes=base_id + "@1")),
          True, "")
    check("metadata supersession v2->v3 allowed",
          lambda: led.seal(make_fact(version=3, supersedes=base_id + "@2")),
          False)
    check("fresh fact at version 2 without supersedes refused",
          lambda: led.seal(make_fact(value="4e0", version=2)),
          True, "starts at version 1")
    check("different triple still seals",
          lambda: led.seal(make_fact(value="1e0")), False)

    # ---------------- mandatory conditions (founding ruleset)
    Q = {"type": "quantity", "value": "1.01325e2", "unit": "kPa",
         "exact": True, "uncertainty": None}
    both = sorted([{"property": "SK-ENT-000006", "object": Q},
                   {"property": "SK-ENT-000007", "object": Q}],
                  key=lambda c: c["property"])
    check("boiling pt w/o conditions refused", lambda: led.seal(
        make_fact(subject="SK-ENT-000005", dtype="laboratory_measurement")),
        True, "required condition")
    check("boiling pt with both conditions seals", lambda: led.seal(
        make_fact(subject="SK-ENT-000005", conds=both,
                  dtype="laboratory_measurement")), False)

    # placeholder-bearing rulesets refuse every fact seal
    led_ph = L.Ledger(None, REGISTRIES, placeholder_rulesets())
    led_ph.records = led.records[:1]
    check("fact refused while ruleset has placeholders",
          lambda: led_ph.seal(make_fact()), True, "placeholder")

    # ---------------- K-series: field validation (external review 2026-07-17)
    def mutated(**over):
        return lambda: led.seal(make_fact(value="9.9e9", **over))

    check("K4: condition value 'GARBAGE' refused", lambda: led.seal(
        make_fact(value="5e0", subject="SK-ENT-000005",
                  dtype="laboratory_measurement",
                  conds=sorted([
                      {"property": "SK-ENT-000006",
                       "object": {"type": "quantity", "value": "GARBAGE",
                                  "unit": "kPa", "exact": True,
                                  "uncertainty": None}},
                      {"property": "SK-ENT-000007", "object": Q},
                  ], key=lambda c: c["property"]))), True, "grammar")
    Q2 = {"type": "quantity", "value": "1e0", "unit": "1",
          "exact": True, "uncertainty": None}
    check("K5: unregistered condition property refused", lambda: led.seal(
        make_fact(value="6e0",
                  conds=[{"property": "SK-ENT-999999", "object": Q2}])),
        True, "not in entity registry")
    check("K6: ring=1.0 gets citable rejection", mutated(ring=1.0),
          True, "integer")
    check("K6b: ring=2 (no whitelisted source) refused", mutated(ring=2),
          True, "")
    check("K7: garbage process_hash refused",
          mutated(process_hash="not-a-hash"), True, "process_hash")
    check("K8a: status='bogus' refused", mutated(status="bogus"),
          True, "status")
    check("K8b: version=-3 refused", mutated(version=-3), True, "version")
    check("K8c: terminality='maybe' refused", mutated(terminality="maybe"),
          True, "terminality")
    check("K8c2: unhashable terminality gets citable rejection (fuzz find)",
          mutated(terminality={"x": 1}), True, "terminality")
    check("K8d: valid_from='yesterday' refused",
          mutated(valid_from="yesterday"), True, "")
    check("K8e: inverted validity window refused",
          mutated(valid_from="2030-01-01", valid_until="2020-01-01"),
          True, "after")
    check("K9a: sources=[] refused", mutated(sources=[]), True, "non-empty")
    check("K8f: dated valid_until needs terminality=scheduled",
          mutated(valid_until="2030-01-01"), True, "scheduled")
    check("K8g: scheduled terminality with valid_until seals",
          lambda: led.seal(make_fact(value="9.91e9",
                                     valid_until="2030-01-01",
                                     terminality="scheduled")),
          False)
    check("K9b: source missing edition refused",
          mutated(sources=[{"source": "SK-SRC-000001",
                            "retrieved": "2026-07-01"}]), True, "")
    def bad_obj(**objover):
        obj = {"type": "quantity", "value": "9.8e9", "unit": "m/s",
               "exact": True, "uncertainty": None}
        obj.update(objover)
        t = {"subject": "SK-ENT-000001", "predicate": "SK-PRED-000001",
             "object": obj, "conditions": []}
        return lambda: led.seal(make_fact(
            triple=t, triple_hash=L.triple_hash(t),
            fact_id=f"SK-R1-PHYS-{L.triple_hash(t)[:12]}"))
    check("K10a: exact=true with uncertainty refused",
          bad_obj(uncertainty="1e-3"), True, "cannot carry uncertainty")
    check("K10b: negative uncertainty refused",
          bad_obj(exact=False, uncertainty="-1e-3"), True, "non-negative")
    check("K11a: float version refused", mutated(version=1.0),
          True, "integer")
    check("K11b: jcs() rejects floats anywhere", lambda: L.jcs({"x": [1.0]}),
          True, "float")
    check("K12: garbage fact_id prefix refused",
          mutated(fact_id="GARBAGE-abcdef123456"), True, "fact_id")
    check("K13: lone surrogate gets citable rejection",
          lambda: L.jcs({"x": "a\ud800b"}), True, "surrogate")
    check("K14: derived_from unknown fact refused",
          mutated(derivation={"type": "derived_exact", "script": None,
                              "derived_from": ["SK-R1-PHYS-" + "9" * 12]}),
          True, "unknown fact")
    check("K15: unit not in v1 UCUM whitelist refused",
          bad_obj(unit="not_a_unit!!"), True, "UCUM")
    check("unknown top-level field refused", mutated(extra="smuggled"),
          True, "unknown field")

    # ascii tripwire backstop: homoglyph in a free-text slot (edition)
    check("homoglyph in source edition trips ASCII guard", mutated(
        sources=[{"source": "SK-SRC-000001", "edition": "CODATA 2022ѕ",
                  "retrieved": "2026-07-01"}]), True, "non-ASCII")
    check("grammar: plain integer refused",
          lambda: led.seal(make_fact(value="299792458")), True, "grammar")
    check("blocked derivation refused",
          lambda: led.seal(make_fact(value="2e0", dtype="causal_inference")),
          True, "")
    check("unknown derivation refused",
          lambda: led.seal(make_fact(value="3e0",
                                     dtype="si_exact_defintion")), True, "")

    def bad_cond():
        f = make_fact(value="7e0")
        f["triple"]["conditions"] = ["oops"]
        led.seal(f)
    check("non-dict condition -> ValidationError", bad_cond,
          True, "malformed condition entry")

    # ---------------- issue #5 findings (F1-F4), pinned
    # FD-29: % is a Ring-2-corpus unit, not in the founding closed set;
    # refused now, added at Ring-2 activation by governance record.
    check("F1: percent unit refused (closed-by-default, FD-29)",
          lambda: led.seal(make_fact(value="7.404e1",
                                     triple={"subject": "SK-ENT-000002",
                                             "predicate": "SK-PRED-000001",
                                             "object": {"type": "quantity",
                                                        "value": "7.404e1",
                                                        "unit": "%",
                                                        "exact": False,
                                                        "uncertainty": None},
                                             "conditions": []},
                                     triple_hash=None, fact_id=None)),
          True, "UCUM")
    n_flags2 = len(led.flags)
    QA = {"type": "quantity", "value": "1e0", "unit": "kPa",
          "exact": True, "uncertainty": None}
    QB = {"type": "quantity", "value": "2e0", "unit": "kPa",
          "exact": True, "uncertainty": None}
    check("F2: duplicate-property conditions seal (s3.4 ranges)",
          lambda: led.seal(make_fact(value="8.1e1",
                                     conds=[{"property": "SK-ENT-000006",
                                             "object": QA},
                                            {"property": "SK-ENT-000006",
                                             "object": QB}])), False)
    RESULTS.append((len(led.flags) > n_flags2,
                    "F2: duplicate-property flag raised",
                    f"{len(led.flags) - n_flags2} new flag(s)"))
    rs_min = rulesets()
    rs_min["mandatory_conditions"]["source_count_rules"] = \
        {"si_exact_definition": 2}
    led_min = L.Ledger(None, REGISTRIES, rs_min)
    led_min.records = led.records[:1]
    check("F3: source_count_rules enforced (min 2, one given)",
          lambda: led_min.seal(make_fact(value="8.2e1")),
          True, "requires >= 2")
    check("F3b: source_count_rules satisfied with two distinct sources",
          lambda: led_min.seal(make_fact(value="8.3e1", sources=[
              {"source": "SK-SRC-000001", "edition": "x",
               "retrieved": "2026-07-01"},
              {"source": "SK-SRC-000002", "edition": "y",
               "retrieved": "2026-07-01"}])), False)
    # "same institution, two editions" is a repeated source ID, so it is
    # caught by the duplicate-entry rule before the distinct-count rule —
    # a source may appear at most once (issue #6, either way it fails)
    check("F5: same institution / two editions refused (issue #6)",
          lambda: led_min.seal(make_fact(value="8.31e1", sources=[
              {"source": "SK-SRC-000001", "edition": "2018",
               "retrieved": "2026-07-01"},
              {"source": "SK-SRC-000001", "edition": "2022",
               "retrieved": "2026-07-01"}])), True, "duplicate source")
    # the distinct-count rule proper: min 2 with genuinely distinct IDs
    # that a naive entry-count would pass — here one distinct source but
    # (hypothetically) padded is impossible now, so assert the positive:
    # exactly-min distinct sources seal, one-short (single) already fails
    # above (F3). Cross-check that min_src counts distinct IDs, not len:
    check("F5b: two distinct sources satisfy min-2 (distinct count)",
          lambda: led_min.seal(make_fact(value="8.33e1", sources=[
              {"source": "SK-SRC-000001", "edition": "a",
               "retrieved": "2026-07-01"},
              {"source": "SK-SRC-000003", "edition": "b",
               "retrieved": "2026-07-01"}])), False)
    check("F6: duplicate source entries refused (v1 hardening, issue #6)",
          lambda: led.seal(make_fact(value="8.32e1", sources=[
              {"source": "SK-SRC-000001", "edition": "x",
               "retrieved": "2026-07-01"},
              {"source": "SK-SRC-000001", "edition": "x",
               "retrieved": "2026-07-01"}])), True, "duplicate source")
    reg_ot = copy.deepcopy(REGISTRIES)
    reg_ot["predicates"]["predicates"].append(
        {"id": "SK-PRED-000009", "definition": "occurred on.",
         "object_types": ["date"], "epistemic_hedge": None,
         "status": "active", "labels": {"en": "occurred on"}})
    led_ot = L.Ledger(None, reg_ot, rulesets())
    led_ot.records = led.records[:1]
    check("F4: predicate object_types enforced",
          lambda: led_ot.seal(make_fact(value="8.4e1",
                                        triple={"subject": "SK-ENT-000001",
                                                "predicate": "SK-PRED-000009",
                                                "object": {"type": "quantity",
                                                           "value": "8.4e1",
                                                           "unit": "m/s",
                                                           "exact": True,
                                                           "uncertainty": None},
                                                "conditions": []},
                                        triple_hash=None, fact_id=None)),
          True, "admits object types")

    # ---------------- K16: near-duplicate flag (warn, never refuse)
    n_flags = len(led.flags)
    check("near-duplicate (same s+p+conds, different unit) still seals",
          lambda: led.seal(make_fact(value="8e0",
                                     triple={"subject": "SK-ENT-000001",
                                             "predicate": "SK-PRED-000001",
                                             "object": {"type": "quantity",
                                                        "value": "8e0",
                                                        "unit": "Hz",
                                                        "exact": True,
                                                        "uncertainty": None},
                                             "conditions": []},
                                     triple_hash=None, fact_id=None)), False)
    RESULTS.append((len(led.flags) == n_flags + 1,
                    "K16: near-duplicate flag raised",
                    f"{len(led.flags) - n_flags} new flag(s)"))

    # ---------------- K17/#3: verify(full=True) fraud-evidence
    RESULTS.append((led.verify(full=True) == [],
                    "verify(full) clean on honest chain", "0 findings"))
    # forge a structurally-hashed but semantically invalid record: the
    # plain tamper check must stay clean while full verify catches it
    forged = make_fact(value="6.6e6", sources=[])
    forged["prev_record_hash"] = led.records[-1]["content_hash"]
    forged["content_hash"] = L.content_hash(forged)
    led.records.append(forged)
    led._index(forged)
    plain, full = led.verify(), led.verify(full=True)
    RESULTS.append((plain == [] and any("INVALID" in f for f in full),
                    "K17: forged sourceless record invisible to hash check, "
                    "caught by verify(full)",
                    f"plain={len(plain)}, full={len(full)}"))
    led.records.pop()

    # ---------------- N-series: 2026-07-17 review round 2
    # N3/#3: verify() must REPORT, never RAISE, on a store the
    # canonicalizer chokes on (a stored float). The auditor's job is
    # hostile stores.
    ln = L.Ledger(None, REGISTRIES, rulesets())
    ln.seal(make_genesis()); ln.seal(make_fact(value="3.3e3"))
    ln.records[1]["version"] = 1.0  # inject a float post-seal
    try:
        fnd = ln.verify()
        RESULTS.append((any("CORRUPT" in f for f in fnd),
                        "N3: verify() reports (not raises) on stored float",
                        f"{len(fnd)} finding(s)"))
    except Exception as e:  # noqa: BLE001
        RESULTS.append((False, "N3: verify() reports (not raises) on float",
                        f"RAISED {type(e).__name__}"))
    ln.records[1]["version"] = 1

    # N2/#2 (FD-25): the 16-char fact_id form is deterministic — only on a
    # real 12-char collision, never a free choice.
    led_f = L.Ledger(None, REGISTRIES, rulesets())
    led_f.seal(make_genesis())
    g = make_fact(value="4.4e4")
    check("N2a: bare 16-char fact_id (no collision) refused",
          lambda: led_f.seal(make_fact(value="4.4e4",
              fact_id="SK-R1-PHYS-" + L.triple_hash(g["triple"])[:16])),
          True, "16-char fact_id form is only permitted")

    # N2b: a fully-retired triple (triple-changing supersession) cannot
    # re-enter — 12-char blocked by id reuse, 16-char blocked by FD-25.
    led_r = L.Ledger(None, REGISTRIES, rulesets())
    led_r.seal(make_genesis())
    a = make_fact(value="5.5e5"); led_r.seal(a)
    b = make_fact(value="6.6e6"); b["supersedes"] = a["fact_id"] + "@1"
    led_r.seal(b)  # triple-changing: retires a's triple entirely
    thA = a["triple_hash"]
    check("N2b-12: re-entry of retired triple (12-char) refused",
          lambda: led_r.seal(make_fact(value="5.5e5")), True, "already sealed")
    check("N2b-16: re-entry of retired triple (16-char) refused",
          lambda: led_r.seal(make_fact(value="5.5e5",
              fact_id="SK-R1-PHYS-" + thA[:16])),
          True, "16-char fact_id form is only permitted")

    # N8: derived_from a dead lineage seals but raises a liveness flag;
    # derived_from a metadata-superseded fact (still live at latest) does not.
    led_d = L.Ledger(None, REGISTRIES, rulesets())
    led_d.seal(make_genesis())
    p1 = make_fact(value="7.7e7"); led_d.seal(p1)
    p2 = make_fact(value="8.8e8"); p2["supersedes"] = p1["fact_id"] + "@1"
    led_d.seal(p2)  # p1's lineage now dead (triple-changing)
    nf = len(led_d.flags)
    check("N8: derived_from a dead lineage still seals",
          lambda: led_d.seal(make_fact(value="9.1e9",
              derivation={"type": "derived_exact", "script": None,
                          "derived_from": [p1["fact_id"]]})), False)
    RESULTS.append((len(led_d.flags) == nf + 1,
                    "N8: derived_from-liveness flag raised on dead lineage",
                    f"{len(led_d.flags) - nf} new flag(s)"))

    # ---------------- tamper detection
    led.records[1]["triple"]["object"]["value"] = "9e9"
    findings = led.verify()
    RESULTS.append((any("TAMPERED" in x for x in findings),
                    "tamper detection", f"{len(findings)} finding(s)"))

    fails = sum(1 for ok, _, _ in RESULTS if not ok)
    w = max(len(n) for _, n, _ in RESULTS)
    for ok, name, actual in RESULTS:
        print(("PASS" if ok else "FAIL"), "-", name.ljust(w), "|", actual)
    print(f"\n{len(RESULTS) - fails}/{len(RESULTS)} cases passed")
    return fails == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
