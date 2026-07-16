# RECOVERY_NOTES.md — provenance of every file after the 2026-07-15 loss

The local working copy was lost before the first push. Nothing was sealed:
no hash was frozen, so every document below regains full authority the
moment the founder re-reviews it. This file records where each rebuilt
file came from and what it needs before the genesis freeze.

## FIRST: try to recover the originals

If any pre-loss original file is recovered (from downloads, backups, or
sync copies of `satyakosh-v0.zip` / `satyakosh-first-commit.zip`), **diff
it against the rebuilt file here and prefer the original.**

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
- stress/volume_test.py — rebuilt and re-run 2026-07-18 (9,000 synthetic
  records: seal, verify, determinism, duplicate refusal, tamper sweep,
  save/load). Report regenerated at stress/VOLUME_TEST_REPORT.md; the
  run also caught and fixed a platform-encoding bug in Ledger.save/load
  (UTF-8 now explicit).

**Fetched verbatim from canonical sources:** LICENSE-APACHE, LICENSE-CC0.

## Before the genesis freeze (in addition to GENESIS_AMENDMENTS.md)

1. Re-review every Tier B/C document end to end.
2. Confirm or reassign all entity registry IDs (Tier C note in
   entities.json), then resolve the four placeholders in
   rulesets/mandatory_conditions.json.
3. ~~Re-implement and re-run the volume test; regenerate its report.~~
   Done 2026-07-18 (stress/volume_test.py, stress/VOLUME_TEST_REPORT.md).
4. Verify every Tier 1 seed value digit-by-digit against CODATA/BIPM.
5. Resolve the flagged Tier 3 condition-typing question (ITS-90 as an
   entity-valued condition is a v-next type; decide the v1 treatment).
6. Only then compute the six founding-document hashes.

## The lesson, institutionalized

The founding documents of a permanence project lived on one laptop. From
today: the GitHub repo is the working copy (push after every session),
and CLAUDE.md now instructs every future session to treat the repo — not
any local disk — as canonical until genesis moves canonicity to the chain.
