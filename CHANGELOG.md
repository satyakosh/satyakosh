# Changelog

Public versioning starts at 1.0.0. Version numbers track the
canonical-byte contract (SCHEMA.md s10).

## 1.0.0-rc.1 (Genesis Window candidate) — 2026-07
- First public version. Internal draft lineage renumbered.
- Governance-engine hardening (2026-07-19, issue #7 — all five findings
  reproduced first): `verify(full)` replays from a position-zero ruleset
  snapshot so a tightening `ruleset_change` no longer retroactively
  condemns history (G1); `ruleset_change` content is structurally
  validated at governance-seal time against exactly the shape
  `validate_fact` indexes into, with a citable in-force backstop, so a
  malformed ruleset can neither seal nor brick later fact seals with a
  raw KeyError (G2); the genesis-declared digests now BIND — the engine
  hashes the rulesets and predicates registry it is handed (JSON as JCS)
  and refuses on mismatch, and `verify.py --repo DIR` binds all six
  digests plus the inline whitelist against a repository checkout,
  honoring later doc_supersession/ruleset_change records (G3); the
  genesis inline whitelist is authoritative — it becomes the in-force
  founding whitelist and the sources file must agree with it on
  {id, publisher, rings} at genesis-seal time (G4); UCUM codes get a
  syntax check and governance deltas refuse any `<<` marker, so
  `<<TBD>>` can never enter force (G5). Governance suite 36 cases.
- Issue #7 follow-up (same day): the genesis sources-file agreement
  check is seal-time only — on audit replay the inline whitelist is
  authoritative, so a sources file later regenerated to mirror a
  governance-added source no longer retroactively condemns the chain
  (reviewer-demonstrated whitelist baseline drift). Post-freeze
  CI-gating of the genesis document hashes tracked in
  GENESIS_AMENDMENTS. FD-32 recorded (position-correct replay;
  genesis-inlining of rulesets considered and deferred in favor of
  G3's hash binding), with two regression cases ported from its
  parallel patch: an era-violating hash-valid forgery flagged only by
  verify(full), and a planted invalid governance record flagged
  without its fold poisoning replay state. Governance suite 41 cases.
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
- Validator hardening round 3 (2026-07-17, second external review; all
  findings reproduced first): verify() never raises — corrupt/hostile
  stored bytes (float, lone surrogate, retyped field) become CORRUPT/
  INVALID findings, and a verifier-side fuzzer enforces it in CI (found
  228 residual crash paths on the first run, all closed); the 16-char
  fact_id form is now permitted only on a real 12-char collision (FD-25),
  closing a retired-triple re-entry channel; derived_from to a dead
  lineage seals with a liveness warning flag. SCHEMA documents retired
  status as a governance-era derived state, born-expired windows as
  intentional, and derivation.script artifact checks as an intake/CI
  requirement. Ledger suite 52 -> 58 cases. Follow-up: the FD-25
  collision check had quietly reintroduced O(n^2) sealing (973
  seals/s at N=9000); a prefix-12 index restores flat scaling
  (4400+ seals/s).
- Issue #6 (Ring-2 campaign, 2026-07-19): the F3 source-count fix
  counted array ENTRIES, not distinct institutions - two editions
  of one publisher, or a byte-identical duplicate entry, satisfied
  '>= 2 independent sources'. Now: duplicate source IDs are refused
  outright (a source appears at most once - v1 hardening, catches
  both bypasses), and source_count_rules counts distinct source IDs
  per RING2 s3.1's independence requirement. Pinned as F5/F5b/F6;
  ledger suite 66 -> 69.
- Governance engine built (2026-07-19, FD-30): SCHEMA s10/P9 realized - validate_governance (five kinds: whitelist_change, ruleset_change, ucum_expansion, ascii_exemption, doc_supersession; strict deltas validated against the rules in force, no no-ops or double-applies) plus Ledger.rules_in_force / _apply_governance folding deltas in chain order onto genesis state (reconstructible from the chain alone, load-path replay included). Built ahead of need as a Genesis Window review target - not a freeze gate. stress/test_governance.py (25 cases) runs a full simulated Ring-2 activation end to end (a fact the founding rules refuse seals only after the activation records) and the ASCII-tripwire narrowing dry-run the review asked for (M4). This reverses FD-29(a)'s defer-timing on the strength of the review-during-window argument.
- Synthesis security review triaged (2026-07-19): most findings
  confirmed already-done (rfc8785 cross-check + seal rehearsal in
  CI, chain-rule pins from issues #1-6) or a stale docstring (H2,
  fixed). Two founder calls (FD-29): the governance engine is a
  pre-Ring-2 prerequisite, not a window-open gate; and % / a are
  removed from the founding UCUM whitelist (closed by default —
  inert for v1, re-added at Ring-2 activation by governance).
- Standalone verifier CLI (2026-07-19, verify.py at repo root): one
  pure-ASCII file, stdlib only, zero imports from the engine -- the
  independent second implementation as a downloadable tool. Verifies
  content hashes, triple hashes, fact_id prefixes, chain linkage and
  head; derives supersession status from the chain alone; --fact and
  --json modes for grounding receipts; hostile input yields findings,
  never crashes. Exercised in CI: clean chain, tamper detection, fact
  lookup.
- Issue #5 (fifth external review, simulated Ring-2 activation; all
  four findings reproduced then closed, 2026-07-19): UCUM whitelist
  gains % and a (the Ring-2 corpus's commonest units; the
  dimensionless workaround sealed and was semantically wrong);
  duplicate condition properties raise a review flag (refusal was
  rejected - s3.4 documents min/max range pairs as a feature);
  source_count_rules dormant capability added (per-derivation-type
  minimum source counts; Ring-2 activation sets values by
  governance, engine change no longer needed); predicate
  object_types registry declarations are now enforced with citable
  refusals. SCHEMA s11 documents all three. Ledger suite 60 -> 66.
