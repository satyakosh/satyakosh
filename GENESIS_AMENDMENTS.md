# Genesis freeze — pending amendments to local files

Every decision from the genesis-design sessions that must land in the
local working files BEFORE the six document hashes are computed. Apply to
the real local bytes directly; do not regenerate documents from memory.

## SCHEMA.md

- [ ] **A1 — Scope the ASCII invariant.** §7.2 and the invariant list:
      "canonical bytes are pure ASCII" applies to `fact` records only, as
      an intake tripwire keyed to v1's admissible vocabularies (any
      non-ASCII byte in a fact record is an attack signature, not
      content). Chain-wide rule remains NFC UTF-8. Genesis record is
      NFC UTF-8 by design.
- [ ] **A2 — State the genesis identity exception.** Invariant 6 (no
      contributor identity in hashed content) carries one conscious
      exception: the genesis inscription (founder name + dedication),
      with consent on record.
- [ ] **A3 — Amend §9** to enumerate the full genesis manifest:
      inscription; schema_version + schema_hash; pipeline_policy_version +
      pipeline_policy_hash; scope_hash; admissibility_map_hash;
      mandatory_conditions_hash; predicates_founding_hash; inline
      three-source whitelist; chain fields.
- [ ] **A4 — Amend §10**: add "supersession of any founding-document
      hash" to the governance-record triggers.
- [ ] **A5 — Version relabel.** Header and all self-references:
      v2.1(-rc2) → 1.0.0 (1.0.0-rc.1 during the Genesis Window). Move the
      v2.0→v2.1 lineage to CHANGELOG/design-history (unsealed).

## SCOPE.md

- [ ] **A6 — Character-inventory clarification** (recommended, not
      blocking): characters-as-entities via Unicode code points are
      in-scope but Ring 2 (external-standard adoption); lexical facts
      (word meanings, translations) remain out of scope. Draws the
      boundary proposers will probe.
- [ ] **A7 — Version relabel** as in A5.

## PIPELINE_POLICY.md

- [ ] **A8 — Batch-proposal mechanism (BLOCKING).** Define review of
      mechanically-ingested batches: the reviewed object is the batch
      (ingestion script + source pin + spot checks); each fact still gets
      its own record, ID, and dispute window; a disputed fact holds in
      review while siblings seal. Required before freeze — the CODATA
      full-set ingestion depends on it, and the policy hash seals at
      genesis.
- [ ] **A9 — Genesis Window review scope**: adversarial review explicitly
      covers all six frozen documents, not only the schema.
- [ ] **A10 — Version relabel** as in A5.

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

1. Mission prose passage (MISSION.md opening is the starting point).
2. ~~Final read of the dedication wording (current draft is locked unless
   you change it).~~ Confirmed 2026-07-17.

- [ ] **A18 — Specify the canonical review-file format.** process_hash
      is "SHA-256 of the raw review-file bytes" (SCHEMA s7.4), but no
      canonical review-file format exists, so the hash is currently
      unverifiable by third parties. Define the format (and how
      reviewer attestations are recorded) BEFORE the Genesis Window
      opens — the window's first sealed facts carry process hashes
      that must be auditable.

## Tracked, not blocking the freeze

- **Governance engine.** SCHEMA s10 / P9 promise chain-position ruleset
  resolution (genesis state + preceding governance records) and
  governance-payload validation; the reference implementation validates
  against in-memory rulesets only. The engine must exist before the
  FIRST governance record seals — nothing may enter the chain that a
  verifier cannot re-derive rules for.

- **Legal wrapper.** Decide the long-term legal form (foundation or
  trust whose sole mandate is perpetual maintenance of the public
  ledger, with explicit succession rules). Institutional independence
  (MISSION principle 3) requires this to exist *before* the first
  serious partner, sponsor, or funding conversation — not after.
