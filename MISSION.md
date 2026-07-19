# Satyakosh — Mission & Project Summary

> *Restored 2026-07-17 from the recovered 2026-07-10 original (pre-loss bytes; see RECOVERY_NOTES.md and docs/rebuild_divergence_report.md); status section updated.*

### As of July 2026 · Schema 1.0.0 release candidate (first public release)

---

## Mission statement

> **Satyakosh (सत्यकोश, "treasury of truth") is a permanent, tamper-evident
> public ledger of verified facts — a neutral trust anchor for an age in
> which machines mediate what humanity knows.**
>
> Every fact on the ledger carries its identity, its recipe, and its
> biography: its name is derived from its own content, its verification is
> independently re-runnable, and the complete history of how it earned its
> place — and of every rule that governed its admission — is sealed beside
> it. Nothing enters silently; nothing changes silently; nothing is ever
> paywalled out of the public record.
>
> Satyakosh does not decide what is true. It witnesses, permanently, what
> humanity's most rigorous processes have established — and exactly how.
> What the seed vault is to crops and the public archive is to the web,
> Satyakosh is to facts.

**Mission principles (each is load-bearing, none is decorative):**

1. **Open data is the moat.** The full ledger is forever downloadable and
   uncrippled. Fact IDs and canonical fields are never paywalled. Revenue
   comes from freshness, convenience, and attestation — never from access.
2. **Trust through process, not gatekeeping.** Verification is transparent,
   auditable, and re-runnable. The automated checker annotates; it never
   vetoes. Humans resolve disputes in public.
3. **Institutional independence.** No government mandates, no single-patron
   capture. The state may one day be an ordinary paying customer; it will
   never be a sponsor whose interests the ledger must serve.
4. **The ledger seals claims and evidence-of-governance — never policy
   itself.** Rules may evolve; every evolution is witnessed on the chain.
5. **Language independence.** Only structure is sealed. Every human language
   is a rendering layer, equal before the chain.
6. **Scope discipline.** Satyakosh refuses whole categories of representable
   content (rules, fiction, lexicons, news feeds, legal registries) because
   a trust anchor that tries to hold everything anchors nothing.

---

## Project summary

### The problem
AI systems increasingly mediate humanity's access to information while
training on, and citing, an internet whose reliability is degrading — partly
because of AI-generated content itself. There is no neutral, permanent,
machine-verifiable ground-truth layer that an AI (or a person) can check a
claim against and cryptographically confirm has not been altered. Satyakosh
is that layer. Primary first customers: AI labs, which need verifiable
ground-truth anchors for training, evaluation, and inference-time grounding.

### The design (schema 1.0.0)
- **Facts are semantic triples** — subject / predicate / typed object /
  typed conditions — plus a sealed jacket (ring, sources, derivation,
  validity window, process hash). Objects and condition values share one
  discriminated type union (`quantity | entity | date`, `text` reserved),
  so the schema extends to future fact categories without breaking changes.
- **Everything sealed is language-neutral bytes.** Prose, names, URLs, and
  translations live in unsealed registry/label files, freely correctable.
- **Facts are content-addressed.** A fact's ID contains a hash of its own
  canonical triple, making the name self-verifying and duplicate detection
  an exact lookup. Canonical serialization is RFC 8785 (JCS) plus strict
  content rules (normalized scientific-notation value grammar, sorted
  conditions with deterministic tie-break, UTC timestamps, no JSON floats).
- **Four interlocking chains of evidence:** the fact-chain (content +
  chain-linking), the process-chain (each fact seals the hash of its full
  review history), the governance-chain (every whitelist or ruleset change
  is itself a sealed record — the rules in force for any fact are determined
  by chain position), and Git's own commit history as an independent layer.
  Merkle-root periodic sealing is adopted in principle, deferred until scale
  demands it.
- **Rings gate ambition; derivation gates admissibility.** Ring 1
  (independently re-derivable) is the v1 scope, sourced exclusively from a
  sealed whitelist (CODATA / NIST / BIPM). A fact's `derivation.type` maps
  to an admissibility rule: observational, mathematical, and definitional
  claims may seal; statistical and documentary claims await Ring 2
  governance; causal and institutional claims are blocked pending an
  evidence framework; time-bound status lives in an unsealed, signed
  **attestation layer** — which is also the commercial real-time product.
- **The pipeline is open:** anyone proposes (GitHub PR) → automated
  whitelist check annotates, never vetoes ("publish under protest" is a
  visible flag, not a block) → public review with a ≥30-day dispute window
  → seal only after objections resolve. Unverified proposals remain in
  review indefinitely; they never seal and never disappear.
- **Genesis Window launch:** the first facts — including the founding seed
  set — pass through the real pipeline in public, with a bug-bounty-style
  scoreboard rewarding validated catches (errors, code flaws, canonical-form
  ambiguities). Top contributors are permanently inscribed on the chain via
  an `inscription` record (opt-in, pseudonymous IDs; names live in an
  erasable registry — right-to-erasure never conflicts with immutability).
  Every fact ever sealed, including fact #1, will have passed the full
  process: the founding invariant holds from record zero.

### Status (July 2026)
- **Provenance:** the local working copy was lost 2026-07-15 and the
  repository rebuilt, hardened through external adversarial review,
  and reconciled against the recovered originals — see
  RECOVERY_NOTES.md and DECISIONS.md. The GitHub repository is the
  canonical working copy.
- **Prototype:** v0 Python ledger built and tamper-detection demonstrated;
  schema 1.0.0 finalized after three semantic stress-test rounds (40
  categories, ~130 adversarial facts) plus a ~9,000-record mechanical volume
  test of the validator, serializer, chain, and admissibility gate.
- **Seed set:** restructured to the tiered plan (amendment A16): the
  seven SI defining constants hand-proposed and individually reviewed;
  the full CODATA 2022 set as one batch proposal (P11); condition-
  bearing exhibits; one deliberate refusal exhibit. Sealing awaits the
  Genesis Window per the pipeline invariant.
- **IP & namespace:** SATYAKOSH word mark filed in Classes 42, 9, 35
  (priority 7 July 2026, Formalities Chk Pass; examination expected
  ~Nov 2026–Jan 2027; Madrid Protocol decision due early Dec 2026).
  Domains (.com/.org/.in/.ai), GitHub org, PyPI, Hugging Face, and social
  handles secured.
- **Deliberately parked:** incorporation form (Pvt Ltd vs Section 8 vs
  hybrid), Discord — each awaiting its triggering condition.
  (Primary domain settled 2026-07-19, FD-31: satyakosh.org.)
  **Next external milestone:** buyer conversations with AI labs;
  internal enthusiasm is not market validation.

### What Satyakosh is not
Not a wiki (no edit-in-place), not a search engine (no ranking), not an
encyclopedia (no prose authority), not a dictionary, not a news or results
feed, not a legal registry, not a fiction knowledge base, and not an oracle —
it never asserts truth it cannot show the working for.
