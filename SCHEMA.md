# Satyakosh — Ledger Schema 1.0.0 (Release Candidate — freezes at Genesis Window open)

> *Restored 2026-07-17 from the recovered 2026-07-10 original (pre-loss
> bytes; see RECOVERY_NOTES.md and docs/rebuild_divergence_report.md);
> post-loss amendments re-applied: A1–A4, the founding-document hash
> doctrine (FD-12), the review-file format pointer (A18/FD-16), and the
> v1 UCUM whitelist wording.*

Satyakosh is a permanent, tamper-evident, hash-chained public ledger of
verified facts. This document canonically specifies what enters the chain
and how it is hashed. Everything human-readable lives outside the seal.

**Freeze semantics:** this RC freezes at Genesis Window open. Adversarial
review of this document is in scope for the window: a hash-breaking flaw
found during the window is fixed and restarts the window; cosmetic findings
queue for the next minor version. After the first seal, changes to this document are additive
minor versions announced via `governance` records (§10).

**Versioning rule:** the version number tracks the canonical-byte
contract. Byte-affecting changes bump the minor version (pre-seal,
restarting any open window); byte-neutral edits are rc revisions
pre-freeze and governance-announced additive minors post-seal; content
changes to witnessed rulesets (whitelist, admissibility map,
mandatory-condition map) are governance records, never version bumps.

**Drafting history:** internal drafts (v0, v2.0, v2.1 — July 2026)
preceded this first public release and were renumbered 1.0.0 at the first
commit; the bytes are identical to internal v2.1. See `CHANGELOG.md`.

---

## 1. Design invariants

1. **Immutability.** Sealed records are never edited; corrections are new
   records that supersede old ones.
2. **Language independence.** Sealed bytes contain only opaque IDs, code
   strings from adopted external standards, normalized numeric strings,
   dates, and enums — no natural-language prose. v1 `fact`-record
   canonical bytes are consequently pure ASCII — an intake tripwire, not
   a style rule: a non-ASCII byte in a fact record can only be evidence
   of error or attack (homoglyphs, invisible characters, bidi controls).
   The genesis record is the deliberate NFC UTF-8 exception, carrying
   the only prose on the chain. *(Scoped by amendment A1; see §7.2.)*
3. **Trust through process.** Every sealed fact carries the hash of its
   complete review history (`process_hash`).
4. **Witnessed governance.** The ledger seals claims and evidence-of-
   governance — never policy itself. Policy may evolve; every evolution is
   a sealed `governance` record, so the ruleset in force for any fact is
   determined by its chain position. Policy fossilized is brittle; policy
   invisible is capturable; policy witnessed is correct.
5. **Everything typed `fact` passed the full pipeline.** No exceptions,
   from record one. Genesis, governance, and inscription records are
   distinct types precisely to preserve this.
