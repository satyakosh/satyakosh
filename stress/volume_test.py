#!/usr/bin/env python3
"""Volume test — REBUILT implementation (the pre-2026-07-15 original was
lost; see RECOVERY_NOTES.md). Exercises the canonical-byte contract and
chain mechanics at ~9,000-record scale using synthetic facts:

  1. seal   — genesis + N unique facts through the real validation path
  2. verify — full-chain verification must return zero findings
  3. determinism — an independent second build from the same inputs must
     produce the identical chain head
  4. duplicates — re-sealing sampled records must be refused
  5. tamper sweep — K single-field mutations (value, prev link, triple)
     must each be detected by verify(), then restore cleanly
  6. save/load — ledger file round-trip preserves the chain head

Synthetic data only, validated against the founding rulesets as
committed; nothing here is ever proposed for real sealing. Fixed seed;
fixed timestamps; re-runs are byte-reproducible.

Run:  python3 stress/volume_test.py [N]          (default N=9000)
      python3 stress/volume_test.py --report     (also writes
                                                  stress/VOLUME_TEST_REPORT.md)
"""
import copy
import json
import platform
import random
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
import ledger as L

SEED = 20260707
N_DEFAULT = 9000
TAMPER_TRIALS = 30
CREATED = "2026-07-18T00:00:00Z"


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def resolved_rulesets():
    """The founding rulesets as committed (entity IDs founder-confirmed
    2026-07-17; placeholder-free)."""
    return {"mandatory_conditions": load("rulesets/mandatory_conditions.json"),
            "admissibility_map": load("rules/admissibility_map.json")}


def make_genesis():
    g = load("genesis_record.json")
    for k, v in list(g.items()):
        if isinstance(v, str) and "PLACEHOLDER" in v:
            g[k] = "e" * 64 if k.endswith("_hash") else CREATED
    # declared digests bind the provided artifacts (issue #7 G3)
    g["mandatory_conditions_hash"] = L.sha256_hex(
        L.jcs(load("rulesets/mandatory_conditions.json")))
    g["admissibility_map_hash"] = L.sha256_hex(L.jcs(load("rules/admissibility_map.json")))
    g["predicates_founding_hash"] = L.sha256_hex(L.jcs(load("registries/predicates.json")))
    g["inscription"]["mission"] = "Synthetic genesis for the volume test."
    return g


SUBJECTS = ["SK-ENT-000001", "SK-ENT-000002", "SK-ENT-000003",
            "SK-ENT-000004", "SK-ENT-000009", "SK-ENT-000010",
            "SK-ENT-000011", "SK-ENT-000012"]
UNITS = ["m/s", "J.s", "kPa", "1", "Hz", "C", "J/K", "mol-1"]
COND_Q = {"type": "quantity", "value": "1.01325e2", "unit": "kPa",
          "exact": True, "uncertainty": None}
BOTH_CONDS = sorted(
    [{"property": "SK-ENT-000006", "object": COND_Q},
     {"property": "SK-ENT-000007", "object": COND_Q}],
    key=lambda c: c["property"])


def make_fact(i):
    """Deterministic unique fact #i. Every ~40th fact is condition-bearing."""
    if i % 40 == 0:
        subject, dtype, conds = "SK-ENT-000005", "laboratory_measurement", BOTH_CONDS
        exact, unc = False, "1e-3"
    else:
        subject = SUBJECTS[i % len(SUBJECTS)]
        dtype, conds, exact, unc = "si_exact_definition", [], True, None
    value = f"{1 + i % 9}.{i:07d}e{i % 300}"  # unique mantissa per i
    triple = {"subject": subject, "predicate": "SK-PRED-000001",
              "object": {"type": "quantity", "value": value,
                         "unit": UNITS[i % len(UNITS)],
                         "exact": exact, "uncertainty": unc},
              "conditions": conds}
    th = L.triple_hash(triple)
    return {"record_type": "fact", "fact_id": f"SK-R1-PHYS-{th[:12]}",
            "triple_hash": th, "version": 1, "supersedes": None,
            "triple": triple, "ring": 1,
            "valid_from": None, "valid_until": None,
            "terminality": "none",
            "sources": [{"source": "SK-SRC-000001",
                         "edition": "synthetic", "retrieved": "2026-07-18"}],
            "derivation": {"type": dtype, "script": None,
                          "derived_from": []},
            "process_hash": "b" * 64, "status": "sealed",
            "created": CREATED}


def build_chain(n, path):
    led = L.Ledger(path, {"entities": load("registries/entities.json"),
                          "predicates": load("registries/predicates.json"),
                          "sources": load("registries/sources.json")},
                   resolved_rulesets())
    led.seal(make_genesis())
    t0 = time.perf_counter()
    for i in range(n):
        led.seal(make_fact(i))
    return led, time.perf_counter() - t0


