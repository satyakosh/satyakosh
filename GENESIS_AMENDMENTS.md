# Genesis freeze — pending amendments to local files

> **Reconciliation note (2026-07-17, FD-24):** the recovered
> pre-loss originals were restored as the base for SCHEMA, SCOPE,
> TAXONOMY, MISSION, CONTRIBUTING, and PIPELINE_POLICY, and the
> amendments below were re-applied on top of the original bytes.
> A1-A10 are therefore applied (checked). See
> docs/rebuild_divergence_report.md.

Every decision from the genesis-design sessions that must land in the
local working files BEFORE the six document hashes are computed. Apply to
the real local bytes directly; do not regenerate documents from memory.

## SCHEMA.md

- [x] **A1 — Scope the ASCII invariant.** §7.2 and the invariant list:
      "canonical bytes are pure ASCII" applies to `fact` records only, as
      an intake tripwire keyed to v1's admissible vocabularies (any
      non-ASCII byte in a fact record is an attack signature, not
      content). Chain-wide rule remains NFC UTF-8. Genesis record is
      NFC UTF-8 by design.
- [x] **A2 — State the genesis identity exception.** Invariant 6 (no
      contributor identity in hashed content) carries one conscious
      exception: the genesis inscription (founder name + dedication),
      with consent on record.
- [x] **A3 — Amend §9** to enumerate the full genesis manifest:
      inscription; schema_version + schema_hash; pipeline_policy_version +
      pipeline_policy_hash; scope_hash; admissibility_map_hash;
      mandatory_conditions_hash; predicates_founding_hash; inline
      three-source whitelist; chain fields.
- [x] **A4 — Amend §10**: add "supersession of any founding-document
      hash" to the governance-record triggers.
- [x] **A5 — Version relabel.** Header and all self-references:
      v2.1(-rc2) → 1.0.0 (1.0.0-rc.1 during the Genesis Window). Move the
      v2.0→v2.1 lineage to CHANGELOG/design-history (unsealed).

## SCOPE.md

- [x] **A6 — Character-inventory clarification** (recommended, not
      blocking): characters-as-entities via Unicode code points are
      in-scope but Ring 2 (external-standard adoption); lexical facts
      (word meanings, translations) remain out of scope. Draws the
      boundary proposers will probe.
- [x] **A7 — Version relabel** as in A5.

## PIPELINE_POLICY.md

- [x] **A8 — Batch-proposal mechanism (BLOCKING).** Define review of
      mechanically-ingested batches: the reviewed object is the batch
      (ingestion script + source pin + spot checks); each fact still gets
      its own record, ID, and dispute window; a disputed fact holds in
      review while siblings seal. Required before freeze — the CODATA
      full-set ingestion depends on it, and the policy hash seals at
      genesis.
- [x] **A9 — Genesis Window review scope**: adversarial review explicitly
      covers all six frozen documents, not only the schema.
- [x] **A10 — Version relabel** as in A5.

## admissibility_map.json

- [ ] **A11 — Confirm final state** as machine-readable data (the §11
      table), JCS-canonicalized. Hash of this file seals in genesis.

## rulesets/mandatory_conditions.json

- [x] **A12 — Confirm final state.** Reference implementation
      check_mandatory_conditions.py self-test passes (16/16 in the
      rebuilt tool: the original's 11 cases + 1 unknown-derivation-type
      case + 2 malformed-input cases + 2 placeholder-guard cases).
      Hash seals in genesis. **Done 2026-07-17:** all four placeholder
      entity IDs resolved (method = SK-ENT-000008; boiling temperature
      of water = SK-ENT-000005; pressure = SK-ENT-000006; temperature
      scale = SK-ENT-000007) and confirmed by the founder, together
      with the full entity registry.

## Predicate registry

- [ ] **A13 — Produce founding snapshot** (at minimum SK-PRED-000001 with
      its definition wording final) and compute predicates_founding_hash.
      Entity-registry founding hash deliberately NOT sealed (labels are
      renderings; revisit via governance record at Ring 2 if needed).
- [x] **A17 — Lock the predicates_founding_hash convention.**
      **Decided 2026-07-17 (founder):** uniform doctrine — prose
      documents (.md) hash as raw frozen file bytes; machine-readable
      JSON documents hash as their JCS serialization. Applied to
      predicates_founding_hash AND mandatory_conditions_hash (both now
      JCS). SCHEMA s9, the genesis draft, and tools/genesis_hashes.py
      updated to match.

## ledger.py

- [x] **A14 — Extend placeholder-refusal check** to the genesis
      structure: refuse to seal if any field contains a placeholder
      marker, any hash field is non-hex, or founder/dedication/mission
      strings are empty. **Done 2026-07-16, and extended beyond the
      original scope:** (a) fact seals also refuse while any ruleset in
      force carries operative placeholders (a placeholder subject rule
      must never silently stop matching); (b) record 0 must be genesis;
      (c) a duplicate canonical triple among non-superseded facts
      refuses to seal (SCHEMA s11 exact-lookup rule); (d) malformed
      proposals are rejected with citable ValidationErrors, never
      crashes.
