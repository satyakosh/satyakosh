# Changelog

Public versioning starts at 1.0.0. Version numbers track the
canonical-byte contract (SCHEMA.md s10).

## 1.0.0-rc.1 (Genesis Window candidate) — 2026-07
- First public version. Internal draft lineage renumbered.
- P11 batch-proposal mechanism added to the pipeline policy.
- ASCII invariant scoped to fact records; genesis defined as NFC UTF-8.
- Genesis record enumerates six founding-document hashes plus the inline
  whitelist.
- Validator hardening (2026-07-16): record 0 must be genesis; duplicate
  canonical triples refuse to seal; fact seals refuse while any ruleset
  in force carries operative placeholders; the intake tool flags unknown
  derivation types; malformed proposals get citable rejections, not
  crashes.
- Intake tool CLI + input hardening; property-based canonicalization
  tests (stress/test_canonical_properties.py) including a byte-for-byte
  cross-check of the JCS implementation against an independent RFC 8785
  library.
- Volume test rebuilt and re-run at 9,000 records (2026-07-16); report
  regenerated. The run exposed a platform-encoding bug in ledger
  save/load — file I/O is now explicitly UTF-8 on all platforms.
- Committed test suite (stress/test_ledger.py), founding-document hash
  tool (tools/genesis_hashes.py, report-only), and CI running all
  checks on every push and pull request.
- Mutation fuzzer (stress/fuzz_validator.py): random 1-3 field mutations
  of valid records must always yield a clean seal or a citable
  ValidationError, never a crash or a seal-but-invalid. Wired into CI
  (two seeds). Its first run found one gap — an unhashable truth_type
  crashed the enum membership test instead of a citable rejection; fixed
  and pinned as regression K8c2. Now clean across 20,000 mutations / 5
  seeds.
- docs/REVIEW_FILE_FORMAT.draft.md: draft proposal for the canonical
  review-file format that process_hash commits to (A18), with open
  questions for founder review.
- Genesis mission prose: working draft chosen and placed in the genesis
  draft (founder's final read locks it at the freeze). Review-file
  format 1.0.0 settled (A18, docs/review_file_format.md): JCS+SHA-256
  bytes, recipes by content hash, hash-at-seal only, per-fact files
  with batch_ref, Git history as the authoritative timeline,
  tool-versioned machine annotations.
- Pre-loss originals recovered (2026-07-17): both zips found and hashed.
  Locked inscription fields verified byte-identical against the
  original; predicate definition wording, source metadata, directory
  READMEs, and the original volume-test report restored; full
  reconciliation worklist at docs/rebuild_divergence_report.md (major
  divergences in SCHEMA s4, SCOPE, TAXONOMY, MISSION, PIPELINE_POLICY
  pending founder decision).
- DECISIONS.md added: the canonical founder decision register
  (FD-1..23 with commit audit trails, plus the explicitly-rejected
  list). The lost pre-push decision record lived outside the repo;
  this one lives inside it, appended in the same commit that applies
  each decision.
- Remaining founder forks settled 2026-07-17: Tier 3 boiling-point
  proposal will be held in review (never sealed with a placeholder
  condition); Tier 4 exhibit is the missing-condition refusal (no
  planted errors); RING2 parameters P1-P7 locked as proposed (still
  contestable per RING2 s9); Genesis Window is readiness-gated with no
  announced date; PyPI 1.0.0rc1 defers until genesis seals clean.
- Validator hardening round 2 (2026-07-17, from an external adversarial
  review; all findings reproduced before fixing): supersession is now a
  full transaction (target must exist, be latest, be unsuperseded;
  metadata supersession keeps fact_id and increments version by exactly
  1 — closes a duplicate-seal bypass); superseded-ness is derived from
  the chain, never written into sealed records; strict field
  enumerations (unknown fields refused); shared typed-union validation
  for condition values incl. registry existence; enums, hash formats,
  date formats, validity-window order, non-empty complete sources, and
  ring typing all enforced; exact quantities cannot carry uncertainty,
  uncertainty non-negative; jcs() refuses JSON floats (proven
  cross-implementation divergence) and lone surrogates; v1 UCUM code
  whitelist; near-duplicate flag implemented (warn, never refuse);
  derived_from references must exist; verify(full=True) replays every
  record through seal-time validation; O(1) duplicate index (4x faster
  sealing); atomic save; chain_head re-verified on load.
- Founder decisions recorded 2026-07-17: the four mandatory-conditions
  placeholder entity IDs resolved and the entity registry confirmed
  final; founding-document hash doctrine locked (prose = raw file
  bytes, JSON = JCS; SCHEMA s9); invocation orthography and dedication
  bytes confirmed, with the exact code-point sequence recorded in
  GENESIS_AMENDMENTS.md.

## Internal prehistory (never public, preserved for the record)
- v0 (2026-07-07): first prototype — schema, five CODATA seed facts,
  ledger engine, live tamper-detection demo. PyPI 0.0.1 name reservation.
- v2.0 (2026-07-09): semantic-triple restructure; JCS canonicalization;
  content-addressed IDs; D1-D8 locked.
- v2.1: typed object union; typed conditions; value grammar one-byte-form;
  ~130-fact semantic stress test; ~9,000-record volume test.
- v2.1-rc2 (2026-07-09): witnessed mandatory-condition ruleset; external
  four-perspective review closed with no hash-breaking findings.
- 2026-07-15: local working copy lost; repository rebuilt from session
  transcripts and the locked decision record (see RECOVERY_NOTES.md).
