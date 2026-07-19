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
- [x] Founded inscription in dual-calendar form (**FD-27, 2026-07-18**):
      "आषाढ़ कृष्ण सप्तमी, विक्रम संवत् 2083 (Vikram Samvat) — 7 July
      2026, 2026-07-07 (Gregorian)". Verified against published
      panchang sources (Drik Panchang et al.; sunrise-tithi convention
      — Ashtami begins later that civil day); NFC-stable, 91 code
      points; the single embedded ISO date is the machine anchor the
      validator now requires and the trademark-priority corroboration
      keys on. **Month convention founder-locked 2026-07-18:
      pūrṇimānta** (the reckoning customarily paired with the Vikram
      Samvat era) — hence Āshādha; the amānta reckoning names the same
      fortnight Jyeshtha (what a Maharashtra panchang shows). Saptami
      at sunrise verified for both New Delhi and Pune (tithi turns to
      Ashtami at ~13:24 IST that day); the tithi itself is
      convention-safe, only the month name forked. **Founder directly
      confirmed 2026-07-18: the Vikram Samvat month on 7 July 2026 is
      Āshādha — the inscription is correct as sealed-to-be.**
- [x] Anaya's informed consent: **granted, recorded 2026-07-18**
      (permanence + erasure waiver explained; the dedication seals
      forever and no future erasure is possible). To be transcribed
      into the genesis review file when it is created at the freeze —
      readiness gate 3 is satisfied.

Recorded invocation code points (NFC, 61 code points, confirmed
2026-07-17 — the genesis review file must match this sequence exactly):

```
0905 0938 0924 094B 0020 092E 093E 0020 0938 0926 094D 0917 092E 092F
0020 0964 0020 0924 092E 0938 094B 0020 092E 093E 0020 091C 094D 092F
094B 0924 093F 0930 094D 0917 092E 092F 0020 0964 0020 092E 0943 0924
094D 092F 094B 0930 094D 092E 093E 0020 0905 092E 0943 0924 0902 0020
0917 092E 092F 0020 0965
```
- [x] Founder string "Shubhankar Patil" matches trademark filings —
      **confirmed by founder against the filing, 2026-07-19.**
- [x] Founding date 2026-07-07 = trademark priority date (independent
      corroboration) — **confirmed by founder against the filing,
      2026-07-19.**
- [ ] At the freeze (FD-33): stamp the sealed genesis record's
      content hash with OpenTimestamps and commit the `.ots` proof
      alongside the first anchor row in `anchors/ANCHORS.md`; then
      push both remotes and request a Software Heritage save, so the
      genesis moment exists in every archive with a trust-free
      existence proof.

## Still owed by the founder (no one else can write these)

1. Mission prose passage: **founder-worded 2026-07-18** — the
   remembrance sentence now carries the founder's own phrasing ("let
   the world remember to return here — not for a verdict, but to
   check"), replacing the drafted wording after review. The prose is
   no longer assistant-scaffolded: the founder has put his hand on the
   sentence. The 48-hour final-read clock runs from this revision; the
   read-aloud locks it at the freeze.
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
values against the sources — **DONE 2026-07-19** (founder verified all
seven defining constants against the SI Brochure / CODATA table;
machine pre-checks and the recovered v0 corroboration are on record);
(3) the dedication-consent note recorded — **DONE 2026-07-18**;
(4) the mission prose confirmed after the 48-hour final read (clock
runs from the 2026-07-18 revision; earliest 2026-07-20);
(5) founder-string / founding-date corroboration checks — **DONE
2026-07-19** (founder confirmed both against the SATYAKOSH
trademark filing: applicant name matches the inscription bytes
exactly; priority date is 7 July 2026, the founded anchor);
(6) tools/genesis_hashes.py green with founder sign-off. No date is
announced before those are checked off. PyPI 1.0.0rc1 ships only after genesis seals clean
(with the verifier), per the existing versioning rule.

## Tracked, not blocking the freeze

- **Ring-2 activation worklist** (from the 2026-07-18 expressiveness
  battery, stress/ring2_expressiveness.py — all 28 frozen-surface
  checks pass; these are activation-era items): (1) the activation
  validator needs its own date pattern for astronomical/BCE years
  (record-level DATE_RE deliberately stays Gregorian-CE); (2) decide
  `edition: null` for archival sources (byte-affecting additive minor
  at activation); (3) the ASCII-tripwire narrowing mechanism is now exercised by a governance dry-run (test_governance.py, review M4); (3b) the precision enum's coarseness (two-day
  disagreements widen to month) is a documented limitation, revisit
  only if Ring 2 practice demands a `range` value; (4) UCUM whitelist:
  `%` and `a` pre-added 2026-07-19 (issue #5 F1 — the dimensionless
  workaround for a rate seals and is semantically wrong); further
  codes with proposals; (5) per-property condition cardinality
  rules (e.g. exactly-one method) belong to the activation ruleset
  schema — v1 flags duplicate properties for review (issue #5 F2).

- ~~**Governance engine.**~~ **Built 2026-07-19 (FD-30),** ahead of
  need, as a Genesis Window review target: validate_governance +
  Ledger.rules_in_force / _apply_governance implement SCHEMA s10 /
  P9 — payload validation against the rules in force, and
  chain-position resolution folded from genesis state plus preceding
  governance records (reconstructible from the chain alone, incl. the
  load-path replay). Five governance kinds; strict deltas that cannot
  no-op or double-apply; full simulated Ring-2 activation and the
  ASCII-narrowing dry-run in stress/test_governance.py (25 cases). Not
  a freeze gate; nothing at the window uses it, and a flaw found in it
  during the window is a fix, not a restart. **Retirement** (the `retires`
  retraction record that derives `status: retired`) ships with it.
- **Durability & anchoring — SETTLED 2026-07-19 (FD-33,
  docs/durability.md).** Mirrors live before the window: Software
  Heritage archived (snapshot c65a549a…) and the GitLab push mirror
  public at gitlab.com/satyakosh/satyakosh (full signed history;
  session workflow pushes both remotes). OpenTimestamps adopted —
  the genesis hash gets its .ots stamp at freeze (add to the freeze
  checklist); per-batch anchoring plus a quarterly heartbeat floor
  with a written tightening path. Remaining activation-era item:
  Zenodo versioned DOI at rc1, as already sequenced.

- **Post-freeze hash gating (issue #7 follow-up, 2026-07-19).** The repo
  tree is mixed CRLF/LF, including genesis-hashed prose documents.
  Functionally safe under `.gitattributes * -text` (committed bytes are
  canonical and genesis hashes compute over them), but one future
  "normalize line endings" commit after the freeze would silently
  invalidate every genesis-declared document hash — today the only
  guard is `tools/genesis_hashes.py`, which is report-only. After the
  freeze: (1) make the genesis-hash check CI-GATING for the
  hash-enumerated files (fail the build if any frozen document's bytes
  no longer match its genesis-declared digest, honoring
  doc_supersession records); (2) record the explicit decision NOT to
  clean up the mixed endings. `verify.py --repo` already provides the
  check mechanism.

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
