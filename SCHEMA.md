# Satyakosh — Ledger Schema 1.0.0-rc.1

**Status:** Release candidate. Frozen at Genesis Window open; adversarial
review of this document is in scope for the window. A hash-breaking flaw
found during the window restarts the window; cosmetic findings are queued
for the next minor version.

**Recovery note (2026-07-15):** this document was reconstructed after loss
of the local working copy, from verbatim session transcripts where
available and from the locked decision record elsewhere. It must be
re-reviewed end-to-end by the founder before its hash is computed for
genesis. See RECOVERY_NOTES.md.

Satyakosh (सत्यकोश, "treasury of truth") is a permanent, tamper-evident,
cryptographically hash-chained public ledger of verified facts. This
document is the canonical specification of what goes into the chain and how
it is hashed. Everything else — prose, translations, URLs, names — lives
outside the seal and may be corrected freely without touching the chain.

Jargon is explained on first use. "Sealed" means: written into the chain,
hashed, and never editable afterward. "Canonical bytes" means: the one
exact byte sequence that represents a record for hashing.

---

## 1. Design invariants

1. **Immutability over editability.** Sealed records are never edited.
   A correction is a new version that `supersedes` the old one.
2. **Language independence.** Only structured, language-neutral data is
   hashed: opaque IDs, numeric strings, unit codes, dates, enums. No
   English (or any language) prose exists inside a sealed `fact` record.
   All human-readable renderings live in unsealed registry and label
   files. Every human language is a rendering layer, equal before the
   chain.
3. **Trust through process.** Every sealed fact carries the hash of its
   own review history (`process_hash`). A fact proves not only that it
   hasn't changed, but that how it got in hasn't been rewritten.
4. **Everything sealed as a `fact` passed the pipeline.** No exceptions,
   including the first records. The genesis record is typed `genesis`
   precisely so this invariant holds from record zero.
5. **No contributor identity inside anything hashed.** Contributors appear
   only as opaque `SK-USR-` IDs in frozen process files. The mapping from
   ID to name lives in an unsealed, deletable registry (opt-in),
   preserving right-to-erasure without breaking the chain. This rule is
   about contributors, not fact subjects: a public figure may be the
   subject or object of a fact. **One deliberate exception:** the genesis
   inscription names the founder and carries a dedication, with informed
   consent on record — a monument, not a fact.
6. **Nothing sealed depends on unsealed files.** The rules in force at any
   chain position are derivable from the chain alone (genesis state plus
   all preceding governance records).
7. **Don't seal the derivable.** Anything computable from sealed data
   (relations like "north of", dependence classifications, aggregate
   views) is a consumer query, never a primary record.
8. **External standards over house registries.** Where a language-neutral
   authoritative code standard exists, adopt it: UCUM (units), ISO 3166
   (jurisdictions), ISO 8601 + astronomical year numbering (dates), InChI
   (chemical identity), Unicode code points (character identity).
   Adoptions are announced via governance records.

---

## 2. Record types

| `record_type` | Purpose | Pipeline? |
|---|---|---|
| `genesis` | Founding record: inscription, founding ruleset & whitelist enumeration | no (by type) |
| `fact` | A verified fact (semantic triple + jacket) | always |
| `governance` | A witnessed change to whitelist membership, pipeline policy version, schema minor version, standards adoption, or any founding-document hash | no (by type; announced & logged) |
| `inscription` | Commemorative structured record (e.g. Genesis Window scoreboard) | no (by type) |

One chain, shared sealing mechanics (§8). The genesis record enumerates the
founding whitelist and ruleset hashes; every later change is a `governance`
record. A verifier reconstructs the rules governing any fact from the chain
alone.

---

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
fact (`triple_hash` exact lookup — duplicate detection is a hash lookup,
never fuzzy text matching).

### 3.1 Subject

