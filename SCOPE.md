# Satyakosh — Scope Rules (SCOPE.md, version 1.0.0)

> *Restored 2026-07-17 from the recovered 2026-07-10 original (pre-loss bytes; see RECOVERY_NOTES.md and docs/rebuild_divergence_report.md); amendment A6 re-applied.*


Satyakosh refuses whole categories of content on purpose. A trust anchor
that tries to hold everything anchors nothing.

This document is the authority for those refusals. When a proposal is
refused at intake for scope reasons, the refusal must cite a rule ID from
this page (S1–S7). Refusals are always principled and citable — never
ad-hoc.

This document is frozen at genesis: its SHA-256 hash is enumerated in the
genesis record. Changes after genesis happen only through `governance`
records.

---

## S1 — Rules and procedures

**Refused:** how-to knowledge and rule systems. Examples: how chess pieces
move, the leap-year algorithm, how to renew a passport.

**Why:** rules are systems, not claims. They have editions, exceptions,
and governing bodies. Sealing a rule freezes one snapshot of a living
system and misrepresents it as a fact.

**Where it belongs:** the rule's own governing body and its documents.

## S2 — Derivable relations

**Refused:** anything computable from facts already on the ledger.
Example: "Paris is north of Rome" (computable from two coordinates).

**Why:** design invariant 7 — don't seal the derivable. Sealing derived
relations multiplies records without adding information, and every sealed
copy is a new surface for inconsistency.

**Where it belongs:** a consumer query over sealed data.

## S3 — Identity and equivalence

**Refused:** claims that two identifiers name the same thing. Example:
"H₂O is water."

**Why:** identity claims are symptoms of registry duplicates, not facts
about the world. Sealing them would freeze bookkeeping as knowledge.

**Where it belongs:** the entity registry's `same_as` link — unsealed and
correctable.

## S4 — Fiction and in-universe claims

**Refused:** claims true only inside a made-up world. Example: "Sherlock
Holmes lives at 221B Baker Street."

**Why:** the ledger witnesses claims about the world. In-universe claims
are true by authorial decree, not by verification; admitting them would
require a parallel truth standard the mission rejects.

**Where it belongs:** fan wikis and literary databases, which do this
well.

## S5 — Event and results feeds

**Refused:** news, scores, and event streams. Examples: match results,
election tallies as they arrive, disaster reports.

**Why:** feeds are about speed; the ledger is about permanence and
process. A 30-day review window cannot and should not race a news wire.
Some settled outcomes may qualify later as documented historical events
under Ring 2 rules.

**Where it belongs:** news organizations and official results services;
time-bound status belongs to the attestation layer.

## S6 — Lexical and translation facts

**Refused:** word meanings and translations. Example: "'chien' means
'dog' in French."

**Why:** language is a rendering layer in this design (invariant 2), not
sealed content. Dictionaries are living documents; lexical claims would
put prose semantics inside the seal, which the architecture forbids. The
`text` object type exists in the schema but is gated off by this rule.

**Where it belongs:** dictionaries; the ledger's own `labels/` layer holds
renderings without sealing them.

**Clarification (amendment A6):** characters are in scope as entities
via their Unicode code points — an external-standard adoption,
Ring 2. Words, meanings, and translations are not. The boundary:
character identity is a code-point assignment by a standards body;
word meaning is living language.

## S7 — Self-reference

**Refused:** claims about Satyakosh's own legal or commercial status.
Examples: "SATYAKOSH is a registered trademark", "Satyakosh Ltd. was
incorporated on…".

**Why:** a ledger must never be judge in its own case. Sealing claims
about ourselves would use the trust instrument to promote the trust
instrument.

**Where it belongs:** public legal registries and the project website.

---

## What scope refusal is not

A scope refusal says nothing about whether a claim is true. It says only:
this ledger is not the right home for it. Most refused categories have
excellent existing homes — that is exactly why Satyakosh does not need to
be one.
