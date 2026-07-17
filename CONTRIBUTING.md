# Contributing to Satyakosh

> *Restored 2026-07-17 from the recovered 2026-07-10 original (pre-loss bytes; see RECOVERY_NOTES.md and docs/rebuild_divergence_report.md).*


Thank you for wanting to add to the treasury. This page explains, in
plain English, how a fact gets in. The binding rules live in
[`PIPELINE_POLICY.md`](PIPELINE_POLICY.md); if this page and that one ever
disagree, that one wins.

## The short version

1. You propose a fact (a pull request).
2. A robot checks your sources. It can complain, but it cannot say no.
3. The public gets at least 30 days to object.
4. When every objection is settled, the fact seals onto the chain —
   forever.

Nobody skips this. Not even the founder. Not even fact #1.

## Before you propose: four questions

Answer these first — they decide whether your fact can enter at all.

**1. How is your fact established?**
Is it defined (the speed of light), measured (the gravitational
constant), proven (a theorem), or derived from other sealed facts? These
can seal today. Statistical and historical claims must wait for Ring 2.
Causal claims ("X causes Y") and legal-status claims are blocked until
dedicated rules exist. See [`TAXONOMY.md`](TAXONOMY.md).

**2. What is it about?**
Your fact's subject must exist in the entity registry
(`registries/entities.json`), or your proposal must add it.

**3. Does it expire?**
"Current" facts (who holds an office, today's tax rate) never seal — they
belong to the attestation layer, not the chain. Facts with known validity
windows state them.

**4. What does it depend on?**
Water boils at 100 °C *at standard pressure, on a stated temperature
scale*. If your fact needs a condition to be true, the condition must be
in the proposal. A fact missing a mandatory condition cannot enter review.

**Also check [`SCOPE.md`](SCOPE.md)** — some things we refuse on
principle: rules and how-tos, fiction, word meanings, news feeds, and a
few more. Every refusal cites a written rule.

## What a proposal looks like

A proposal is one JSON file in `proposals/`, following
[`SCHEMA.md`](SCHEMA.md) exactly:

- the fact as a **semantic triple** — subject, predicate, typed object,
  typed conditions
- **sources** from the whitelist (`registries/sources.json`) with edition
  and retrieval date
- the **derivation** — how it is established, plus a runnable
  verification script where possible
- the value written in the **normalized number grammar** (SCHEMA.md §7.3),
  copying the source's digits exactly — never rounded, never "cleaned up"

The pull request template walks you through every field.

## What happens next

- The **automated checker** posts its findings publicly. If it objects
  and you disagree, you may still push the proposal into review — your
  disagreement with the machine stays visible forever. We call this
  *publish under protest*. It is transparency, not a bypass.
- The **review window** runs at least 30 days. Anyone on earth may
  object. You answer objections in public.
- **Sealing** happens only when the window is done and every objection is
  resolved. If an objection never resolves, your proposal stays in the
  review zone — visible, unsealed — indefinitely.

## Your identity

Inside anything permanent you are an opaque ID like `SK-USR-000042`.
Linking that ID to your name is opt-in and reversible — you can be erased
from the name registry at any time. The permanent record never contains
your name.

## Found a mistake instead?

Even better. Errors in proposals, in the code, in the schema, or in these
rules are exactly what the review process exists to catch. Open an issue
or object on the proposal. During the Genesis Window, validated catches
are scored and permanently inscribed on the chain.

## Code contributions

`ledger.py` and the tooling are Apache-2.0. Ordinary pull requests are
welcome. Changes that affect canonical bytes (hashing, serialization,
validation) are schema changes and follow the versioning rule in
SCHEMA.md — they cannot be merged as ordinary code fixes.