An entity ID. Ring 1 v1 convention: subjects are quantity-entities ("the
boiling temperature of water"). Entity IDs are opaque, append-only, never
reused or re-pointed. Entity *equivalence* is a registry `same_as` link —
never a sealed fact (identity facts are symptoms of registry duplicates).

### 3.2 Predicate

V1 defines exactly one: `SK-PRED-000001` = *subject has the quantity value
given by object, under the stated conditions*. New predicates (e.g.
*instance of*, *authored by*, controlled negative predicates such as *is
incapable of*) are additive via governance records. Predicate registry
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
  **tie-break by the JCS bytes of the condition object** (two conditions
  may share a property, e.g. a min and max temperature).
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

---

## 4. The sealed fact record

| Field | Type | Notes |
|---|---|---|
| `record_type` | `"fact"` | |
| `fact_id` | string | `SK-R<ring>-<DOMAIN>-<12hex>` (§6) |
| `triple_hash` | string | full SHA-256 of canonical triple (§7) |
| `version` | int | metadata-only supersession increments this |
| `supersedes` | string \| null | `fact_id@version`; may reference a different fact_id (triple-changing supersession, e.g. a CODATA revision) |
| `triple` | object | §3 |
| `ring` | int | 1 in v1 |
| `truth_type` | enum | `always \| conditional \| seasonal \| periodic` |
| `valid_from` / `valid_until` | date \| null | validity window |
| `valid_until_expected` | bool | distinguishes "timeless" from "surely ends, date unknown" |
| `sources` | array | `{source: "SK-SRC-…", edition, retrieved}`, sorted by source ID |
| `derivation` | object | `{type, …}`; `derived_from` (optional array of fact_ids) seals the dependency graph; `derived_exact` requires non-empty `derived_from`; Ring 1 derivations include a runnable recipe |
| `process_hash` | string | SHA-256 of the raw review-file bytes |
| `status` | enum | `sealed \| superseded` |
| `created` | timestamp | UTC |
| `content_hash` | string | §7.4 |
| `prev_record_hash` | string | §8 |

No `statement` field exists. No `claim_class` field exists (coarse class is
a derived consumer view — `docs/derived_views/claim_class.md`; finer grain,
if ever needed, arrives by refining `derivation.type` values via
governance).

---

## 5. Registries (unsealed, append-only on IDs)

| File | Holds | ID form |
|---|---|---|
| `registries/entities.json` | quantity-entities, condition properties; `condition_dependent` flag; `same_as` links; labels per language | `SK-ENT-NNNNNN` |
| `registries/predicates.json` | predicate definitions incl. epistemic hedges | `SK-PRED-NNNNNN` |
| `registries/sources.json` | whitelisted publishers; `rings` applicability | `SK-SRC-NNNNNN` |
| `registries/contributors.json` | opt-in, deletable ID→name map | `SK-USR-NNNNNN` |

IDs are never reused or re-pointed. Labels and descriptions are freely
correctable. The predicate registry's founding snapshot is hashed into
genesis (§9) because predicate definitions are semantically load-bearing
for every sealed fact.

---

## 6. Fact IDs (content-addressed)

```
SK-R1-PHYS-9f3a2c81d4e0
│  │   │    └── first 12 hex chars of triple_hash
│  │   └────── domain of the subject entity (courtesy tag)
│  └────────── ring
└───────────── namespace
```

- The **canonical identity is the hash**; the ring and domain segments are
  human affordances derived from sealed/registry data and carry no
  identity.
- The full `triple_hash` is sealed alongside the ID, so the ID is
  verifiable: recompute the canonical triple's hash, check the prefix.
- 12 hex chars = 48 bits: expected first collision ≈ 16M records.
  **Collision rule:** if a new fact's 12-char prefix collides with an
  existing fact_id, the new fact takes a 16-char suffix. (Full-hash
  collisions are treated as impossible; a demonstrated SHA-256 collision
  is a migrate-the-chain event, as it is for every system using SHA-256.)
- A superseding version keeps the same `fact_id` with `version`
  incremented **iff** its canonical triple is unchanged (metadata-only
  supersession). If the triple changes (e.g. CODATA revises G), the new
  triple yields a new `triple_hash`, hence a **new fact_id**; the old
  fact's status becomes `superseded` via a terminal version pointing
  forward. Claim identity and record identity stay aligned.

---

## 7. Canonical serialization

Determinism rule: **same claim → same bytes → same hash.** A stray space, a
reordered key, or a re-encoded character must be impossible in canonical
form.

### 7.1 Base: RFC 8785 (JSON Canonicalization Scheme)

Canonical form of any hashed object is its RFC 8785 serialization:
lexicographically sorted keys, minimal string escaping, UTF-8 encoding, no
insignificant whitespace.

**Schema-level constraint that keeps JCS trivial: no JSON floats exist
anywhere in sealed records.** The only JSON numbers permitted are small
integers (`version`, `ring`). All measured/defined values are strings.

### 7.2 Content normalization (applied before serialization)

1. All strings are Unicode NFC-normalized. Canonical bytes are NFC UTF-8
   chain-wide. **Additionally, `fact` records in v1 must be pure ASCII.**
   This is an intake tripwire, not a content rule: every vocabulary
   admissible in a v1 fact record (opaque IDs, UCUM, ISO codes, the §7.3
   grammar, enums, dates) is structurally ASCII, so a non-ASCII byte in a
   fact record can only be evidence of error or attack (homoglyphs,
   invisible characters, bidi controls). The genesis record is the
   deliberate exception (it carries the only prose on the chain). If a
   future governance record activates a type or standard with legitimate
   non-ASCII codes, the tripwire narrows by governance record.
2. Timestamps: UTC only, `YYYY-MM-DDTHH:MM:SSZ`. Dates: `YYYY-MM-DD`.
3. Hashes: lowercase hex.
4. `conditions` arrays: sorted by `property` ID (ascending, bytewise);
   tie-break by JCS bytes of the condition object.
5. `sources` arrays: sorted by `source` ID (ascending, bytewise).
6. UCUM codes: verbatim, case-sensitive (UCUM case is semantic).

### 7.3 Value grammar (for `value` and `uncertainty` strings)

One byte-form per (number × precision):

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

`triple_hash` = SHA-256(JCS(triple)) ·
`content_hash` = SHA-256(JCS(record − {content_hash, prev_record_hash})) ·
`process_hash` = SHA-256(JCS(review file)) — the canonical review-file
format is `docs/review_file_format.md` (versioned inside each review
file; evolves by governance record).

---

## 8. Chain mechanics

Record 0 = genesis, `prev_record_hash` = 64 zeros.
`chain_link(i) = SHA-256(content_hash(i) ‖ chain_link(i−1))` over hex
strings; latest link = **chain head**, published on site, mirrors
(Internet Archive, Zenodo), and periodic external anchors. Canonical
store: public GitHub repo (Git history = independent second layer).
Merkle-root periodic sealing: adopted in principle, deferred until scale
demands.

---

## 9. Genesis record

The genesis record enumerates the complete founding ruleset, so that a
verifier can reconstruct the rules governing fact #1 from the chain alone:

- the founding **inscription** — the one deliberate prose exception on the
  chain (a monument, not a fact; sealed once, never edited): mission
  passage, cultural invocation with citation, founder name, dedication,
  founding date. NFC UTF-8.
- `schema_version` + `schema_hash` (SHA-256 of frozen SCHEMA.md)
- `pipeline_policy_version` + `pipeline_policy_hash`
- `scope_hash` (frozen SCOPE.md)
- `admissibility_map_hash` (SHA-256 of JCS(`rules/admissibility_map.json`))
- `mandatory_conditions_hash` (SHA-256 of
  JCS(`rulesets/mandatory_conditions.json`))
- `predicates_founding_hash` (SHA-256 of JCS(`registries/predicates.json`),
  founding snapshot)

Hash convention for founding documents: prose documents (`.md`) hash as
their raw frozen file bytes; machine-readable JSON documents hash as
their RFC 8785 (JCS) serialization.
- the founding **whitelist, inline** (machine-readable `SK-SRC-` entries
  with publisher and ring applicability — in the record, not referenced)
- chain fields (§8)

`ledger.py` refuses to seal a genesis containing placeholder markers,
non-hex hash fields, or empty inscription strings; it also refuses if any
hash-enumerated ruleset contains placeholder markers in operative fields.

---

## 10. Governance records

Sealed on: whitelist add/remove/ring-change · pipeline policy version
change · schema minor version · external-standard adoption · intake
ruleset change (admissibility map; mandatory-condition map) ·
**supersession of any founding-document hash**. Payload: machine-readable
delta + effective-from. The rules governing any fact = genesis state ⊕ all
governance records preceding it.

Version numbers track the canonical-byte contract: byte-affecting changes
bump the minor version; byte-neutral edits are rc revisions pre-freeze;
witnessed-ruleset content changes are governance records and never trigger
version bumps.

---

## 11. Validation & admissibility (enforced by `ledger.py`)

**Structural:** required fields; types; registry existence of all IDs;
object/condition typing per §3.3–3.4 (v1 gate: `quantity` only); value &
uncertainty grammar (§7.3); UCUM code check (v1: a closed whitelist of
founding-scope codes in the reference implementation, expanded with
proposals); condition sort + tie-break;
mandatory-condition satisfaction per the mandatory-condition map in force
at this chain position (first enforced at intake per §3.4); source sort;
date/timestamp formats; ASCII-only canonical bytes for `fact` records
(§7.2; genesis is NFC UTF-8); fact_id prefix ↔ `triple_hash`
recomputation; no duplicate `triple_hash` among non-superseded facts;
`derived_from` non-empty for `derived_exact`; **near-duplicate flag**
(same subject+predicate+conditions, different unit → human review:
possible unit-converted duplicate — a warning, not a byte rule).

**Admissibility:** the fact's `derivation.type` must map to SEAL for its
ring in the admissibility map in force at its chain position; all sources
must be whitelisted for that ring.

---

## 12. Drafting history

Internal draft lineage (v0 → v2.0 → v2.1 → v2.1-rc2) preceded the first
public version. Public versioning starts at 1.0.0; see CHANGELOG.md. The
canonical-byte contract tested in the ~9,000-record volume test is
unchanged by the renumbering.
