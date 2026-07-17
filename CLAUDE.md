# CLAUDE.md — Satyakosh (सत्यकोश)

Guidance for Claude (Claude Code, claude.ai sessions, and any AI assistant)
working in this repository. Read this file fully before editing anything.

## What this project is

Satyakosh is a permanent, tamper-evident, cryptographically hash-chained
public ledger of verified facts — a neutral trust anchor designed to outlive
its tools, its maintainers, and its era. It is an institution in the spirit
of the Svalbard Seed Vault or the Internet Archive, not a product.

The single most important property of this codebase: **some bytes, once
sealed, can never change.** Every convention below exists to protect that
property. When in doubt, do less, and ask.

## Absolute invariants — never violate, never "fix"

1. **Sealed records are immutable.** Never edit, reformat, re-serialize,
   re-hash, or "clean up" anything in the sealed ledger — including
   whitespace, key order, or typos. A typo in a sealed record is a permanent
   feature. Corrections happen only through new records (supersession or
   governance), never through edits.
2. **Canonical bytes are law.** Canonical serialization is RFC 8785 (JCS);
   content hashing is SHA-256. Never substitute a different JSON serializer,
   canonicalization scheme, or hash. Never let a formatter, linter, or IDE
   touch canonical-form files.
3. **Numeric values are decimal strings, never JSON floats.** No exceptions,
   including in tests and examples.
4. **`fact` records are pure ASCII in canonical form.** This is an intake
   tripwire against homoglyph/invisible-character attacks, not a style rule.
   Non-ASCII bytes in a fact record are an attack signature. The genesis
   record is the deliberate exception (NFC-normalized UTF-8) and carries the
   only prose on the chain.
5. **No human language inside sealed bytes.** Facts are semantic triples of
   opaque IDs (`SK-ENT-`, `SK-PRED-`, `SK-SRC-`) plus typed objects. All
   labels, in all languages, live in the unsealed labels layer. Every
   language is a rendering, equal before the chain. Never move a label into
   canonical form "for readability."
6. **No contributor identity inside hashed content.** Contributors appear
   only as opaque `SK-USR-` IDs (erasable via the opt-in registry). The
   genesis inscription (founder name, dedication) is the single, consciously
   consented exception.
7. **External standards over house registries.** Units are UCUM. Dates are
   ISO 8601. Jurisdictions are ISO 3166. Character identity is Unicode code
   points. Never invent a house code where a standard exists.
8. **Everything sealed as a `fact` passed the pipeline.** There is no seed
   bypass, no admin bypass, no "just this once." Genesis is a separate
   record type precisely so that this rule has no exceptions.
9. **Ring 1 sources are a closed whitelist**: CODATA (SK-SRC-000001),
   NIST (SK-SRC-000002), BIPM (SK-SRC-000003). Never derive or verify a
   fact from general web search. Ring 2/3 remain sealed-out until their
   governance machinery exists.

## Versioning discipline

- Public versioning starts at **1.0.0** (`1.0.0-rc.1` during the Genesis
  Window). Pre-public internal versions (v2.0, v2.1-rc2, PyPI 0.0.1) are
  visible prehistory; do not resurrect them in new documents.
- Version strings live **inside hashed bytes**. Any change to a
  canonical-byte-affecting rule bumps the minor version and requires a
  governance record post-seal. Byte-neutral edits are rc revisions before
  the freeze only.
- **Do not tag a v1.0.0 release until genesis is sealed clean.**
- PyPI: next release is `1.0.0rc1` (0.0.1 is already published and cannot
  be reused).

## Genesis freeze (current phase)

Six documents freeze at Genesis Window open; their SHA-256 hashes seal into
the genesis record: `SCHEMA.md`, `SCOPE.md`, `PIPELINE_POLICY.md`,
`admissibility_map.json`, `rulesets/mandatory_conditions.json`, and the
predicate registry snapshot. After the freeze, any change to these is a
publicly visible governance record. Treat all six as hash-critical: no
drive-by edits, no formatting passes, no "while I'm here" fixes.

The genesis record itself (`genesis_record.draft.json`) is fully specified
except the mission prose. Its locked fields — the Pavamana mantra, the
citation string, the founder name, the dedication (including the exact
bytes "Anaya Gangakhedkar"), the founding date 2026-07-07 — are decisions,
not drafts. Do not reword them.

## Working conventions with the founder

- **Stress-test before commit.** Pressure-test assumptions thoroughly;
  then lock decisions explicitly and record them. Decisions get names
  and audit trails: post-rebuild decisions are FD-entries in
  DECISIONS.md, appended in the same commit that applies them.
- **Only stop at genuine forks.** Mechanical derivations are not decisions
  needing ratification; do not pad reviews with fake choices.
- **Public-facing English is simple and short.** SCHEMA.md may be precise
  but must explain jargon on first use.
- **Session continuity is via the GitHub repo** (the canonical working
  copy). Never reconstruct hash-critical documents from memory or
  summaries — a plausible-but-divergent document is worse than a missing
  one. Ask for the real bytes.
- Do not fetch GitHub repo *tree pages* (blocked by robots.txt); use
  raw.githubusercontent.com URLs or the API.
- **The GitHub repo is the canonical working copy** (lesson of the
  2026-07-15 local-file loss). Push after every working session. Never
  let hash-critical documents exist only on one machine.

## Things Claude must never do in this repo

- Edit anything under a sealed ledger directory, ever.
- Reformat, prettify, or re-serialize canonical JSON.
- Convert decimal-string values to numbers.
- Add human-readable labels, names, or comments into canonical records.
- Introduce non-ASCII characters into `fact` records or their tooling
  output.
- Bypass or weaken the intake gate, the mandatory-conditions check, or the
  placeholder-refusal check in `ledger.py`.
- Invent facts, sources, or hashes. If a hash is not yet computable, leave
  an explicit placeholder that `ledger.py` will refuse to seal.

## License

Data (ledger, registries, labels, proposals): CC0.
Code: Apache-2.0.
