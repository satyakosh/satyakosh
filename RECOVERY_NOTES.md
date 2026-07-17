# RECOVERY_NOTES.md — provenance of every file after the 2026-07-15 loss

The local working copy was lost before the first push. Nothing was sealed:
no hash was frozen, so every document below regains full authority the
moment the founder re-reviews it. This file records where each rebuilt
file came from and what it needs before the genesis freeze.

## FIRST: try to recover the originals

If any pre-loss original file is recovered (from downloads, backups, or
sync copies of `satyakosh-v0.zip` / `satyakosh-first-commit.zip`), diff
it against the rebuilt file here. NOTE (2026-07-17): "prefer the
original" no longer applies wholesale — the rebuilt line now carries
founder-locked decisions (see DECISIONS.md) that postdate the originals;
recovered files are read-only references for the founder re-review.

**Recovered 2026-07-17: `satyakosh-v0.zip`** (7,691 bytes, SHA-256
`630e214688293d09d0d82beff89c8c7ae1a64408a66c3df30984e692b93002e0`) —
the 2026-07-06 "Fact Anchor" v0.1 prototype: SCHEMA.md, ledger.py,
seed_facts.json, sealed 5-record demo ledger (chain verifies intact).
Pure prehistory; kept locally, not imported (CHANGELOG: never public,
preserved for the record). It independently corroborates three Tier 1
seed values (c, h, N_A) and contains nothing the current line lacks.
**Recovered 2026-07-17: `satyakosh-first-commit.zip`** (45,039 bytes,
SHA-256
`659851a0f97f32a33c7ad2f5c9039068dcb9f0c80af9c17acafefe0a28dde910`,
30 files — and it had been sitting extracted in Downloads all along;
the 2026-07-15 loss took the later working copy, not this package).
Full file-by-file reconciliation worklist:
**docs/rebuild_divergence_report.md**. Headlines: all five locked
inscription fields byte-identical; admissibility map semantically
identical; predicate wording + source metadata + directory READMEs +
the original volume-test report restored; MAJOR divergences found in
SCHEMA s4 / SCOPE / TAXONOMY / MISSION / PIPELINE_POLICY (rebuilds were
based on earlier-draft fragments) — founder reconciliation required
before the freeze. RING2.md was NOT in this package: the seven
source-admission criteria remain outstanding (last lead: the
2026-07-09 session).

## Provenance tiers

**Tier A — authoritative (written fresh this session, no loss):**
- genesis_record.draft.json — every field a locked decision
- CLAUDE.md, GENESIS_AMENDMENTS.md, RECOVERY_NOTES.md

**Tier B — recovered near-verbatim from transcripts (spot-check, then
trust):**
- SCHEMA.md — invariants, record types, s3.1-3.4, s6, s7 (incl. the v2.1
  value grammar word-for-word), s7.4-s11 recovered verbatim; s4/s5 tables
  rebuilt from fragments; amendments A1-A5 applied
- rulesets/mandatory_conditions.json — structure and wording recovered
  verbatim, placeholders preserved as in the original draft
- RING2.md — sections 6-9 near-verbatim; 1-5 rebuilt (one marked gap:
  the exact seven source-admission criteria)
- MISSION.md — principles 3-6, problem, and design text near-verbatim

**Tier C — reconstructed from the locked decision record (content is
right, wording is new; founder must re-review line by line):**
- SCOPE.md (S1-S7), PIPELINE_POLICY.md (P1-P10 + new P11), TAXONOMY.md,
  CONTRIBUTING.md, README.md, CHANGELOG.md, registries/*.json,
  rules/admissibility_map.json, seed_proposals.draft.json,
  docs/derived_views/claim_class.md

**Tier D — code, functionally reconstructed (specified by SCHEMA s7-s11;
NOT byte-identical to lost originals; tests re-run in-container):**
- ledger/ledger.py — smoke test passed: valid seal, mandatory-condition
  rejection, grammar rejection, homoglyph rejection, tamper detection,
  chain-head stability
- tools/check_mandatory_conditions.py — self-test 16/16 (the original's
  11 cases + 1 unknown-derivation-type case + 2 malformed-input cases +
  2 placeholder-guard cases)
- stress/volume_test.py — rebuilt and re-run 2026-07-16 (9,000 synthetic
  records: seal, verify, determinism, duplicate refusal, tamper sweep,
  save/load). Report regenerated at stress/VOLUME_TEST_REPORT.md; the
  run also caught and fixed a platform-encoding bug in Ledger.save/load
  (UTF-8 now explicit).

**Fetched verbatim from canonical sources:** LICENSE-APACHE, LICENSE-CC0.

## Before the genesis freeze (in addition to GENESIS_AMENDMENTS.md)

1. Re-review every Tier B/C document end to end.
2. ~~Confirm or reassign all entity registry IDs (Tier C note in
   entities.json), then resolve the four placeholders in
   rulesets/mandatory_conditions.json.~~ Done 2026-07-17: all IDs
   founder-confirmed; placeholders resolved.
3. ~~Re-implement and re-run the volume test; regenerate its report.~~
   Done 2026-07-16 (stress/volume_test.py, stress/VOLUME_TEST_REPORT.md).
4. Verify every Tier 1 seed value digit-by-digit against CODATA/BIPM.
5. Resolve the flagged Tier 3 condition-typing question (ITS-90 as an
   entity-valued condition is a v-next type; decide the v1 treatment).
6. Only then compute the six founding-document hashes.

## The lesson, institutionalized

The founding documents of a permanence project lived on one laptop. From
today: the GitHub repo is the working copy (push after every session),
and CLAUDE.md now instructs every future session to treat the repo — not
any local disk — as canonical until genesis moves canonicity to the chain.