- Ring-2/3 expressiveness battery (2026-07-18,
  stress/ring2_expressiveness.py, in CI): drafts representative
  future claims using the reserved entity/date shapes and proves the
  frozen machinery carries them - 28 hard checks on
  canonicalization, identity semantics (precision/calendar/scoping
  distinctions hash distinctly, as the conflict ladder requires),
  ASCII survival of all Ring-2 vocabularies, and citable refusal of
  Ring-2/BLOCKED/attestation claims today. Its E1 probe caught a
  real activation-era bug - the near-duplicate index assumed every
  object has a unit and would have crashed on entity/date facts;
  fixed (heuristic now quantity-scoped) and pinned. Remaining
  findings recorded as the Ring-2 activation worklist in
  GENESIS_AMENDMENTS.
- Genesis seal rehearsal (2026-07-18): stress/rehearse_genesis.py
  runs the full freeze-day ceremony on a staging chain in CI -
  computes the six hashes, fills a draft copy, seals, verifies,
  and re-derives content_hash and chain head with an independent
  stdlib-only second implementation that must agree. FD-28: founded
  month convention locked purnimanta (Ashadha; amanta name Jyeshtha
  recorded); documents freeze as 1.0.0 with rc.1 as the pre-freeze
  drafting label. Invocation re-verified byte-for-byte against the
  FD-13 sequence; Saptami-at-sunrise verified for Delhi and Pune.
- Genesis inscription (2026-07-18, FD-27): founded field now dual-
  calendar (Vikram Samvat first, then Gregorian, calendars named;
  panchang-verified, NFC-stable, single ISO machine anchor enforced
  by the validator); mission prose gained the remembrance sentence
  (48-hour final-read clock restarted).
- RING2.md original recovered (2026-07-09 draft rc1) and restored
  wholesale with the FD-19 parameter locks applied - including the
  seven source-admission criteria (S1-S7) that were the last marked
  reconstruction gap. The recovery of the lost working copy is
  complete: every founding document is now original bytes or a
  founder-decided successor.
- Reconciliation (FD-24, 2026-07-17): the recovered originals of
  SCHEMA, SCOPE, TAXONOMY, MISSION, CONTRIBUTING, and PIPELINE_POLICY
  restored as the base with all post-loss amendments re-applied. The
  sealed fact record returns to its taxonomy-review field set
  (terminality instead of truth_type; derivation.script seals the
  recipe hash); SCOPE's original S1-S7 (incl. self-reference) and the
  four-dimension TAXONOMY return; pipeline rules return to P1-P10 (+
  P11 batch). Validator and all suites aligned.
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
