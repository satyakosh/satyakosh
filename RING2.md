# RING2.md — The public rulebook for Ring 2 (draft skeleton)

**Status: partially recovered.** Sections 6–9 are near-verbatim from the
2026-07-09 session transcript. Sections 1–5 are rebuilt from the session's
decision summary and must be re-reviewed by the founder. Nothing in this
document is sealed; that is the point — this is the one phase of Ring 2's
life in which every rule is still negotiable in public.

Ring 1 (independently re-derivable facts) is open. Ring 2 (documented
consensus) stays sealed-out until the rules below are locked and a
governance record opens each domain's door. This document is the plan and
the invitation.

## 1. Why the door is closed

Opening Ring 2 without written disagreement rules would make every refusal
a judgment call with the founder's name attached — and one arguable sealed
fact breaks the guarantee for all facts. The door opens domain by domain,
by witnessed governance record, only when the machinery below exists.

## 2. The record-scoped-claims doctrine (the core idea)

Ring 2 facts are sealed as claims about **what documented records say** —
"literacy rate *per the 2011 census method*," "the date whitelisted
archives agree on" — never as the ledger's opinion about the world. The
method and scope travel *inside* the fact as conditions. That is what lets
a neutral project hold history and statistics without taking a side.

## 3. Evidence rules per derivation type

- `documentary_evidence` — requires whitelisted archival sources; dates
  carry calendar and precision explicitly.
- **Conflict ladder for documentary date disagreements (three steps):**
  (1) reconcile calendars — many conflicts are Julian/Gregorian artifacts;
  (2) widen precision — seal at the precision level the sources agree on
  (year, not day); (3) if disagreement survives both: **don't seal.**
- `statistical_analysis` — requires a method condition (see the
  mandatory-conditions ruleset, encoded dormant since genesis) and a
  source that publishes its methodology.
- **Contested-attribution rule** ("who actually said this?") — an
  attribution seals only with a documented primary record; absence of
  contest is checked in review, and contested attributions stay in review.

## 4. Source admission criteria (S1–S7 for sources)

Seven criteria a source must pass to join a domain's whitelist — including
independence, published methodology, correction policy, archival
stability, and the **state-as-publisher doctrine**: a government agency
can be a *publisher of records* (a census bureau publishing its own
census) but never an *authority whose word makes things true*.

**[RECONSTRUCTION GAP: the lost original enumerated all seven criteria
individually. The list above names five recoverable ones; the founder or
a recovered copy of the original file must restore the exact seven before
this document is relied on. If the original proves unrecoverable, the
candidate re-derivations for the missing two (founder-endorsed
2026-07-17, pending final wording) are: institutional longevity — a
credible expectation that the source and its archives outlive a decade,
or a named successor of record; and stable citable editions — the source
publishes versioned, machine-accessible editions that can be pinned.]**

## 5. Candidate first domains

Final choice is demand-driven (D2). Current candidates, for argument:

- **External-standard code assignments** (ISO 3166 etc.) — lowest
  controversy; rides the existing standards-adoption governance; smallest
  evidence framework. The gentlest possible first door.
- **Provenance / authorship** — named by the July 2026 external review as
  the highest-value Ring 2 domain for AI grounding ("who actually said
  this?"); requires the contested-attribution rule in full.
- **Documented events / statistical aggregates** — heaviest frameworks;
  later doors.

## 6. Unlock conditions D1–D5

Each domain's door opens by one witnessed governance record, only after:

- **D1** — a minimum body of sealed Ring 1 facts demonstrates the pipeline
  in production (parameter P1).
- **D2** — demonstrated demand: the first domain is chosen by evidence of
  need, not taste (parameter P6).
- **D3** — this rulebook has survived a public review window (parameter
  P2) with reviewer quorum (parameter P3).
- **D4** — at least one design partner in writing (parameter P4).
- **D5** — domain viability: the domain has the minimum number of
  independent whitelisted institutions (parameter P7).

## 7. Ring 3 status

After the taxonomy work, most of what intuition files under "Ring 3"
(contested, time-varying) was rehomed: current-status → attestation layer;
causal/institutional → BLOCKED pending dedicated frameworks. No Ring 3
framework will be drafted before Ring 2 has demonstrated supersession and
dispute handling in production. Ring 3 is the horizon, not the roadmap.

## 8. Settled vs proposed vs open

| Item | Status |
|---|---|
| Triple structure; typed unions; canonical bytes | **Settled** (SCHEMA, frozen) |
| Ring 2 unlocks only `statistical_analysis` + `documentary_evidence` | **Settled** (admissibility map) |
| Causal/institutional stay BLOCKED; attestation boundary; SCOPE refusals | **Settled** |
| Witnessed-ruleset mechanism for mandatory conditions & whitelists | **Settled** (locks of 9 July 2026) |
| Record-scoped-claims doctrine (§2) | **Proposed here** (elaborates TAXONOMY) |
| Conflict ladder; contested-attribution rule; state doctrine; source criteria; D1–D5 | **Proposed here** |
| **P1** minimum sealed Ring 1 facts (proposed 50) | **Locked** (founder, 2026-07-17; contestable per §9) |
| **P2** rules review window (proposed ≥60 days) | **Locked** (founder, 2026-07-17; contestable per §9) |
| **P3** reviewer quorum (proposed ≥3, institutionally independent) | **Locked** (founder, 2026-07-17; contestable per §9) |
| **P4** design-partner threshold (proposed ≥1, in writing) | **Locked** (founder, 2026-07-17; contestable per §9) |
| **P5** Ring 2 fact dispute-window floor (proposed: same ≥30 days; domains may set longer, never shorter) | **Locked** (founder, 2026-07-17; contestable per §9) |
| **P6** first-domain selection rule (proposed: demand-driven per D2) | **Locked** (founder, 2026-07-17; contestable per §9) |
| **P7** domain-viability source minimum (proposed ≥2 institutions) | **Locked** (founder, 2026-07-17; contestable per §9) |

## 9. How to argue with this document (please do)

Open a GitHub issue or PR against `RING2.md`. Most wanted:

- **Adversarial examples** — a fact these rules would wrongly seal, or
  wrongly refuse. Breaking the rules now is the contribution; that is how
  the value grammar got fixed.
- **Source candidates** — nominate an institution for a domain whitelist
  with evidence against the source criteria.
- **Edge cases** — calendar and precision pathologies, contested
  attributions, entity-scoping traps.

Validated catches earn the same recognition as Genesis Window review.
Nothing here is sealed. That is precisely the point — this is the one
phase of Ring 2's life in which every rule is still negotiable in public,
and the chain will later witness that it was.