- [ ] **A15 — Scope the ASCII validator** per A1: enforce
      pure-ASCII on fact records; enforce NFC UTF-8 (not ASCII) on the
      genesis record.

## Seed proposals (local file)

- [ ] **A16 — Restructure to the tiered plan**: (1) seven SI defining
      constants, hand-proposed, individually reviewed, facts #1–7;
      (2) full CODATA 2022 recommended set (~350) as one batch proposal
      per A8; (3) a handful of condition-bearing facts exercising
      Dimension D; (4) one deliberate permanent rejection demonstrating
      the review zone.

## Genesis transcription checklist (for the review file)

- [x] Pavamana mantra: **confirmed 2026-07-17 (founder)** — the
      unaccented, word-separated Devanagari form as drafted, a
      deliberate legibility-and-unambiguity choice (consistent with the
      simplified-romanization citation) rather than a facsimile of one
      printed edition; danda pattern । after lines 1-2, double danda ॥
      terminal; spaced मृत्योर्मा अमृतं (no avagraha). NFC-stable,
      61 code points; exact sequence recorded below.
- [x] Citation string locked: "Brihadaranyaka Upanishad 1.3.28"
      (simplified romanization — deliberate choice over IAST).
- [x] Dedication exact bytes: **confirmed 2026-07-17 (founder)** —
      wording final; em dash (U+2014) kept by explicit decision.
- [ ] Anaya's informed consent (permanence + erasure waiver explained)
      noted in the review file.

Recorded invocation code points (NFC, 61 code points, confirmed
2026-07-17 — the genesis review file must match this sequence exactly):

```
0905 0938 0924 094B 0020 092E 093E 0020 0938 0926 094D 0917 092E 092F
0020 0964 0020 0924 092E 0938 094B 0020 092E 093E 0020 091C 094D 092F
094B 0924 093F 0930 094D 0917 092E 092F 0020 0964 0020 092E 0943 0924
094D 092F 094B 0930 094D 092E 093E 0020 0905 092E 0943 0924 0902 0020
0917 092E 092F 0020 0965
```
- [ ] Founder string "Shubhankar Patil" matches trademark filings.
- [ ] Founding date 2026-07-07 = trademark priority date (independent
      corroboration).

## Still owed by the founder (no one else can write these)

1. Mission prose passage: **working draft chosen 2026-07-17** (the
   plain-institutional register; now in genesis_record.draft.json).
   Founder's final read — after at least 48 hours and one read-aloud —
   locks it at the freeze; until then it is a draft, not a decision.
2. ~~Final read of the dedication wording (current draft is locked unless
   you change it).~~ Confirmed 2026-07-17.

- [x] **A18 — Specify the canonical review-file format.**
      **Settled 2026-07-17 (founder):** format 1.0.0 at
      docs/review_file_format.md — JCS + SHA-256 canonical bytes;
      recipes referenced by content hash (mirrored alongside review
      files); process_hash computed only at seal (held proposals stay
      live and unsealed); one review file per fact with batch_ref
      (P11); Git history is the authoritative timeline; machine
      annotations carry tool_version. SCHEMA s7.4 updated to point at
      the format doc. Not genesis-hashed by design — evolves by
      governance record, versioned inside each review file. **A draft proposal exists at
      docs/REVIEW_FILE_FORMAT.draft.md** with five open questions for
      the founder to settle; once settled it folds into SCHEMA s7.4.

## Window scheduling (locked 2026-07-17, founder)

The Genesis Window is **readiness-gated, not scheduled**. It opens only
after ALL of: (1) founder line-by-line re-read of every Tier B/C
document; (2) founder digit-by-digit verification of the Tier 1 seed
values against the sources; (3) the dedication-consent note recorded;
(4) the mission prose confirmed after the 48-hour final read;
(5) founder-string / founding-date corroboration checks;
(6) tools/genesis_hashes.py green. No date is announced before those
are checked off. PyPI 1.0.0rc1 ships only after genesis seals clean
(with the verifier), per the existing versioning rule.

## Tracked, not blocking the freeze

- **Governance engine.** SCHEMA s10 / P9 promise chain-position ruleset
  resolution (genesis state + preceding governance records) and
  governance-payload validation; the reference implementation validates
  against in-memory rulesets only. The engine must exist before the
  FIRST governance record seals — nothing may enter the chain that a
  verifier cannot re-derive rules for. **Retirement** (the `retires`
  retraction record that derives `status: retired`) ships with it.
- **Intake artifact checks.** The intake pipeline (and CI) must verify,
  for every proposal carrying a `derivation.script`, that the recipe
  file exists at `derivations/<triple_hash>.py`, its SHA-256 matches,
  and it runs clean — so no fact seals pointing at a missing or drifted
  recipe. Out of scope for `ledger.py` (which validates bytes, not the
  filesystem); belongs to the proposal-intake tooling built for the
  Genesis Window.

- **Legal wrapper.** Decide the long-term legal form (foundation or
  trust whose sole mandate is perpetual maintenance of the public
  ledger, with explicit succession rules). Institutional independence
  (MISSION principle 3) requires this to exist *before* the first
  serious partner, sponsor, or funding conversation — not after.