6. **No contributor identity inside anything hashed.** Contributors appear
   only as opaque `SK-USR-` IDs in frozen process files; the ID→name map is
   unsealed, opt-in, and erasable (GDPR/DPDP-compatible). *Fact subjects and
   objects may be public entities, including people* ("PM of India — held
   by — [person-entity]"); erasure law applies to their unsealed labels
   exactly as for any entity. **One deliberate exception:** the genesis
   inscription names the founder and carries a dedication, with informed
   consent on record — a monument, not a fact. *(Amendment A2.)*
7. **Don't seal the derivable.** Anything computable from sealed data
   (relations like "north of", dependence classifications, aggregate views)
   is a consumer query, never a primary record.
8. **External standards over house registries.** Where a language-neutral
   authoritative code standard exists, adopt it: UCUM (units), ISO 3166
   (jurisdictions), ISO 8601 + astronomical year numbering (dates), InChI
   (chemical identity), Unicode code points (character identity).
   Adoptions are announced via governance records.

## 2. Record types

| `record_type` | Purpose | Pipeline? |
|---|---|---|
| `genesis` | Founding record: inscription, founding ruleset & whitelist enumeration | no (by type) |
| `fact` | A verified fact (semantic triple + jacket) | always |
| `governance` | A witnessed change to whitelist membership, pipeline policy version, schema minor version, standards adoption, or any founding-document hash | no (by type; announced & logged) |
| `inscription` | Commemorative structured record (e.g. Genesis Window scoreboard) | no (by type) |

One chain, shared sealing mechanics (§8). The genesis record enumerates the
founding whitelist and ruleset hashes; every later change is a
`governance` record. A verifier reconstructs the rules governing any fact
from the chain alone.

## 3. The semantic triple

```json
{
  "subject":   "SK-ENT-000001",
  "predicate": "SK-PRED-000001",
  "object":    { "type": "quantity", "value": "2.99792458e8", "unit": "m/s",
                 "exact": true, "uncertainty": null },
  "conditions": []
}
```

The triple is the claim's canonical identity: same canonical triple = same
fact (`triple_hash` exact lookup).

### 3.1 Subject
An entity ID. Ring 1 v1 convention: subjects are quantity-entities ("the
boiling temperature of water"). Entity IDs are opaque, append-only, never
reused or re-pointed. Entity *equivalence* is a registry `same_as` link —
never a sealed fact (identity facts are symptoms of registry duplicates).

### 3.2 Predicate
V1 defines exactly one: `SK-PRED-000001` = *The subject has the quantity
value given by the object, under the stated conditions.* New predicates
(e.g. *instance of*, *authored by*, controlled negative predicates such as
*is incapable of*) are additive via governance records. Predicate registry
definitions carry any epistemic hedge the predicate implies (a causal
predicate's definition states its probabilistic character); the triple
never launders a hedged claim into a flat one.

### 3.3 Object — the typed union
`object.type` is a discriminated union. **v1 validation admits only
`quantity`; the union's shape is frozen now so later types are additive
(old hashes never contain them):**

| type | fields | status |
|---|---|---|
| `quantity` | `value` (string, §7.3), `unit` (UCUM code; `"1"` if dimensionless), `exact` (bool), `uncertainty` (string in same unit \| null) | **v1 active** |
| `entity` | `id` ("SK-ENT-…") **or** `standard` + `code` (e.g. `"iso3166-1a2"`, `"IN"`) | reserved (Ring 2) |
| `date` | `value` (ISO 8601, astronomical year numbering for BCE), `precision` (`day\|month\|year\|decade\|century`), `calendar` (default `"gregorian"`) | reserved (Ring 2) |
| `text` | `value`, `lang` (BCP 47) | reserved; gated off — lexical facts are out of scope (SCOPE.md) |

### 3.4 Conditions — typed, sorted, mandatory-when-required
Each condition is `{ "property": "SK-ENT-…", "object": { …typed union… } }`
— the same union as §3.3 (so jurisdictions, calendars, temperature scales,
reference models, and methods are all expressible).

- **Canonical order:** sort by `property` ID (bytewise ascending);
  **tie-break by the JCS bytes of the condition object** (two conditions may
  share a property, e.g. a min and max temperature).
- **Model/frame is an explicit condition,** not smuggled through the source
  edition: temperature scale (ITS-90), geodetic model (WGS84), etc., as
  entity-valued conditions when the claim depends on them.
- **Mandatory-condition rules** are keyed on `derivation.type` and subject
  class, enforced at intake (§11): e.g. statistical claims require a method
  condition; counts-over-discovered-sets require a "known as of" epoch;
  reference-value claims require their convention. A fact missing a
  mandatory condition never enters review. The founding rule map is
  `rulesets/mandatory_conditions.json`, sealed by hash in the genesis
  record (§9); changes are governance records (§10). A requirement is
  satisfied iff at least one condition's `property` matches the required
  property ID.

## 4. The sealed fact record

| Field | Type | Notes |
|---|---|---|
| `record_type` | `"fact"` | |
| `fact_id` | string | `SK-R<ring>-<DOMAIN>-<12hex>` (§6) |
| `triple_hash` | string | full SHA-256 of canonical triple (§7) |
| `version` | int | metadata-only supersession increments this |
| `supersedes` | string \| null | `fact_id@version`; **may reference a different fact_id** (triple-changing supersession, e.g. a CODATA revision) |
| `triple` | object | §3 |
| `ring` | int | v1: must be 1 |
| `valid_from` / `valid_until` | date \| null | claim content |
| `terminality` | `"none" \| "expected" \| "scheduled"` | distinguishes timeless (c) from surely-ends-date-unknown (an office) from dated expiry |
| `sources` | array | `{source: "SK-SRC-…", edition, retrieved}`; sorted by source ID; every source must be whitelist-active *at this chain position* |
| `derivation` | object | §4.1 |
| `process_hash` | string | SHA-256 of the frozen review file (§7.4) |
| `status` | `"sealed" \| "superseded" \| "retired"` | always `sealed` at seal time; `superseded` and `retired` are *derived*, never written into a sealed record (see below) |
| `created` | UTC `YYYY-MM-DDTHH:MM:SSZ` | |
| `content_hash`, `prev_record_hash` | strings | §8 |

**Removed during drafting (July 2026 taxonomy review):**
- `truth_type` — conflated stability with dependence. Dependence is
  derivable from structure (invariant 7); the stability *forecast* is
  editorial and lives unsealed in the attestation layer as its freshness
  contract. The founding always/conditional/seasonal/periodic taxonomy is
  satisfied structurally by conditions + validity window + terminality +
  attestation.
- `claim_class` — was Dimension A stored twice. One sealed field
  (`derivation.type`) now carries it; admissibility is a validation mapping
  (§11), witnessed via governance records, not a stored label. Coarse
  classification is a derived consumer view
  (`docs/derived_views/claim_class.md`).

**Derived status (never a written verb).** A sealed record's `status` is
always `sealed`; it is never edited. The other two states are read off
the chain:
- **superseded** — a later sealed record names this one in `supersedes`
  (`fact_id@version`). This mechanism exists and is validated (§6, §11).
- **retired** — a later `governance` retraction record names this fact
  (a `retires: "fact_id@version"` payload, derived exactly as
  supersession is). Retirement is a governance-era mechanism: it ships
  with the governance engine (SCHEMA §10 / PIPELINE_POLICY), which is
  not yet implemented. Until then no fact can become retired, and the
  enum value is a forward declaration — like the reserved object types.
  `ledger.py` therefore refuses `retired` as a *seal-time input*.

A born-with-a-closed-window fact (a `valid_until` already in the past at
seal time) is **valid and intentional**: it records a quantity that held
over a bounded historical window (the common shape of a value later
revised by supersession). The validator does not reject it — a rule that
did would refuse legitimate historical facts.

### 4.1 Derivation
```json
{ "type": "laboratory_measurement", "script": null, "derived_from": [] }
```
- `type` ∈ `si_exact_definition | defined_convention | mathematical_proof |
  laboratory_measurement | derived_exact | statistical_analysis |
  documentary_evidence | causal_inference | institutional_declaration`
  (the full Dimension A vocabulary; §11 maps each to an admissibility
  verdict — only the first five can seal in v1/Ring 1).
- `script`: null, or SHA-256 of a runnable verification script at
  `derivations/<triple_hash>.py` (sealing the hash freezes the file; the
  review file also pins it — docs/review_file_format.md). `ledger.py`
  validates only the hash *form* (a record is bytes, not a filesystem);
  that the artifact **exists, matches the hash, and runs clean** is an
  intake-pipeline requirement (PIPELINE_POLICY P3; CI runs every pinned
  recipe) so no fact seals pointing at a missing or drifted recipe.
- `derived_from`: fact_ids this fact's value/exactness inherits from
  (e.g. R ← {N_A, k}). Seals the dependency graph; `derived_exact`
  requires it non-empty, and every referenced fact must already be
  sealed.

## 5. Unsealed layers (registries, labels, attestations)

Append-only on IDs; freely correctable otherwise.

- `registries/entities.json` — `SK-ENT-…` → domain, labels{lang}, description,
  `same_as`/external_ids (Wikidata etc.). Precise entity *scoping* lives in
  the description and is governance-critical for Rings 2–3.
- `registries/predicates.json` — definitions incl. epistemic hedges.
- `registries/sources.json` — **the whitelist**: `SK-SRC-…` → name,
  publisher, urls, editions[], `rings` (applicability). Membership changes
  only via governance records; this file mirrors chain state for
  convenience.
- `registries/contributors.json` — `SK-USR-…` → handle, opt-in, erasable.
- `labels/facts/<fact_id>.json` — statements in any languages, pretty
  notation ("299 792 458 m/s"), derivation prose.
- **Attestation layer** (separate service, out of chain): signed,
  timestamped "verified-current-as-of" statements referencing fact_ids or
  attestation-only claims (offices, known-counts, empirical negatives).
  This layer is also the commercial real-time product; the chain stays free.

## 6. Fact IDs (content-addressed)

`SK-R1-PHYS-9f3a2c81d4e0` — namespace, ring, subject-domain tag (courtesy,
frozen at seal; registry reclassification never rewrites it — hash is
identity), then the first 12 hex of `triple_hash` (48 bits; expected first
collision ≈ 16M records). On a 12-char prefix collision the newer fact takes
16 chars. A full SHA-256 collision is a migrate-the-chain event, as for
every SHA-256 system.

## 7. Canonical serialization

**Rule zero: same claim → same bytes → same hash.**

### 7.1 Base
RFC 8785 (JCS): sorted keys, minimal escaping, UTF-8, no insignificant
whitespace. Schema constraint keeping JCS trivial: **no JSON floats
anywhere**; the only JSON numbers are small integers (`version`, `ring`).

### 7.2 Content normalization
All strings NFC-normalized; canonical bytes are NFC UTF-8 chain-wide.
**Additionally, `fact` records in v1 must be pure ASCII** — the intake
tripwire of invariant 2: every vocabulary admissible in a v1 fact record
(opaque IDs, UCUM, ISO codes, the §7.3 grammar, enums, dates) is
structurally ASCII, so a non-ASCII byte can only be error or attack. The
genesis record is the deliberate exception (the only prose on the chain).
If a future governance record activates a type or standard with
legitimate non-ASCII codes, the tripwire narrows by governance record.
*(Amendment A1.)*
UTC timestamps `YYYY-MM-DDTHH:MM:SSZ` · dates `YYYY-MM-DD` · lowercase
hex · conditions sorted per §3.4 · sources sorted by ID · UCUM verbatim
case-sensitive.

### 7.3 Value grammar — **normalized scientific notation**
An earlier draft grammar admitted semantic duplicates (`"1000"` vs `"1e3"` vs
`"1.0e3"`: same number, different bytes, different hashes — duplicate
detection silently defeated). The grammar therefore mandates one byte-form per
(number × precision):

```
value    := "0"  |  mantissa "e" exponent
mantissa := ["-"] nonzero-digit [ "." digits ]
exponent := "0" | ["-"] nonzero-digit digits*
```

- Exactly one nonzero digit before the point; lowercase `e` **always
  present** (except literal `"0"`); no `+`; no leading zeros in the
  exponent.
- **Significant figures are sacred and are the mantissa's digit count.**
  Trailing zeros in the fraction are preserved as published
  (`"6.67430e-11"` ≠ `"6.6743e-11"` — different precision claims).
  Normalization never adds, drops, or rounds digits; the proposer
  transcribes the source's digits into this form; review checks the
  transcription. `-0` and all-zero mantissas are forbidden.
- Renderings ("299 792 458 m/s") live in labels; ugly-but-unambiguous wins
  inside the hash.

### 7.4 What gets hashed
`triple_hash` = SHA-256(JCS(triple)) · `content_hash` = SHA-256(JCS(record −
{content_hash, prev_record_hash})) · `process_hash` = SHA-256(JCS(review
file)) — the canonical review-file format is `docs/review_file_format.md`
(versioned inside each review file; evolves by governance record).

**Founding-document hash doctrine (FD-12):** prose documents (`.md`)
hash as their raw frozen file bytes; machine-readable JSON documents
hash as their RFC 8785 (JCS) serialization.

## 8. Chain mechanics

Record 0 = genesis, `prev_record_hash` = 64 zeros.
`chain_link(i) = SHA-256(content_hash(i) ‖ chain_link(i−1))` over hex
strings; latest link = **chain head**, published on site, mirrors
(Internet Archive, Zenodo), and periodic external anchors. Canonical store:
public GitHub repo (Git history = independent second layer). Merkle-root
periodic sealing: adopted in principle, deferred until scale demands.

## 9. Genesis record

The genesis record enumerates the complete founding ruleset, so that a
verifier can reconstruct the rules governing fact #1 from the chain alone
*(amendment A3)*:

- the founding **inscription** — the one deliberate prose exception on the
  chain (a monument, not a fact; sealed once, never edited): mission
  passage, cultural invocation with citation, founder name, dedication,
  founding date. NFC UTF-8. The founding date is inscription prose in
  dual-calendar form (Vikram Samvat first, then Gregorian, calendars
  named — FD-27) and must contain exactly one embedded Gregorian ISO
  date (`YYYY-MM-DD`) as the machine-readable anchor.
- `schema_version` + `schema_hash` (SHA-256 of frozen SCHEMA.md)
- `pipeline_policy_version` + `pipeline_policy_hash`
- `scope_hash` (frozen SCOPE.md)
- `admissibility_map_hash` (SHA-256 of JCS(`rules/admissibility_map.json`))
- `mandatory_conditions_hash` (SHA-256 of
  JCS(`rulesets/mandatory_conditions.json`))
- `predicates_founding_hash` (SHA-256 of JCS(`registries/predicates.json`),
  founding snapshot)
- the founding **whitelist, inline** (machine-readable `SK-SRC-` entries
  with publisher and ring applicability — in the record, not referenced)
- chain fields (§8)

`ledger.py` refuses to seal a genesis containing placeholder markers,
non-hex hash fields, or empty inscription strings — in the record itself
or in the *operative* fields of any hash-enumerated ruleset (commentary
fields exempt). The draft genesis lives at `genesis_record.draft.json`
(repo root) until the Genesis Window opens.

## 10. Governance records

Sealed on: whitelist add/remove/ring-change · pipeline policy version
change · schema minor version · external-standard adoption · intake
ruleset change (admissibility map; mandatory-condition map) ·
**supersession of any founding-document hash** *(amendment A4)*.
Payload: machine-readable delta + effective-from. The rules governing any
fact = genesis state ⊕ all governance records preceding it.

## 11. Validation & admissibility (enforced by `ledger.py`)

**Structural:** required fields; types; registry existence of all IDs;
object/condition typing per §3.3–3.4 (v1 gate: `quantity` only);
predicate object-type admission (the registry's `object_types`
declaration is enforced — a predicate admitting only dates never seals
a quantity); value &
uncertainty grammar (§7.3); UCUM code check (v1: a closed whitelist of
founding-scope codes in the reference implementation, expanded with
proposals); per-derivation-type minimum **distinct-institution** source counts
when the mandatory-conditions ruleset declares `source_count_rules`
(RING2 §3.1 independence — the count is over distinct source IDs,
never entries; v1: none declared, default 1; Ring-2 activation sets
values by governance); no duplicate source entries;
condition sort + tie-break (duplicate condition properties are
legitimate for ranges and raise a review flag, never a refusal);
source sort; date/timestamp
formats; ASCII-only canonical bytes for `fact` records (§7.2; genesis is
NFC UTF-8); fact_id prefix ↔ `triple_hash` recomputation; no duplicate
`triple_hash` among non-superseded facts; **near-duplicate flag** (same
subject+predicate+conditions, different unit → human review: possible
unit-converted duplicate — a warning, not a byte rule).

**Admissibility map (founding version, as data at
`rules/admissibility_map.json`; changes = governance records):**

| `derivation.type` | verdict |
|---|---|
| si_exact_definition, defined_convention, mathematical_proof, laboratory_measurement, derived_exact | **SEAL (Ring 1, v1)** |
| statistical_analysis, documentary_evidence | RING-2 PENDING (enters review only when Ring 2 governance record exists) |
| causal_inference | BLOCKED (requires evidence-framework governance record) |
| institutional_declaration | BLOCKED (independence principle; see SCOPE.md) |

**Process:** `process_hash` matches the frozen review file; review shows
completed ≥30-day window, all objections resolved, and (for
`derived_exact`) all `derived_from` facts already sealed.

Scope refusals (rules, relations, identity, fiction, feeds, lexicon,
self-reference) are specified in `SCOPE.md` and cited at intake — refusal is
always principled and citable, never ad-hoc.
