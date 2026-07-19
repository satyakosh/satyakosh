#!/usr/bin/env python3
"""Governance engine test suite (SCHEMA s10 / P9).

Exercises the witnessed-governance machinery end to end:
  - a full simulated Ring-2 activation (whitelist + rulesets + UCUM),
    proving a fact that the founding rules refuse SEALS after the
    activation governance record, and only after it;
  - the ASCII-tripwire narrowing dry-run the security review asked for
    (M4): a legitimate non-ASCII code is refused until an
    ascii_exemption record seals, then accepted;
  - rules-in-force resolution from the chain alone (reload reproduces
    state), and verify(full=True) replaying governance;
  - a negative battery: malformed / no-op / unknown-kind deltas refused
    with citable errors;
  - the issue #7 regression battery (G1-G5): tightening ruleset_change
    leaves history CLEAN under verify(full); garbage ruleset content
    refused at governance seal and citable if ever in force; genesis
    digests bind the provided artifacts; the inline whitelist is
    authoritative over the sources file; UCUM syntax + '<<' marker
    refusals.

Nothing here touches the real chain; all rulesets are synthetic. This
is a Genesis-Window review target: the governance FORMAT benefits from
adversarial review more than the code does.

Run:  python3 stress/test_governance.py
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


REG = {k: load(f"registries/{k}.json") for k in
       ("entities", "predicates", "sources")}
RS = {"mandatory_conditions": load("rulesets/mandatory_conditions.json"),
      "admissibility_map": load("rules/admissibility_map.json")}

RESULTS = []


def check(name, fn, expect_reject, expect_msg=""):
    try:
        fn()
        ok, actual = not expect_reject, "sealed/ok"
    except L.ValidationError as e:
        actual = f"reject: {str(e)[:60]}"
        ok = expect_reject and (expect_msg in str(e))
    except Exception as e:  # noqa: BLE001
        ok, actual = False, f"CRASH {type(e).__name__}: {str(e)[:48]}"
    RESULTS.append((ok, name, actual))


def note(name, ok, detail):
    RESULTS.append((ok, name, detail))


def genesis():
    g = load("genesis_record.draft.json")
    for k, v in list(g.items()):
        if isinstance(v, str) and "PLACEHOLDER" in v:
            g[k] = "e" * 64 if k.endswith("_hash") else "2026-07-19T00:00:00Z"
    # declared digests bind the provided artifacts (issue #7 G3)
    g["mandatory_conditions_hash"] = L.sha256_hex(
        L.jcs(RS["mandatory_conditions"]))
    g["admissibility_map_hash"] = L.sha256_hex(L.jcs(RS["admissibility_map"]))
    g["predicates_founding_hash"] = L.sha256_hex(L.jcs(REG["predicates"]))
    g["inscription"]["mission"] = "Governance test genesis."
    return g


def gov(kind, delta, eff="2026-08-01"):
    return {"record_type": "governance", "governance_kind": kind,
            "delta": delta, "effective_from": eff,
            "created": "2026-08-01T00:00:00Z"}


def fact(value="2.99792458e8", subject="SK-ENT-000001", unit="m/s",
         dtype="si_exact_definition", ring=1, conds=None, sources=None,
         edition_bytes=None):
    obj = {"type": "quantity", "value": value, "unit": unit,
           "exact": True, "uncertainty": None}
    triple = {"subject": subject, "predicate": "SK-PRED-000001",
              "object": obj, "conditions": conds or []}
    th = L.triple_hash(triple)
    src = sources or [{"source": "SK-SRC-000001",
                       "edition": edition_bytes or "x",
                       "retrieved": "2026-07-01"}]
    dom = "PHYS"
    return {"record_type": "fact", "fact_id": f"SK-R{ring}-{dom}-{th[:12]}",
            "triple_hash": th, "version": 1, "supersedes": None,
            "triple": triple, "ring": ring, "valid_from": None,
            "valid_until": None, "terminality": "none", "sources": src,
            "derivation": {"type": dtype, "script": None, "derived_from": []},
            "process_hash": "a" * 64, "status": "sealed",
            "created": "2026-08-02T00:00:00Z"}


def run():
    # ---------- Ring-2 activation, end to end ----------
    led = L.Ledger(None, REG, RS)
    led.seal(genesis())

    # a statistical fact with a % unit is refused under founding rules
    # (both admissibility RING-2 PENDING and % not in UCUM)
    stat = fact(value="7.404e1", subject="SK-ENT-000004", unit="%",
                dtype="statistical_analysis")
    check("Ring-2 statistical fact refused pre-activation",
          lambda: led.seal(stat), True)

    # activation bundle: three governance records seal in sequence
    # 1) admissibility: statistical_analysis SEAL at ring 2
    adm2 = copy.deepcopy(RS["admissibility_map"])
    adm2["map"]["statistical_analysis"]["ring_2"] = "SEAL"
    check("gov: admissibility ruleset_change seals",
          lambda: led.seal(gov("ruleset_change",
                                {"target": "admissibility_map",
                                 "content": adm2})), False)
    # 2) whitelist: a ring-2 source
    check("gov: whitelist add (ring 2 source) seals",
          lambda: led.seal(gov("whitelist_change",
                                {"add": [{"id": "SK-SRC-000004",
                                          "publisher": "Census Bureau",
                                          "rings": [2]}]})), False)
    # 3) UCUM: add %
    check("gov: ucum_expansion (%) seals",
          lambda: led.seal(gov("ucum_expansion", {"add_codes": ["%"]})), False)

    # now the same statistical fact SEALS at ring 2 with the ring-2 source
    # AND its founding-dormant method condition (SK-ENT-000008) present
    method_cond = [{"property": "SK-ENT-000008",
                    "object": {"type": "quantity", "value": "1e0",
                               "unit": "1", "exact": True,
                               "uncertainty": None}}]
    act = fact(value="7.404e1", subject="SK-ENT-000004", unit="%",
               dtype="statistical_analysis", ring=2, conds=method_cond,
               sources=[{"source": "SK-SRC-000004", "edition": "2011",
                         "retrieved": "2026-08-01"}])
    check("Ring-2 fact SEALS after activation (% unit, ring-2 source, method)",
          lambda: led.seal(act), False)

    # a ring-1 fact still cannot use the ring-2 source
    check("ring-1 fact still refused a ring-2-only source",
          lambda: led.seal(fact(value="5e0", sources=[
              {"source": "SK-SRC-000004", "edition": "x",
               "retrieved": "2026-08-01"}])), True, "ring 1")

    # ---------- rules-in-force resolves from the chain alone ----------
    import tempfile
    tmp = Path(tempfile.gettempdir()) / "gov_chain.json"
    led.path = tmp
    led.save()
    reloaded = L.Ledger(tmp, REG, RS)
    note("reload reproduces in-force UCUM", "%" in reloaded._ucum,
         f"% present: {'%' in reloaded._ucum}")
    note("reload reproduces whitelist", "SK-SRC-000004" in reloaded._whitelist,
         f"ring-2 source present: {'SK-SRC-000004' in reloaded._whitelist}")
    note("reload chain head matches", reloaded.chain_head() == led.chain_head(),
         "verified")
    note("verify(full) clean across governance",
         reloaded.verify(full=True) == [],
         f"{len(reloaded.verify(full=True))} findings")
    tmp.unlink()

    # ---------- ASCII-tripwire narrowing dry-run (review M4) ----------
    led2 = L.Ledger(None, REG, RS)
    led2.seal(genesis())
    # micro sign is a legitimate but non-ASCII code; refused by default
    check("non-ASCII unit refused before exemption (M4)",
          lambda: led2.seal(fact(value="1e0", unit="µm")),
          True, "UCUM")
    # the non-ASCII UCUM code cannot even be added until its char is
    # exempted — the tripwire is narrowed BEFORE the code needs it
    check("ucum add of non-ASCII code refused before char exemption",
          lambda: led2.seal(gov("ucum_expansion", {"add_codes": ["µm"]})),
          True, "not yet exempted")
    led2.seal(gov("ascii_exemption", {"exempt_chars": ["µ"]}))
    led2.seal(gov("ucum_expansion", {"add_codes": ["µm"]}))
    check("micro unit SEALS after exemption + UCUM add (M4 mechanism proven)",
          lambda: led2.seal(fact(value="3e0", unit="µm")), False)
    # an unrelated homoglyph is still tripped — exemption is per-character
    check("unexempted homoglyph still refused post-exemption",
          lambda: led2.seal(fact(value="4e0", edition_bytes="2011​")),
          True, "non-ASCII")

    # ---------- negative battery ----------
    led3 = L.Ledger(None, REG, RS)
    led3.seal(genesis())
    led3.seal(gov("ucum_expansion", {"add_codes": ["%"]}))
    check("neg: unknown governance_kind refused",
          lambda: led3.seal(gov("teleport", {"x": 1})), True, "governance_kind")
    check("neg: ucum re-add of in-force code refused (no no-ops)",
          lambda: led3.seal(gov("ucum_expansion", {"add_codes": ["%"]})),
          True, "already in force")
    check("neg: ucum non-ASCII code refused (char not exempted)",
          lambda: led3.seal(gov("ucum_expansion", {"add_codes": ["µ"]})),
          True, "not yet exempted")
    check("neg: whitelist remove of absent source refused",
          lambda: led3.seal(gov("whitelist_change",
                                 {"remove": ["SK-SRC-000009"]})),
          True, "not whitelisted")
    check("neg: whitelist add of existing source refused",
          lambda: led3.seal(gov("whitelist_change",
                                 {"add": [{"id": "SK-SRC-000001",
                                           "publisher": "x", "rings": [1]}]})),
          True, "already whitelisted")
    check("neg: ruleset_change with placeholder content refused",
          lambda: led3.seal(gov("ruleset_change",
                                 {"target": "mandatory_conditions",
                                  "content": {"subject_rules": [
                                      {"subject": "<SK-ENT: x>"}]}})),
          True, "placeholder")
    check("neg: bad effective_from refused",
          lambda: led3.seal(gov("ucum_expansion", {"add_codes": ["d"]},
                                eff="soon")), True, "effective_from")
    check("neg: unknown field in governance record refused",
          lambda: led3.seal({**gov("ucum_expansion", {"add_codes": ["d"]}),
                             "smuggled": 1}), True, "unknown field")
    check("neg: doc_supersession bad hash refused",
          lambda: led3.seal(gov("doc_supersession",
                                 {"document": "SCHEMA.md",
                                  "new_version": "1.1.0",
                                  "new_hash": "nothex"})), True, "new_hash")
    check("neg: empty delta refused",
          lambda: led3.seal(gov("ucum_expansion", {})), True, "non-empty")
    # positive: a well-formed doc_supersession seals
    check("doc_supersession (schema minor bump) seals",
          lambda: led3.seal(gov("doc_supersession",
                                 {"document": "SCHEMA.md",
                                  "new_version": "1.1.0",
                                  "new_hash": "a" * 64})), False)

    # ---------- issue #7 regression battery ----------
    # G1: a TIGHTENING ruleset_change must not retroactively condemn
    # history — verify(full) replays from the position-zero snapshot,
    # judging every record by the rules in force when it sealed
    led4 = L.Ledger(None, REG, RS)
    led4.seal(genesis())
    led4.seal(fact(value="6e0"))  # valid under founding rules
    tight = copy.deepcopy(RS["mandatory_conditions"])
    tight["subject_rules"] = list(tight.get("subject_rules", [])) + [
        {"subject": "SK-ENT-000001", "requires": ["SK-ENT-000006"],
         "rationale": "issue 7 G1 regression: a tightening change"}]
    led4.seal(gov("ruleset_change", {"target": "mandatory_conditions",
                                     "content": tight}))
    import tempfile as _tf
    tmp = Path(_tf.gettempdir()) / "gov_g1.json"
    led4.path = tmp
    led4.save()
    rl = L.Ledger(tmp, REG, RS)  # pristine founding files, real load path
    note("G1: tightening ruleset_change leaves history CLEAN",
         rl.verify(full=True) == [],
         f"{len(rl.verify(full=True))} findings")
    check("G1: NEW fact refused under the tightened rule in force",
          lambda: rl.seal(fact(value="7e0")), True, "required condition")
    tmp.unlink()

    # G2: garbage ruleset content refused at governance-seal time, and
    # a structurally broken in-force ruleset is citable, never a KeyError
    check("G2: garbage ruleset content refused at governance seal",
          lambda: led3.seal(gov("ruleset_change",
                                 {"target": "mandatory_conditions",
                                  "content": {"nonsense": 1}})),
          True, "unknown operative key")
    check("G2: ruleset without the indexed structure refused",
          lambda: led3.seal(gov("ruleset_change",
                                 {"target": "admissibility_map",
                                  "content": {"map": "not-an-object"}})),
          True, "map")
    check("G2: in-force garbage ruleset is citable, never a KeyError",
          lambda: L.validate_fact(
              fact(value="9e0"), REG,
              {"mandatory_conditions": {"nonsense": 1},
               "admissibility_map": RS["admissibility_map"]}),
          True, "structurally invalid")

    # G3: the genesis-declared digests bind the artifacts in force
    g_bad = genesis()
    g_bad["mandatory_conditions_hash"] = "f" * 64
    check("G3: genesis with wrong ruleset digest refused",
          lambda: L.Ledger(None, REG, RS).seal(g_bad),
          True, "does not match")
    led5 = L.Ledger(None, REG, RS)
    led5.seal(genesis())
    led5.seal(fact(value="8e0"))
    tmp2 = Path(_tf.gettempdir()) / "gov_g3.json"
    led5.path = tmp2
    led5.save()
    rs_t = copy.deepcopy(RS)
    rs_t["mandatory_conditions"]["subject_rules"] = []  # tampered file
    rt = L.Ledger(tmp2, REG, rs_t)
    note("G3: tampered ruleset file condemned by verify(full)",
         any("INVALID record 0" in f for f in rt.verify(full=True)),
         f"findings: {rt.verify(full=True)[:1]}")
    tmp2.unlink()

    # G4: the genesis inline whitelist is authoritative
    reg_x = copy.deepcopy(REG)
    reg_x["sources"]["sources"].append(
        {"id": "SK-SRC-000099", "publisher": "FileOnly", "rings": [1]})
    check("G4: sources file diverging from inline whitelist refused",
          lambda: L.Ledger(None, reg_x, RS).seal(genesis()),
          True, "diverges")
    led6 = L.Ledger(None, REG, RS)
    led6.seal(genesis())
    note("G4: in-force whitelist is the genesis inline enumeration",
         set(led6._whitelist) ==
         {e["id"] for e in genesis()["whitelist"]},
         f"{sorted(led6._whitelist)}")

    # G5: UCUM codes get a syntax check; '<<' markers never enter force
    check("G5: '<<TBD>>' code refused (placeholder marker in delta)",
          lambda: led3.seal(gov("ucum_expansion",
                                 {"add_codes": ["<<TBD>>"]})),
          True, "placeholder")
    check("G5: angle-bracket unit refused by UCUM syntax check",
          lambda: led3.seal(gov("ucum_expansion", {"add_codes": ["kg>"]})),
          True, "syntax")

    fails = sum(1 for ok, _, _ in RESULTS if not ok)
    w = max(len(n) for _, n, _ in RESULTS)
    for ok, name, actual in RESULTS:
        print(("PASS" if ok else "FAIL"), "-", name.ljust(w), "|", actual)
    print(f"\n{len(RESULTS) - fails}/{len(RESULTS)} cases passed")
    return fails == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
