# Rebuild divergence report — recovered originals vs the rebuilt line

2026-07-17. The pre-loss first-commit package (`satyakosh-first-commit.zip`,
SHA-256 `659851a0f97f32a33c7ad2f5c9039068dcb9f0c80af9c17acafefe0a28dde910`,
30 files, 2026-07-10) was recovered and diffed file-by-file against the
rebuilt repository. This report is the founder's reconciliation worklist:
every semantic divergence, classified. The rebuilt line carries
founder-locked post-loss decisions (DECISIONS.md), so recovered originals
are references, not automatic overrides — but several rebuilt documents
turn out to be reconstructions of *earlier drafts* than the originals,
and the originals are richer.

## Verified identical (no action)

- **All five locked genesis inscription fields are byte-identical**:
  invocation (61 code points), citation, founder, dedication, founded.
  The transcript reconstruction was perfect. FD-13/FD-14 now rest on
  original evidence.
- **Admissibility map**: structurally different JSON, semantically
  identical (same 9 derivation types, same verdicts). The original's own
  note specifies `SHA-256(JCS(file))` — FD-12's hash doctrine matches
  the original convention independently.
- **Original entity registry was empty** ("entities are registered
  together with the seed proposals") — the FD-11 ID assignments
  contradict nothing.
- **Genesis draft structure**: same fields, same whitelist, same
  placeholder discipline (naming differs: `genesis.draft.json` vs
  `genesis_record.draft.json`).

## Restored mechanically in this commit (no decision needed)

- **SK-PRED-000001 definition wording** (load-bearing — seals into
  `predicates_founding_hash`): original sentence restored, plus the
  original `object_types` and `status` fields.
- **Source registry enrichment**: original `name`/`urls`/`editions`
  metadata merged into the rebuilt entries.
- **Directory READMEs** (proposals, labels, registries verbatim;
  derivations, ledger, rules, stress adapted to the current layout).
- **The original volume-test report** archived as
  `stress/VOLUME_TEST_REPORT-2026-07-09.md` — historical record of the
  pre-loss 9,000-record run and the four findings that shaped the value
  grammar. (Its X-series attack list confirms the original validator
  rejected exact-with-uncertainty — behavior the rebuilt validator
  independently regained in hardening round 2.)

## MAJOR divergences — founder reconciliation required before freeze

These four documents are genesis-hashed (or feed genesis-hashed
content). The rebuilt versions were reconstructed from earlier-draft
fragments; the originals are the final pre-loss state.

1. **SCHEMA s4 — the sealed fact field set.** The original *removed*
   `truth_type` (July 2026 taxonomy review: "conflated stability with
   dependence"; satisfied structurally by conditions + validity window +
   terminality + attestation) and uses `terminality`
   (`none|expected|scheduled`) instead of the rebuilt boolean
   `valid_until_expected`; original `status` enum includes `retired`;
   original `derivation` is structured (`{type, script, derived_from}`)
   with `script` = SHA-256 of `derivations/<triple_hash>.py` sealed
   *inside the fact record*. The rebuilt validator, all test fixtures,
   and the seed drafts follow the rebuilt (stale) field set.
   **Recommendation: adopt the original field set** — it is the
   deliberate outcome of the taxonomy review — and re-apply the rebuilt
   line's post-loss improvements on top. Coordinated change: SCHEMA,
   ledger.py, all fixtures, seed proposals, review-file format
   (`derivation.script` complements FD-16's `recipe_hash`).
2. **SCOPE.md — a different S1–S7.** Original: S1 rules/procedures ·
   S2 derivable relations · S3 identity/equivalence · S4 fiction ·
   S5 event/results feeds · S6 lexical/translation · S7
   **self-reference** ("a ledger must never be judge in its own case").
   Rebuilt: different numbering, missing identity/equivalence and
   self-reference entirely, adds legal-registries and
   opinion/prediction. Rule IDs are cited in refusals and
   cross-referenced by other documents — the numbering is load-bearing.
   **Recommendation: restore the original wholesale**, then re-apply
   amendment A6 (Unicode character-inventory clarification) to it.
3. **TAXONOMY.md — the four-dimension intake model.** The original is
   the final "dimensions A–D, only Dimension A earns a sealed field"
   architecture with full verdict tables (SEAL-V1 / RING-2 PENDING /
   ATTEST / BLOCKED) and worked examples; the rebuilt C1–C10 table is an
   earlier draft. The original also documents the truth_type removal
   rationale (ties to divergence 1) and corroborates the Tier 3 boiling
   value (9.9974e1 Cel @ ITS-90). **Recommendation: restore wholesale.**
4. **MISSION.md — the principles and the statement.** Original
   principle 1 is "**Open data is the moat**" (revenue from freshness,
   convenience, attestation — never from access); the rebuild replaced
   it with "Immutability over editability" (which the original treats as
   a schema invariant, not a mission principle). The original also
   carries the full quotable mission statement ("What the seed vault is
   to crops and the public archive is to the web, Satyakosh is to
   facts."), the attestation-layer-as-product line, and the status
   context (trademark classes/timeline, parked incorporation options,
   "internal enthusiasm is not market validation").
   **Recommendation: restore wholesale** (status section updated to
   2026-07); revisit the genesis mission-prose draft against the
   original statement before the final read.
5. **PIPELINE_POLICY.md — different P-numbering and seal
   preconditions.** Original P1–P10 ordering differs from rebuilt
   P1–P11; original P5 carries the explicit seal preconditions
   (window complete, objections resolved, derived_from already sealed,
   process_hash matches) that the rebuilt version scattered; original
   P10 fixes rules P1–P9 during the window while allowing operational
   tuning. **Recommendation: restore the original**, then re-apply
   amendment A8 (batch proposals — the rebuilt P11) as P11.
6. **SCHEMA smaller items**: original invariant 4 carries the witnessed-
   governance formulation ("policy fossilized is brittle; policy
   invisible is capturable; policy witnessed is correct"); original
   invariant 6 handles fact-subjects-who-are-people and erasure law for
   unsealed labels; original s5 documents the attestation layer and
   `labels/facts/<fact_id>.json`; original s11 has the Process
   paragraph (review completeness as a validation requirement).
   **Recommendation: fold into the s4 reconciliation pass.**

## Still missing after this recovery

- **RING2.md original** (with the exact seven source-admission
  criteria) was not part of the first-commit package — it lived in the
  2026-07-09 session. The gap and its candidate re-derivations stand.
- The original `ledger.py` (internal v2.1), `volume_test.py`,
  `mandatory_conditions.draft.json`, and seed proposals were never in
  this package (the checklist said to add them from the machine — they
  were lost with it). The rebuilt versions, twice adversarially
  hardened, exceed them; no action.

## Note on the recovery itself

The package had been sitting extracted in `Downloads\satyakosh-first-commit`
since before the loss — the 2026-07-15 loss took the *later* working
copy (v2.1 engine, RING2, mandatory-conditions draft), not this
package. Lesson unchanged and now doubly earned: the repo is canonical;
local disks are not.
