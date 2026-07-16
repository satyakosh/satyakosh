# PIPELINE_POLICY.md — How a fact gets in

**Status: RECONSTRUCTED from the locked decision record; rule numbering
P1-P10 preserved from the lost original's structure but wording must be
re-reviewed by the founder before this file is frozen and hashed for
genesis. P11 (batch proposals) is a new addition locked in the July 2026
genesis-design session — it must exist before the freeze. See
RECOVERY_NOTES.md.**

This document freezes at Genesis Window open. Its SHA-256 hash is sealed
in the genesis record. Every later change is a public governance record.

- **P1 — Anyone may propose.** Proposals arrive as GitHub pull requests
  using the fact-proposal template.
- **P2 — Machines annotate; they never veto.** Automated checks
  (whitelist, schema validation, mandatory conditions, duplicates) attach
  visible flags. "Publish under protest" means a proposal enters review
  over the machine's objection, with the objection visible — it never
  means bypassing review.
- **P3 — Intake gate.** A proposal that fails structural validation or is
  missing a mandatory condition never enters review. The rejection cites
  the exact rule (SCHEMA s11, SCOPE S1-S7, or the mandatory-conditions
  ruleset) — a principled, citable refusal.
- **P4 — Public review zone.** Every proposal that passes intake is
  publicly visible with all flags, regardless of check outcome.
- **P5 — Dispute window.** Minimum 30 days. Uniform in v1: no expedited
  lane (locked 2026-07-09). Anyone may object; objections are public.
- **P6 — Seal only after objections resolve.** Unresolved proposals remain
  in review indefinitely. They never seal and never disappear.
- **P7 — Review history is sealed with the fact.** Each sealed fact
  carries the SHA-256 of its complete review file (process_hash).
- **P8 — Contributors are pseudonymous on-chain.** Opaque SK-USR- IDs
  only; the name mapping is opt-in and deletable.
- **P9 — Rules in force are chain-determined.** Intake and seal-time
  checks resolve the ruleset at the record's chain position: genesis state
  plus all preceding governance records.
- **P10 — Genesis Window.** The first facts, including the founding seed
  set, pass through this full pipeline in public. Validated catches
  (errors, code flaws, canonical-form ambiguities) earn permanent sealed
  inscription. Adversarial review of all six frozen founding documents is
  in scope. A hash-breaking flaw restarts the window.
- **P11 — Batch proposals (mechanically ingested sets).** A batch of facts
  derived by one script from one pinned source edition may be proposed as
  a single batch proposal. The reviewed object is the batch: reviewers
  audit the ingestion script, the source pin, and spot-check facts; the
  machine annotation checks every row. Each fact in the batch still
  receives its own record, its own ID, and its own dispute window. A
  disputed fact holds in review individually while undisputed siblings
  seal. Founding use: the complete CODATA 2022 recommended values.
