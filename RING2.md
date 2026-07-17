# Satyakosh — Ring 2 Framework (Public Draft)
### Status: DRAFT rc1 · unsealed · published for public review · 9 July 2026
### Repo path: `RING2.md` (root, beside SCOPE.md)

> *Restored 2026-07-17 from the recovered 2026-07-09 original (pre-loss bytes; see RECOVERY_NOTES.md); founder parameter locks FD-19 applied to s8.*

**What this document is:** the rulebook-in-progress for the next class of
facts. Ring 2 is locked today not because the room is missing — the schema
already holds `entity` and `date` objects in reserve — but because the
rules for handling disagreement about history, statistics, and authorship
are not written. This document writes them, in public, while no fact is at
risk. Argue with the rules now; the facts come later.

**What this document is not:** it is not SCHEMA, it changes zero canonical
bytes, and nothing in it binds. When a domain actually opens, the *final*
version of its evidence framework and source whitelist are hashed into an
activation `governance` record — the same draft → resolve → witness path
`rulesets/mandatory_conditions.json` followed. Until that record seals,
everything below is correctable prose.

---

## 1. What Ring 2 is — and is not

Ring 2 admits facts established by **documented consensus** rather than
independent re-derivation: documented historical events, statistical
aggregates, provenance/authorship, biological and medical reference
values, definitional code assignments, and stable jurisdictional
assignments (TAXONOMY: the RING-2 PENDING table).

Ring 2 is **not**:

- **Causal or institutional claims.** `causal_inference` and
  `institutional_declaration` stay BLOCKED; each needs its own framework.
  Ring 2 opening changes nothing for them.
- **Current status.** "Who is PM now," known-counts, empirical negatives —
  attestation layer, never sealed, unchanged.
- **Out-of-scope categories.** SCOPE.md refusals (rules, fiction, lexicon,
  feeds, identity, self-reference) survive Ring 2 untouched.
- **A lower bar.** Same triple structure, same canonical bytes, same open
  pipeline, same annotate-never-veto source check, same dispute-window
  floor (§8, P5). Ring 2 raises the *evidence* requirements; it never
  relaxes the *process*.

## 2. The doctrine: record-scoped claims

The single idea that makes Ring 2 sealable at all:

> **Ring 2 facts seal as scoped claims about what documented processes and
> records establish — never as bare world-truths the ledger personally
> vouches for.**

The scoping is carried by machinery that already exists: conditions
(method, jurisdiction, reference population, calendar), sources (which
record), and predicate definitions (which carry any epistemic hedge — a
documentary predicate says so in its registry definition; the triple never
launders a hedged claim into a flat one, SCHEMA §3.2).

Concretely: the ledger does not seal "literacy in India is 74.04%." It
seals "literacy rate **per the 2011 census methodology** = 7.404e1 %" —
the method is inside the claim. It does not adjudicate history; it
witnesses that whitelisted documentary chains converge on 1947-08-15. The
difference is what lets a neutral trust anchor hold contested-adjacent
domains without taking sides.

## 3. Evidence framework (draft)

### 3.1 `statistical_analysis`

Two claim shapes, two rules:

- **World-quantities independently measurable** (e.g., a physical-anatomy
  reference value): **≥2 independent whitelisted sources** agreeing within
  stated uncertainty; reference-population and counting-convention
  conditions mandatory (TAXONOMY).
- **Record-scoped quantities** (e.g., a census figure — there is only one
  2011 census): the documented process is part of the claim via the
  mandatory **method condition**; the source requirement becomes primary
  publication on the whitelist **plus independent archival verification**
  that the record says what the proposal says it says. Independence
  applies to *verifying the record*, not to re-running a census.

Value/uncertainty transcription rules are Ring 1's, unchanged (§7.3
grammar is frozen bytes).

### 3.2 `documentary_evidence`

**Documented events (dates).** Where whitelisted sources disagree, a
three-step ladder — and only the ladder:

1. **Calendar reconciliation.** If the disagreement is a calendar artifact
   (Julian vs Gregorian), convert deterministically; the sealed `date`
   object's `calendar` field and labels record the reconciliation.
2. **Precision widening.** If sources agree at a coarser precision (year,
   not day), seal at the **coarsest precision all whitelisted sources
   support** — the `precision` field exists exactly for this.
3. **No seal.** If conflict survives steps 1–2, the claim stays in public
   review with the conflict documented. It never disappears and never
   seals. *The ledger witnesses consensus; it never casts the deciding
   vote.*

**Provenance / attribution.** Seals only when whitelisted scholarship
shows **stable consensus**; the predicate definition carries the hedge
("documentary-consensus attribution"). A live scholarly dispute in
whitelisted sources = stays in review. If consensus later shifts, the
correction is a supersession — the old record is superseded, never erased,
and the chain honestly witnesses that scholarship moved.

