# Satyakosh — Mission

**Status: reconstructed after loss of the local copy. Principles 3-6 and
the problem/design text are recovered near-verbatim from session
transcripts; principles 1-2 are restated from the locked decision record.
Founder to re-review. See RECOVERY_NOTES.md.**

Satyakosh (सत्यकोश, "treasury of truth") is a permanent, tamper-evident
public ledger of verified facts — a neutral trust anchor for an age in
which machines mediate what humanity knows.

## Principles

1. **Immutability over editability.** A sealed record is never edited.
   Corrections are new records. History is never rewritten.
2. **Trust through process, not authority.** Satyakosh never asserts truth
   it cannot show the working for. Every fact carries its sources, its
   derivation, and the sealed history of its own review.
   The automated checker annotates; it never vetoes. Humans resolve
   disputes in public.
3. **Institutional independence.** No government mandates, no
   single-patron capture. The state may one day be an ordinary paying
   customer; it will never be a sponsor whose interests the ledger must
   serve.
4. **The ledger seals claims and evidence-of-governance — never policy
   itself.** Rules may evolve; every evolution is witnessed on the chain.
5. **Language independence.** Only structure is sealed. Every human
   language is a rendering layer, equal before the chain.
6. **Scope discipline.** Satyakosh refuses whole categories of
   representable content (rules, fiction, lexicons, news feeds, legal
   registries) because a trust anchor that tries to hold everything
   anchors nothing.

## The problem

AI systems increasingly mediate humanity's access to information while
training on, and citing, an internet whose reliability is degrading —
partly because of AI-generated content itself. There is no neutral,
permanent, machine-verifiable ground-truth layer that an AI (or a person)
can check a claim against and cryptographically confirm has not been
altered. Satyakosh is that layer. Primary first customers: AI labs, which
need verifiable ground-truth anchors for training, evaluation, and
inference-time grounding.

## The design (1.0.0)

- **Facts are semantic triples** — subject / predicate / typed object /
  typed conditions — plus a sealed jacket (ring, sources, derivation,
  validity window, process hash). Objects and condition values share one
  discriminated type union (quantity | entity | date, text reserved), so
  the schema extends to future fact categories without breaking changes.
- **Everything sealed is language-neutral bytes.** Prose, names, URLs, and
  translations live in unsealed registry/label files, freely correctable.
- **Facts are content-addressed.** A fact's ID contains a hash of its own
  canonical triple, making the name self-verifying and duplicate detection
  an exact lookup.
- **Four interlocking chains of evidence:** the fact-chain, the
  process-chain, the governance-chain, and Git's own commit history as an
  independent layer.
- **Rings gate ambition; derivation gates admissibility.** Ring 1
  (independently re-derivable) is the v1 scope, sourced exclusively from a
  sealed whitelist (CODATA / NIST / BIPM). Ring 2 opens only when its
  written disagreement rules and governance machinery exist (see
  RING2.md).
- **The pipeline is open:** anyone proposes → automated checks annotate,
  never veto → public review with a 30-day-minimum dispute window → seal
  only after objections resolve.
- **Genesis Window launch:** the first facts pass through the real
  pipeline in public, with a bug-bounty-style scoreboard rewarding
  validated catches. The founding invariant holds from record zero.
