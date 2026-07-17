#!/usr/bin/env python3
"""Mutation fuzzer for the intake validator.

Invariant under test: for ANY mutation of a record, Ledger.seal either
succeeds or raises a citable ValidationError. Any other exception is a
crash (an attacker-supplied proposal must never take the gate down),
and anything that seals must survive verify(full=True) replay.

This industrializes the manual adversarial pass of 2026-07-17 (which
found 17 gaps by hand-mutating fields): every run hand-mutates a few
thousand more. Deterministic: fixed seed unless one is passed.

Run:  python3 stress/fuzz_validator.py [trials] [seed]
"""
import copy
import json
import sys
from pathlib import Path
from random import Random

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "ledger"))
import ledger as L


def load(rel):
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


REG = {k: load(f"registries/{k}.json")
       for k in ("entities", "predicates", "sources")}
RS = {"mandatory_conditions": load("rulesets/mandatory_conditions.json"),
      "admissibility_map": load("rules/admissibility_map.json")}

JUNK = [None, True, False, 0, 1, -3, 1.0, -0.5, "", "x", "GARBAGE",
        "1e1", "0", "-1e-3", "sealed", "SK-ENT-000001", "a\ud800b",
        "m/ѕ", "e" * 64, [], {}, ["oops"], {"k": "v"}, 10**20]


def make_genesis():
    g = load("genesis_record.draft.json")
    for k, v in list(g.items()):
        if isinstance(v, str) and "PLACEHOLDER" in v:
            g[k] = "e" * 64 if k.endswith("_hash") else "2026-07-18T00:00:00Z"
    g["inscription"]["mission"] = "Fuzz-run synthetic genesis."
    return g


def make_fact(i):
    Q = {"type": "quantity", "value": "1.01325e2", "unit": "kPa",
         "exact": True, "uncertainty": None}
    conds = [] if i % 2 else sorted(
        [{"property": "SK-ENT-000006", "object": Q},
         {"property": "SK-ENT-000007", "object": Q}],
        key=lambda c: c["property"])
    subject = "SK-ENT-000001" if i % 2 else "SK-ENT-000005"
    dtype = "si_exact_definition" if i % 2 else "laboratory_measurement"
    triple = {"subject": subject, "predicate": "SK-PRED-000001",
              "object": {"type": "quantity", "value": f"1.{i:06d}e1",
                         "unit": "m/s", "exact": True, "uncertainty": None},
              "conditions": conds}
    th = L.triple_hash(triple)
    return {"record_type": "fact", "fact_id": f"SK-R1-PHYS-{th[:12]}",
            "triple_hash": th, "version": 1, "supersedes": None,
            "triple": triple, "ring": 1,
            "valid_from": None, "valid_until": None,
            "terminality": "none",
            "sources": [{"source": "SK-SRC-000001", "edition": "fuzz",
                         "retrieved": "2026-07-01"}],
            "derivation": {"type": dtype, "script": None,
                          "derived_from": []},
            "process_hash": "a" * 64, "status": "sealed",
            "created": "2026-07-18T00:00:00Z"}


def paths(obj, prefix=()):
    """All (container-path, key) pairs in a JSON tree."""
    out = []
    if len(prefix) > 12:  # belt against any residual structural sharing
        return out
    if isinstance(obj, dict):
        for k, v in obj.items():
            out.append((prefix, k))
            out.extend(paths(v, prefix + (k,)))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.append((prefix, i))
            out.extend(paths(v, prefix + (i,)))
    return out


def resolve(obj, prefix):
    for p in prefix:
        obj = obj[p]
    return obj


