# Satyakosh (सत्यकोश) — a treasury of truth

A permanent, tamper-evident, hash-chained public ledger of verified
facts — open source, end to end.

AI systems increasingly decide what people read and believe, while the
internet they learn from degrades. Satyakosh is a neutral ground-truth
layer: every fact is sealed with cryptographic proof that it has not been
altered, plus full provenance and a runnable derivation recipe. Anyone can
verify any fact, forever, without trusting us.

**What makes it different is checkable in one sentence:** every fact
seals together with the hash of its own adversarial review, and anyone
can verify the entire chain from a bare clone — no account, no API, no
trust in the maintainers. To our knowledge, it is the first
open-source ledger where a fact and the record of its review seal
together. Know prior art? Open an issue — refutations are the point
here.

*Not for a verdict, but to check.*

## Start here

| File | What it is |
|---|---|
| `MISSION.md` | Why this exists and the six principles |
| `SCHEMA.md` | The canonical specification of sealed records |
| `SCOPE.md` | What we refuse, and why (rules S1-S7) |
| `DECISIONS.md` | The founder decision register (FD-series, audit-trailed) |
| `verify.py` | Standalone chain verifier -- one file, stdlib only, independent of the engine |
| `PIPELINE_POLICY.md` | How a fact gets in (rules P1-P11) |
| `RING2.md` | The public rulebook for the next expansion |
| `CONTRIBUTING.md` | How to propose facts and catch errors |
| `chain.json` | **The chain** — the sealed ledger itself |
| `genesis_record.json` | Record zero as sealed (identical to `chain.json` record 0) |
| `registries/` | Entity, predicate, source, and contributor registries |
| `rules/` | Machine-readable rulesets frozen by genesis hashes |
| `rulesets/` | Mandatory-condition rules (frozen by genesis hash) |
| `labels/` | Human-language renderings, freely correctable |

## Status

**The chain is live.** Record 0 — the genesis record — sealed
2026-07-20T11:05:55Z with all six founding-document hashes bound and
verified by three independent implementations (the engine, the
standalone Python verifier, and the browser JavaScript verifier):

```
genesis content_hash  ebd533692e9bed7945cad78b2ae5e7dddc3f023061fe9eb01898cf5979100a0e
chain head            f3995a8fe67fc6adb949a99bd8bf146ced6a95c74881f0dd5910050aeebe4615
```

Check it yourself: `python verify.py chain.json --repo .` — or in a
browser at [satyakosh.org/verify.html](https://satyakosh.org/verify.html).
The **Genesis Window is open**: a 30-day public adversarial review
through which the first facts (the seven 2019 SI defining constants)
must pass, one pull request each, no exceptions — see
[CONTRIBUTING.md](CONTRIBUTING.md).

## How to cite

Data in this repository is CC0: you may use it for anything, with no
permission needed. If you want to credit us, cite:

> Satyakosh: a tamper-evident public ledger of verified facts.
> https://satyakosh.org — fact IDs are permanent; cite the fact ID and
> the chain-head hash you verified against.

## Licenses

Data (ledger, registries, labels, proposals): CC0 1.0.
Code: Apache-2.0. See LICENSE-CC0 and LICENSE-APACHE.
