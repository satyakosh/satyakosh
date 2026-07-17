# Satyakosh — Pipeline Policy (version 1.0.0)

> *Restored 2026-07-17 from the recovered 2026-07-10 original (pre-loss bytes; see RECOVERY_NOTES.md and docs/rebuild_divergence_report.md); amendments A8 (P11) and A9 re-applied.*


This document is the binding rulebook of the fact-addition pipeline. The
genesis record enumerates this document's SHA-256 hash; after genesis,
changes happen only through `governance` records (machine-readable delta
plus effective-from date).

Plain-English walkthrough for contributors: `CONTRIBUTING.md`. If the two
documents ever disagree, this one wins.

---

## P1 — Open proposal

Anyone may propose a fact by opening a pull request that adds a proposal
file under `proposals/`. No account standing, affiliation, or permission
is required beyond a GitHub account.

## P2 — Intake check (structure and scope)

A proposal must pass structural validation (SCHEMA.md §11) and the intake
questionnaire (TAXONOMY.md) before it enters review:

- Its `derivation.type` must map to an admissible verdict for the current
  ring under the admissibility map in force at the current chain position.
- All mandatory conditions for its class must be present.
- Scope refusals must cite a rule ID from SCOPE.md.

A proposal refused at intake is closed with the citable reason. Refusal at
intake is about structure and scope only — never about whether the claim
is believed.

## P3 — Automated source check: annotate, never veto

The automated checker compares the proposal's sources against the
whitelist in force at the current chain position and re-runs any
derivation script. Its findings are posted publicly on the proposal.

**The machine holds no veto.** A proposer may move a machine-flagged
proposal into review; the flag stays permanently visible on the proposal
("publish under protest"). Protest publishes the disagreement — it never
bypasses review.

## P4 — Public review window

Every proposal that enters review stays open for public objection for at
least **30 calendar days**. Anyone may object. Objections are public,
threaded on the proposal, and never deleted.

## P5 — Resolution before sealing

A proposal may seal only when:

1. its review window has completed (≥30 days), and
2. every objection raised is resolved — answered to the objector's
   withdrawal, or closed with a written public resolution, and
3. for `derived_exact` proposals, every fact listed in `derived_from` is
   already sealed, and
4. the frozen review file's SHA-256 matches the `process_hash` to be
   sealed.

## P6 — Sealing

Sealing writes the fact record to the chain (SCHEMA.md §8). The frozen
review file is retained permanently; its hash inside the sealed record
makes the review history tamper-evident.

## P7 — Unresolved proposals never seal, never disappear

A proposal with unresolved objections, or one that never passes
verification, remains in the public review zone indefinitely. It is never
sealed and never deleted. The review zone is part of the public record.

## P8 — Contributor identity

Contributors appear in frozen review files only as opaque `SK-USR-` IDs.
The ID-to-name map is a separate, unsealed, opt-in registry and is
erasable on request. No name, handle, or contact detail ever enters
anything hashed.

## P9 — Corrections

Sealed records are never edited. A correction is a new proposal that
passes this full pipeline and, on sealing, marks the old record
`superseded` via the `supersedes` field. Supersession may cross fact IDs
when the canonical triple itself changes (for example, a CODATA revision).

## P10 — The Genesis Window

The founding launch period is called the Genesis Window. During it:

1. The seed proposals pass through this pipeline in public — P1 through
   P6 apply in full, with no shortcuts for the founder.
2. Adversarial review of all six frozen founding documents — the
   schema, this policy, the scope rules, the admissibility map, the
   mandatory-conditions map, the predicate snapshot — and of the code
   is in scope (amendment A9). A hash-breaking flaw is fixed and restarts the window;
   cosmetic findings queue for the next minor version.
3. Validated catches (errors, code flaws, canonical-form ambiguities) are
   scored publicly. At window close, the scoreboard seals as an
   `inscription` record. Contributors appear as `SK-USR-` IDs; inclusion
   is opt-in.

Window mechanics (scoring detail, duration beyond the 30-day minimum) are
operational and may be tuned during the window; the rules P1–P9 may not.

## P11 — Batch proposals (mechanically ingested sets)

A batch of facts derived by one script from one pinned source edition
may be proposed as a single batch proposal. The reviewed object is the
batch: reviewers audit the ingestion script, the source pin, and
spot-check facts; the automated checker checks every row. Each fact in
the batch still receives its own record, its own ID, and its own
dispute window (each with its own review file referencing the shared
batch review). A disputed fact holds in review individually while
undisputed siblings seal. Founding use: the complete CODATA 2022
recommended values. *(Amendment A8, locked July 2026.)*
