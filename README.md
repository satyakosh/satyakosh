# Satyakosh (सत्यकोश) — a treasury of truth

A permanent, tamper-evident, hash-chained public ledger of verified facts.

AI systems increasingly decide what people read and believe, while the
internet they learn from degrades. Satyakosh is a neutral ground-truth
layer: every fact is sealed with cryptographic proof that it has not been
altered, plus full provenance and a runnable derivation recipe. Anyone can
verify any fact, forever, without trusting us.

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
| `genesis_record.draft.json` | Record zero, placeholders visible |
| `registries/` | Entity, predicate, source, and contributor registries |
| `rules/` | Machine-readable rulesets frozen by genesis hashes |
| `rulesets/` | Mandatory-condition rules (frozen by genesis hash) |
| `labels/` | Human-language renderings, freely correctable |

## Status

Pre-genesis. The chain is empty. The genesis record is drafted with
visible placeholders. The Genesis Window — a 30-day public adversarial
review — opens when the founding documents freeze.

## How to cite

Data in this repository is CC0: you may use it for anything, with no
permission needed. If you want to credit us, cite:

> Satyakosh: a tamper-evident public ledger of verified facts.
> https://satyakosh.org — fact IDs are permanent; cite the fact ID and
> the chain-head hash you verified against.

## Licenses

Data (ledger, registries, labels, proposals): CC0 1.0.
Code: Apache-2.0. See LICENSE-CC0 and LICENSE-APACHE.