def mutate(rng, record):
    """Apply 1-3 random mutations; return the mutant."""
    m = copy.deepcopy(record)
    for _ in range(rng.randint(1, 3)):
        sites = paths(m)
        if not sites:
            break
        op = rng.randrange(5)
        prefix, key = rng.choice(sites)
        container = resolve(m, prefix)
        if op == 0:                      # delete
            del container[key]
        elif op == 1:                    # replace with junk
            container[key] = copy.deepcopy(rng.choice(JUNK))
        elif op == 2 and isinstance(container, dict):  # unknown key
            container["fuzz_" + str(rng.randrange(10))] = \
                copy.deepcopy(rng.choice(JUNK))
        elif op == 3 and isinstance(container.get(key)
                                    if isinstance(container, dict)
                                    else container[key], str):
            s = container[key]           # corrupt a string
            tweak = rng.choice(["+", "E", " ", "0", "ѕ", "​", "@1"])
            pos = rng.randrange(len(s) + 1)
            container[key] = s[:pos] + tweak + s[pos:]
        else:                            # swap two values
            p2, k2 = rng.choice(sites)
            a, b = prefix + (key,), p2 + (k2,)
            if a[:len(b)] == b or b[:len(a)] == a:
                continue  # never swap a node with its own ancestor/descendant
            c2 = resolve(m, p2)
            try:
                container[key], c2[k2] = c2[k2], container[key]
            except (KeyError, IndexError):
                pass
    return m


def fresh_ledger(genesis_records):
    led = L.Ledger(None, REG, RS)
    led.records = list(genesis_records)
    return led


def verifier_fuzz(rng, genesis_records, trials):
    """Second invariant: verify() must never RAISE. Build an honest
    chain, mutate a stored record arbitrarily, and assert verify()
    returns findings instead of crashing (auditing a hostile store is
    its whole job)."""
    base = fresh_ledger(genesis_records)
    for i in range(8):
        base.seal(make_fact(i))
    failures = 0
    for _ in range(trials):
        led = L.Ledger(None, REG, RS)
        led.records = [copy.deepcopy(r) for r in base.records]
        idx = rng.randrange(1, len(led.records))
        rec = led.records[idx]
        sites = paths(rec)
        prefix, key = rng.choice(sites)
        resolve(rec, prefix)[key] = copy.deepcopy(rng.choice(JUNK))
        try:
            led.verify()          # default mode must not raise
            led.verify(full=True)  # full mode must not raise
        except Exception as e:  # noqa: BLE001
            failures += 1
            print(f"  VERIFY RAISED on mutated record {idx}: "
                  f"{type(e).__name__}: {str(e)[:70]}")
    return failures


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 20260707
    rng = Random(seed)

    template = L.Ledger(None, REG, RS)
    template.seal(make_genesis())
    genesis_records = list(template.records)

    sealed = rejected = 0
    failures = []
    for i in range(trials):
        led = fresh_ledger(genesis_records)
        if i % 10 == 9:                  # 10%: fuzz the genesis path
            mutant = mutate(rng, make_genesis())
            led = L.Ledger(None, REG, RS)
        else:
            mutant = mutate(rng, make_fact(i))
        try:
            led.seal(mutant)
            sealed += 1
            replay = led.verify(full=True)
            if replay:
                failures.append(
                    (i, "SEALED-BUT-INVALID", str(replay[:1])))
        except L.ValidationError:
            rejected += 1
        except Exception as e:  # noqa: BLE001 - crashes are the quarry
            failures.append((i, type(e).__name__, str(e)[:90]))

    print(f"{trials} trials (seed {seed}): {sealed} sealed clean, "
          f"{rejected} citable rejections, {len(failures)} failures")
    for i, kind, detail in failures[:20]:
        print(f"  FAIL trial {i}: {kind}: {detail}")

    v_fail = verifier_fuzz(rng, genesis_records, trials // 2)
    print(f"verifier fuzz ({trials // 2} mutated stores): "
          f"{v_fail} raise-failures (verify() must only return findings)")
    if failures or v_fail:
        print(f"\nreproduce: python3 stress/fuzz_validator.py "
              f"{trials} {seed}")
    return 1 if (failures or v_fail) else 0


if __name__ == "__main__":
    sys.exit(main())