### 3.3 Draft mandatory-condition additions
(merged into the witnessed mandatory-conditions ruleset by the activation
governance record — the second-lock mechanism, unchanged)

| Claim class | Mandatory conditions |
|---|---|
| Statistical aggregate | method; reference population; epoch where applicable |
| Biological/medical reference value | reference population; counting convention |
| Jurisdictional assignment | jurisdiction (ISO 3166 entity condition) |
| Documented event date | calendar condition whenever non-Gregorian ambiguity exists |

### 3.4 Draft predicate additions
(registered at activation via governance; definitions carry their hedges)

`occurred_on` (event → date) · `authored_by` (work → entity;
documentary-consensus hedge) · `is_assigned_code` (entity → entity via
`standard`+`code`) · `instance_of` (already anticipated, SCHEMA §3.2).

### 3.5 Entity scoping

Ring 2 makes entity scoping load-bearing ("India" — the Republic? British
India? the subcontinent?). Rules: Ring 2 subject entities require scoping
review at registration; distinct temporal or legal scopes are **distinct
entities** linked by registry relations, never one elastic entity; scoping
text lives in the registry description (unsealed, correctable — SCHEMA
§5), but a fact's *identity* binds to the entity ID, so scoping disputes
are registry work, not chain surgery.

## 4. Source admission criteria (per-domain whitelists)

A source enters a domain whitelist only if it satisfies all of:

- **S1 — Primary.** Publisher of the record itself, never an aggregator.
- **S2 — Versioned.** Published, stable, citable editions (the CODATA
  property, generalized).
- **S3 — Transparent.** Methodology public.
- **S4 — Durable.** Institutional permanence, or third-party archival
  guarantee (Internet Archive / Zenodo class).
- **S5 — Language-neutral citability.** IDs and editions, not prose.
- **S6 — Independence audit.** The publisher's incentives relative to the
  claims it would ground are assessed and documented. **The state doctrine:
  a state statistical agency is admissible as the publisher of a
  documented process** (census, survey — method-as-condition mandatory),
  **never as an authority whose declaration constitutes the fact** — that
  is `institutional_declaration`, and it stays BLOCKED. Publisher of
  record: yes. Oracle: never.
- **S7 — Domain viability.** A domain opens only when its whitelist holds
  **≥2 independent institutions** [P7] — a one-source domain is a
  single-point-of-capture domain.

Whitelist membership changes remain governance records, exactly as in
Ring 1. Each domain's whitelist is a separate ruleset artifact hashed at
that domain's activation.

## 5. The door: unlock conditions

Ring 2 opens **per domain**, never wholesale. A domain's door opens when
all five hold:

| # | Condition | Proposed parameter |
|---|---|---|
| **D1** | Genesis Window closed clean **and** the Ring 1 pipeline has sealed real facts through the full process in production | ≥50 sealed facts [P1] |
| **D2** | Demand is external and named: at least one committed design partner requests this domain in writing | ≥1 partner [P4] |
| **D3** | The domain's evidence framework + source whitelist are drafted, published, and have survived their own public review window with all objections resolved — **rules face the same scrutiny facts do** | ≥60-day rules window [P2] |
| **D4** | Reviewer capacity exists: independent domain reviewers registered with `SK-USR-` IDs, no two from the same institution | ≥3 reviewers [P3] |
| **D5** | The activation itself seals as **one governance record**: domain identifier; evidence-framework hash; domain-whitelist hash; mandatory-condition ruleset delta; new predicate registrations; object-type activation; effective-from | — |

Schema note: the first activation that enables `entity`/`date` objects is
an additive minor version — the natural **v2.2** — announced via the same
governance record, per the codified versioning rule. Old hashes untouched,
by construction.

## 6. Candidate first domains

Final choice is demand-driven (D2). Current candidates, for argument:

- **External-standard code assignments** (ISO 3166 etc.) — lowest
  controversy; rides the existing standards-adoption governance; smallest
  evidence framework. The gentlest possible first door.
- **Provenance / authorship** — named by the July 2026 external review as
  the highest-value Ring 2 domain for AI grounding ("who actually said
  this?"); requires the §3.2 contested-attribution rule in full.
- **Documented events / statistical aggregates** — heaviest frameworks;
  later doors.

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
| Conflict ladder; contested-attribution rule; state doctrine; S1–S7; D1–D5 | **Proposed here** |
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
  with evidence against S1–S7.
- **Edge cases** — calendar and precision pathologies, contested
  attributions, entity-scoping traps.

Validated catches earn the same recognition as Genesis Window review.
Nothing here is sealed. That is precisely the point — this is the one
phase of Ring 2's life in which every rule is still negotiable in public,
and the chain will later witness that it was.