def main():
    args = [a for a in sys.argv[1:] if a != "--report"]
    write_report = "--report" in sys.argv[1:]
    n = int(args[0]) if args else N_DEFAULT
    rng = random.Random(SEED)
    cache = REPO / ".cache"
    cache.mkdir(exist_ok=True)
    for stale in ("volume_ledger.json", "volume_ledger_2.json"):
        (cache / stale).unlink(missing_ok=True)
    results, ok = [], True

    def record(name, passed, detail):
        nonlocal ok
        ok = ok and passed
        results.append((passed, name, detail))
        print(("PASS" if passed else "FAIL"), "-", name, "|", detail)

    # 1. seal
    led, seal_s = build_chain(n, cache / "volume_ledger.json")
    record("seal", len(led.records) == n + 1,
           f"{n} facts + genesis in {seal_s:.1f}s "
           f"({n / seal_s:.0f} seals/s)")

    # 2. verify (tamper-evidence), then full replay (fraud-evidence)
    t0 = time.perf_counter()
    findings = led.verify()
    verify_s = time.perf_counter() - t0
    record("verify clean chain", not findings,
           f"0 findings expected, got {len(findings)} in {verify_s:.1f}s")
    t0 = time.perf_counter()
    full_findings = led.verify(full=True)
    full_s = time.perf_counter() - t0
    record("verify(full) seal-time replay", not full_findings,
           f"0 findings expected, got {len(full_findings)} in {full_s:.1f}s")
    record("no near-duplicate flags", not led.flags,
           f"{len(led.flags)} flag(s)")
    head = led.chain_head()

    # 3. determinism — independent rebuild, same inputs
    led2, _ = build_chain(n, cache / "volume_ledger_2.json")
    record("deterministic chain head", led2.chain_head() == head,
           head[:16] + "...")

    # 4. duplicates refused
    dup_refused = 0
    for i in rng.sample(range(n), 20):
        try:
            led.seal(make_fact(i))
        except L.ValidationError:
            dup_refused += 1
    record("duplicate refusal", dup_refused == 20, f"{dup_refused}/20 refused")

    # 5. tamper sweep — every single-field mutation must be detected
    detected = 0
    for _ in range(TAMPER_TRIALS):
        idx = rng.randrange(1, len(led.records))
        rec = led.records[idx]
        field = rng.choice(["value", "prev", "created"])
        if field == "value":
            saved = rec["triple"]["object"]["value"]
            rec["triple"]["object"]["value"] = "8.8888888e88"
        elif field == "prev":
            saved = rec["prev_record_hash"]
            rec["prev_record_hash"] = "f" * 64
        else:
            saved = rec["created"]
            rec["created"] = "2001-01-01T00:00:00Z"
        if led.verify():
            detected += 1
        if field == "value":
            rec["triple"]["object"]["value"] = saved
        elif field == "prev":
            rec["prev_record_hash"] = saved
        else:
            rec["created"] = saved
    record("tamper detection", detected == TAMPER_TRIALS,
           f"{detected}/{TAMPER_TRIALS} single-field mutations detected")
    record("chain intact after restore",
           not led.verify() and led.chain_head() == head, "verified")

    # 6. save/load round-trip
    led.save()
    led3 = L.Ledger(led.path, led.registries, led.rulesets)
    size_mb = led.path.stat().st_size / 1e6
    record("save/load round-trip",
           led3.chain_head() == head and not led3.verify(),
           f"{size_mb:.1f} MB ledger file")

    print(f"\n{'ALL PASS' if ok else 'FAILURES PRESENT'} "
          f"({len(results)} checks, N={n})")

    if write_report:
        lines = [
            "# Volume test report (rebuilt implementation)", "",
            "The pre-2026-07-15 report was lost with the original working",
            "copy; this report supersedes it and describes the rebuilt test",
            "(stress/volume_test.py). Synthetic data only, validated",
            "against the founding rulesets as committed (entity IDs",
            "founder-confirmed 2026-07-17).", "",
            f"- Date: 2026-07-17 · Python {platform.python_version()} "
            f"on {platform.system()}",
            f"- Scale: {n} facts + 1 genesis record, fixed seed {SEED}", "",
            "| Check | Result | Detail |", "|---|---|---|"]
        lines += [f"| {name} | {'PASS' if p else 'FAIL'} | {d} |"
                  for p, name, d in results]
        lines += ["",
                  f"Synthetic chain head: `{head}`", "",
                  "Re-run: `python3 stress/volume_test.py --report` "
                  "(byte-reproducible).", ""]
        (REPO / "stress" / "VOLUME_TEST_REPORT.md").write_text(
            "\n".join(lines), encoding="utf-8")
        print("report written to stress/VOLUME_TEST_REPORT.md")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
