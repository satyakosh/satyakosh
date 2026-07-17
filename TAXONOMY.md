# Satyakosh — Fact Taxonomy (final)

> *Restored 2026-07-17 from the recovered 2026-07-10 original (pre-loss bytes; see RECOVERY_NOTES.md and docs/rebuild_divergence_report.md).*

### The intake model: four dimensions, one admissibility verdict

Facts are not filed into buckets; they are located along four independent
dimensions (per expert review, July 2026). The dimensions are how proposals
are *analyzed at intake*; the schema stores only what each dimension
compiles down to. **Only Dimension A earns a sealed field.**

| Dimension | Question | Values | Compiles to |
|---|---|---|---|
| **A — Source of truth** | How is it established? | defined · measured · observed · derived · proven · statistical · documentary (testimony) | **sealed** `derivation.type` → admissibility verdict + ring floor + evidence requirements |
| **B — Subject** | What is it about? | mathematical · physical · chemical · biological · geographic · historical · legal · linguistic · social · institutional | entity registry `domain` (unsealed; fact_id tag is a frozen courtesy, hash is identity) |
| **C — Stability** | How long does it hold? | eternal · stable · slowly-changing · time-bound · real-time | sealed *claim content* (`valid_from/until`, `terminality`) + **unsealed** freshness rating (an editorial forecast → the attestation layer's cache-invalidation contract) |
| **D — Dependence** | What does it hold relative to? | independent · conditional · context-dependent · cross-referential · model-dependent | **derived, never stored**: read off the record (conditions array; model condition; `derived_from`) |

The founding truth-type taxonomy (always / conditional / seasonal /
periodic) is not a field anywhere: it is *satisfied structurally* by
conditions, validity windows, terminality, and the attestation layer. The
requirements document became the architecture.

---

## Consolidated categories × admissibility (schema 1.0.0)

Verdicts: **SEAL-V1** (seals now, Ring 1) · **RING-2 PENDING** (representable
now, seals when Ring 2 governance + evidence framework exist) ·
**ATTEST** (attestation layer only — signed, timestamped, unsealed) ·
**BLOCKED** (representable, inadmissible until a dedicated framework exists) ·
**OUT OF SCOPE** (refused by mission, see SCOPE.md).

### SEAL-V1 — Ring 1, seals today
| Category | Example | Dimension A |
|---|---|---|
| Defined constants | c = 2.99792458e8 m/s | defined |
| Conventional exact values | standard atmosphere = 1.01325e5 Pa | defined |
| Measured fundamental constants | G = 6.67430(15)e-11 m³kg⁻¹s⁻² | measured |
| Mathematical facts incl. provable negatives | no even prime > 2 | proven |
| Conditional physical/chemical properties | water boils at 9.9974e1 Cel @ 1.01325e2 kPa, ITS-90 | measured |
| Taxonomic quantities | gold's atomic number = 79 | defined/observed |
| Derived exact constants | R = N_A·k (with `derived_from`) | derived |

### RING-2 PENDING — representable, awaiting Ring 2 governance
| Category | Example | Gating requirement |
|---|---|---|
| Statistical / aggregate | literacy rate (2011 census) = 74.04% | method-as-condition mandatory; ≥2 independent sources |
| Documented historical events | independence: 1947-08-15 | date objects; per-domain source lists; entity-scoping governance |
| Provenance / authorship | Hamlet — authored by — Shakespeare | evidence structure; contested-attribution handling |
| Biological/medical reference values | adult human bones = 206 | mandatory reference-population + counting-convention conditions |
| Definitional assignments | ISO 3166: India = "IN" | external-standard adoption record |
| Stable jurisdictional assignments | capital of France = Paris | jurisdiction condition; churn assessment |

### ATTEST — attestation layer, never sealed
| Category | Example | Why never sealed |
|---|---|---|
| Time-bound status / office | current PM of India | "current" is not a chain property |
| Counts over discovered sets | Pluto: 5 *known* moons | epistemic, defeasible by observation |
| Empirical negatives | element 119 not yet synthesized | absence-of-evidence, expires silently |
| High-churn jurisdictional | tax rates, visa rules | churn > chain cadence |

### BLOCKED — inadmissible pending dedicated frameworks
| Category | Example | Missing framework |
|---|---|---|
| Causal / mechanistic | smoking causes lung cancer | structured evidence model (strength, dissent, mechanism) |
| Institutional / legal-status | ₹500 is legal tender | authority = the state; independence principle; liability |

### OUT OF SCOPE — refused by mission (SCOPE.md)
Rules & procedures (chess moves, leap-year algorithm, passport renewal) ·
derivable relations ("Paris is north of Rome") · identity/equivalence
(registry `same_as`, never a fact) · fiction/in-universe claims · event &
results feeds · lexical/translation facts · the project's own legal or
commercial status (self-reference).

---

## How intake uses this (the contributor questionnaire)

1. **Dimension A:** how is your fact established? → fixes `derivation.type`,
   which fixes the verdict row above. If BLOCKED/OUT-OF-SCOPE, intake stops
   with a principled, citable reason — never an ad-hoc refusal.
2. **Dimension B:** what is the subject? → routes to the entity registry
   (register or reuse `SK-ENT-` IDs) and to domain reviewers.
3. **Dimension C:** does it expire? → sets `valid_from/until` +
   `terminality`; real-time answers divert the proposal to the attestation
   layer before review effort is spent.
4. **Dimension D:** what does it hold relative to? → drives the
   condition-completeness check (pressure? temperature scale? jurisdiction?
   method? reference model? epoch?). A fact missing a mandatory condition
   for its class does not enter review.
