# DECISIONS.md — founder decision register

Every locked decision since the 2026-07-15 rebuild, with its audit
trail (the commit that applied it). Pre-loss decisions (the D1–D8 /
P1–P11 series of the v2.0–v2.1 era) are recorded where they landed —
in the founding documents themselves; this register does not
reconstruct them from memory. New decisions are appended here in the
same commit that applies them.

IDs are `FD-n` (founder decision), append-only, never renumbered.

---

## Repository identity & integrity (2026-07-16)

**FD-1 — Commit identity.** Commits are authored as
`Shubhankar Patil <25669040+punyanagari@users.noreply.github.com>` —
real name, GitHub-noreply email (personal email never in history).
*Applied: 8395f6d.*

**FD-2 — Every commit is SSH-signed.** All commits on the ledger repo
carry a Verified signature (ed25519 signing key registered on the
GitHub account). *Applied: 8395f6d and all successors.*

**FD-3 — Git never rewrites bytes.** `.gitattributes` sets `* -text`:
no line-ending conversion on any platform, ever — founding-document
hashes are computed over exact file bytes. *Applied: 8395f6d.*

**FD-4 — `main` is protected.** Force pushes and branch deletion are
blocked; git history is one of the four evidence chains and must not
be rewritable, including by the founder. *Applied: repo settings,
2026-07-17; verified via API.*

**FD-5 — Private workflow stays private.** Machine-local and
session-recovery material lives in `*.local.*` files (gitignored),
never in public history. *Applied: 8395f6d.*

## Validator & engineering doctrine (2026-07-16 → 17)

**FD-6 — The reference implementation stays stdlib-only.** Zero
runtime dependencies is a supply-chain property of a trust anchor.
Test-only dependencies (hypothesis, rfc8785) are permitted — they
never touch ledger.py. *Applied: df947c6.*

**FD-7 — Hardening round 1.** Record 0 must be genesis; duplicate
canonical triples refuse to seal; fact seals refuse while any ruleset
in force carries operative placeholders; malformed proposals get
citable rejections, never crashes. *Applied: 2b31d74 (A14 extended).*

**FD-8 — Seed values follow s7.3 to the letter.** The Cs-133 seed
value carries its published trailing zero (`9.192631770e9`):
significant figures are sacred even for exact definitions.
*Applied: 2b31d74.*

**FD-9 — Hardening round 2 (external adversarial review, 17/17
findings reproduced then closed).** Supersession is a transaction:
target must exist, be the latest version, be unsuperseded; metadata
supersession keeps the fact_id and increments version by exactly 1.
**Superseded-ness is derived from the chain, never written into
sealed bytes** — the reviewer's suggested status mutation was rejected
as an immutability violation. Strict field enumerations (unknown
fields refused); condition values validated with the same typed-union
rules as objects; enums, formats, ring typing, non-empty complete
sources all enforced; `jcs()` refuses JSON floats (proven
cross-implementation hash fork) and lone surrogates; UCUM is a v1
closed whitelist (`UCUM_V1` in ledger.py, expanded with proposals);
near-duplicate detection warns and never refuses; `verify(full=True)`
replays every record through seal-time validation. *Applied: 5608cdf.*

**FD-10 — Continuous adversarial pressure.** A deterministic mutation
fuzzer runs in CI on every push (two seeds): any mutation of any
record must produce either a clean seal or a citable ValidationError —
never a crash, never a silent acceptance. *Applied: 5e6e557.*

## Genesis content (2026-07-17)

**FD-11 — Entity IDs final.** The founding entity registry is
confirmed; the four mandatory-conditions placeholders resolve to
method = SK-ENT-000008, boiling temperature of water = SK-ENT-000005,
pressure = SK-ENT-000006, temperature scale = SK-ENT-000007. IDs are
append-only and never re-pointed. *Applied: 94f3f88.*

**FD-12 — Founding-document hash doctrine.** Prose documents (`.md`)
hash as raw frozen file bytes; machine-readable JSON hashes as its
RFC 8785 (JCS) serialization — one rule, zero exceptions
(mandatory_conditions and the predicate snapshot are both JCS).
*Applied: 94f3f88 (SCHEMA s9, genesis draft, tools/genesis_hashes.py).*

**FD-13 — Invocation orthography.** The Pavamana mantra seals in the
unaccented, word-separated Devanagari form as drafted — danda । after
lines 1–2, double danda ॥ terminal, spaced मृत्योर्मा अमृतं (no
avagraha) — a deliberate legibility choice consistent with the
simplified-romanization citation. NFC-stable, 61 code points, exact
sequence recorded in GENESIS_AMENDMENTS.md. *Applied: 94f3f88.*

**FD-14 — Dedication bytes.** Wording final; em dash (U+2014) kept by
explicit decision. Consent note is recorded in the review file at the
freeze. *Applied: 94f3f88.*

**FD-15 — Mission prose (working draft).** The plain-institutional
register ("…It asserts no authority. It shows its working. What it
seals, it keeps.") is in the genesis draft; it locks only after the
founder's 48-hour final read at the freeze. *Applied: 6afcc02.*

## Pipeline & window (2026-07-17)

**FD-16 — Review-file format 1.0.0 (A18).** Canonical bytes are
JCS + SHA-256; recipes are referenced by content hash and mirrored
alongside review files; `process_hash` is computed only at seal (held
proposals stay live and unsealed); one review file per fact with
`batch_ref` (P11); Git history is the authoritative timeline; machine
annotations carry `tool_version`. See docs/review_file_format.md.
*Applied: 6afcc02.*

**FD-17 — Tier 3 (ITS-90) holds in review.** The boiling-point
proposal is submitted and held (P6; renumbered P7 when the
original PIPELINE_POLICY was restored — FD-24) as a living exhibit — never
sealed with a placeholder condition. It seals only after a governance
record activates the entity condition type. *Applied: 6afcc02.*

**FD-18 — Tier 4 is the missing-condition exhibit.** The deliberate
refusal demonstration is a proposal missing its mandatory pressure
condition: deterministic, honest, citable. No planted value errors —
recognition rewards real catches only. *Applied: 6afcc02.*

**FD-19 — RING2 parameters locked.** P1 ≥50 sealed Ring-1 facts ·
P2 ≥60-day rules review · P3 ≥3 independent reviewers · P4 ≥1 design
partner in writing · P5 ≥30-day dispute floor · P6 demand-driven
first domain · P7 ≥2 independent institutions. All remain publicly
contestable per RING2 §9 until Ring 2 opens. *Applied: 6afcc02.*

**FD-20 — The Genesis Window is readiness-gated.** No date is
announced until the six readiness gates in GENESIS_AMENDMENTS.md are
checked off. Freeze on readiness, never on a schedule.
*Applied: 6afcc02.*

**FD-21 — PyPI 1.0.0rc1 ships only after genesis seals clean**,
together with the verifier. *Applied: 6afcc02.*

## Public posture (2026-07-17)

**FD-22 — Security findings are public by default.** SECURITY.md:
public adversarial review is the design; private disclosure only for
findings dangerous to publish before a fix. No monetary bounty —
recognition is permanent sealed inscription (P10 / RING2 §9).
*Applied: c61227b.*

**FD-23 — A legal wrapper precedes the first serious partner.** A
foundation or trust with succession rules must exist before any
sponsor, partner, or funding conversation — institutional independence
requires an institution. Tracked in GENESIS_AMENDMENTS.md.
*Applied: c61227b (tracked; entity not yet formed).*

## Reconciliation with the recovered originals (2026-07-17)

**FD-24 — Restore the recovered originals; re-apply post-loss
amendments on top.** The recovered 2026-07-10 package proved that the
rebuilt SCHEMA s4, SCOPE, TAXONOMY, MISSION, and PIPELINE_POLICY came
from earlier-draft fragments. The originals are restored as the base:
the s4 field set returns to its taxonomy-review form (`truth_type`
removed; `terminality` `none|expected|scheduled`; `status` includes
`retired`; `derivation` = `{type, script, derived_from}` with the
recipe hash sealed in the record), SCOPE's true S1–S7 (incl.
identity/equivalence and self-reference) returns with rule-ID
authority, TAXONOMY returns as the four-dimension intake model, MISSION
returns with "Open data is the moat" as principle 1, and
PIPELINE_POLICY returns with its P1–P10 numbering and explicit seal
preconditions. Re-applied on top: A1–A4, A6, A8 (as P11), A9, FD-12,
FD-16/A18, the UCUM whitelist wording, and the A16 seed restructure.
Validator, fixtures, and cross-references aligned; pipeline-rule
citations now use the restored numbering. *Applied: this commit.*

## Validator hardening round 3 (2026-07-17, second external review)

**FD-25 — fact_id form is deterministic; no re-entry of a retired
triple.** The 16-char fact_id form is permitted *only* on a real
12-char prefix collision with a different sealed triple; the 12-char
form is mandatory otherwise and must escalate on collision. This closes
the gap where a fully-superseded triple (retired by a triple-changing
supersession) could re-seal at version 1 under the 16-char form with no
supersedes link — re-entry semantics, if ever wanted, arrive by
governance; accidental semantics could not be removed. *Applied: this
commit.*

**FD-26 — verify() never raises.** Auditing a hostile or corrupt store
is verify()'s entire purpose, so bytes that trip the canonicalizer (a
stored float, a lone surrogate, a retyped field) are reported as
`CORRUPT`/`INVALID` findings, never propagated as exceptions. The load
path surfaces the same as a clean "ledger file corrupt at record i"
error. A verifier-side fuzzer (mutate a stored record, assert
findings-not-raises) runs in CI. *Applied: this commit.*

Also this round (mechanical, no decision): `derived_from` to a
dead-lineage fact seals but raises a liveness warning flag (like the
near-duplicate flag); SCHEMA documents that `retired` status is a
governance-era derived state (no seal-time verb), that a born-expired
validity window is intentional, and that `derivation.script` artifact
existence/lint is an intake-pipeline + CI requirement, not a byte rule.

**FD-27 — The founding date seals in dual-calendar form.** The
`founded` inscription reads Vikram Samvat first, then Gregorian, both
calendars named: "आषाढ़ कृष्ण सप्तमी, विक्रम संवत् 2083 (Vikram
Samvat) — 7 July 2026, 2026-07-07 (Gregorian)". Verified against
published panchang sources (sunrise-tithi convention); NFC-stable.
The validator requires exactly one embedded Gregorian ISO date as the
machine anchor (corroboration keys on it). The mission prose gained
its remembrance sentence in the same session; the 48-hour final-read
clock restarted. *Applied: this commit.*

**FD-28 — Version strings and the month convention.** (a) The founded
inscription uses the **pūrṇimānta** month reckoning (Āshādha), the
convention customarily paired with the Vikram Samvat era; the amānta
name for the same fortnight (Jyeshtha) is recorded in the transcription
checklist so no future reader mistakes the fork for an error. Saptami
at sunrise verified for both Delhi and Pune. (b) The founding documents
freeze as **1.0.0** — their headers already carry 1.0.0 with
release-candidate status prose; "rc.1" is the pre-freeze drafting
label, and the genesis record seals `schema_version`/
`pipeline_policy_version` as "1.0.0". The rc→1.0.0 promotion is noted
in CHANGELOG at the freeze. *Applied: this commit.*

**FD-29 — Governance-engine timing, and closed-by-default UCUM
(from a synthesis security review, 2026-07-19).** (a) The governance
engine (payload validation + chain-position ruleset resolution) is
required before the FIRST governance record seals — Ring-2 activation,
after the window — NOT before the Genesis Window opens: the window
seals only the genesis record (its own type) and Ring-1 seed facts
(plain facts), and a hash-breaking flaw restarts the window rather than
needing a governance record. It stays the tracked pre-Ring-2
prerequisite; the window is not blocked. (b) The founding UCUM
whitelist admits exactly the founding-scope codes — `%` and `a`, added
2026-07-18 for Ring-2 expressibility (issue #5 F1), are removed: no
Ring-1 seed uses them, they are inert while Ring 2 is sealed out, and
UCUM_V1 is not a genesis-hashed artifact, so they return at Ring-2
activation by governance record. Reverses the issue-#5 F1 seal
behaviour; the F1 test now pins refusal. Ring-2 stress harnesses extend
the set locally. *Applied: this commit.*

**FD-30 — Build the governance engine before the window, as a
review target (revises FD-29a).** FD-29(a) deferred the governance
engine to pre-Ring-2 on the correct observation that the window seals
nothing that needs it. The founder's counter is stronger: the Genesis
Window is the project's highest-scrutiny moment, and the governance
*payload format* — which benefits from adversarial review far more than
implementation does — should be exposed to it. So the engine is built
now (SCHEMA s10 / P9: validate_governance + rules_in_force /
_apply_governance), **dormant and non-gating**: nothing at the window
uses it, its correctness does not block the freeze, and a flaw found in
it during the window is a fix, not a window restart. Five governance
kinds, strict deltas validated against the rules in force,
chain-position resolution reconstructible from the chain alone. Full
simulated Ring-2 activation and the review's M4 ASCII-narrowing dry-run
in stress/test_governance.py (25 cases). *Applied: this commit.*

**FD-31 — Public website: role, repo, hosting, and timing
(2026-07-19).** The website plan is docs/website_roadmap.md (promoted
from draft this commit). Its role, settled after debate: search +
verify + request-a-fact triage — never intake at scale. Volume comes
from batch ingest pipelines with recipe-by-hash review (P11), not from
humans typing into forms, on any surface. Standing principles: the
website is never authoritative (the chain plus a locally run verifier
is), never a write path to the chain, and never a truth oracle — intake
forms check structure (duplicates, schema/units via the real validator,
source-admissibility class), never "truth" against web references
(invariant 9). Founder-settled specifics: (1) domain satyakosh.org
(already purchased); (2) the site lives in its own repository,
`satyakosh/website` — this repository stays stdlib-only ledger + tools;
(3) the Phase 0 static page publishes now, before the Genesis Window,
labeled pre-genesis honestly; (4) the request-a-fact form launches only
after the first batch pipeline has run, so an unserved queue is not the
public's first impression; (5) hosting is GitHub Pages — static-first,
deploys from committed bytes only. *Applied: this commit; site
published separately in satyakosh/website.*

**FD-32 — verify(full) replay is position-correct; genesis state is
not inlined (2026-07-19).** Issue #7 G1: verify(full) built its replay
shadow from `self.rulesets` — the END state, since the load path folds
every governance record — so a tightening ruleset_change retroactively
condemned facts sealed under earlier rules, contradicting s10/P9 ("the
ruleset governing any fact is genesis state plus all preceding
governance records") and verify's own seal-time-replay contract. The
fix snapshots the genesis ruleset baseline at construction
(`_genesis_rulesets`, deep-copied so caller-side mutation cannot drift
it) and replays from it; whitelist and UCUM already had
genesis-equivalent baselines. **Considered and deferred: inlining the
founding rulesets INTO the genesis record** (full chain
self-containment) — hash-binding the provided rulesets to the
genesis-declared digests (issue #7 G3) gives the same assurance
without bloating genesis, and the whitelist branch of the same disease
(G4) is covered by inline-whitelist authority. Recorded so chain
self-containment is not re-litigated without new evidence. Pinned in
stress/test_governance.py by the G-series battery, including an
era-violating hash-valid forgery flagged only by verify(full) (default
verify stays CLEAN on the well-formed lie, by design) and an invalid
mid-chain governance record flagged without its fold poisoning replay
state. *Applied: commits 1daf5bf / 195480b / aa4881d plus the two
ported regression cases (this commit); drafted in a parallel unpushed
G1-only patch, reconciled on issue #7.*

**FD-33 — Durability & anchoring policy (2026-07-19).** The
GitHub-dependency triage concluded: the trust root is host-independent
(bare clone + verify.py; review records are committed content per
A18), but availability had a single always-on copy, and wholesale
chain substitution — records are hash-chained, not signed — is refuted
only by independent copies and anchored heads. Policy settled at
docs/durability.md: (1) forge mirror = GitLab
(gitlab.com/satyakosh/satyakosh, founder-held, full signed history);
(2) both Software Heritage archival and the mirror live BEFORE the
Genesis Window (done same day — snapshot c65a549a…); (3)
OpenTimestamps ADOPTED — committed .ots proofs per anchor, first stamp
is the genesis hash at freeze; operator-only tooling, zero runtime
dependency, the one anchor requiring no institution's honesty; (4)
anchor cadence = per sealed batch plus a QUARTERLY heartbeat floor,
sized to be keepable solo forever (every beat is a founder-signed
commit, FD-1 — no bot holds the key; a missed beat is publicly
visible, so the promise must not outrun the operator), with an
explicit tightening path (monthly → weekly by ordinary doc change
once the ledger carries live reliance; tightening is always
permitted, loosening below the published floor is the credibility
cost). The policy document is deliberately NOT genesis-hashed —
mirrors and cadences evolve with infrastructure. Weekly floor was
considered and set aside for now: 52 personally-signed ops/year is a
promise a solo founder will visibly break, and the log displays every
miss. *Applied: this commit; mirrors live in 6546fef.*

## Explicitly rejected (recorded so they are not re-litigated)

- **Mutating a sealed record's status on supersession** — violates
  invariant 1; superseded-ness is derived (FD-9).
- **Reputation-weighted influence in governance** — proto-authority
  and a capture surface; recognition stays display-only.
- **Sealing ML/review feedback as governance records** — outside the
  s10 trigger list; intake tooling stays unsealed.
- **Schema changes for "richer" derivation graphs** — `derived_from`
  already seals the dependency graph; the proposed example was itself
  a SCOPE violation.
- **Refusing duplicate condition properties** (issue #5's F2 fix as
  proposed) — SCHEMA s3.4 documents same-property pairs as a feature
  (min/max ranges; the tie-break exists for them). Duplicates raise
  a review flag instead; per-property cardinality rules belong to
  the Ring-2 activation ruleset schema.
- **Planted errors as review-zone demos** — staged, with a bad failure
  mode (FD-18 chose the honest exhibit).
- **Early Merkle proofs** — deferred until scale demands (SCHEMA s8);
  at founding scale the linear replay is the proof.
- **Heavy framework adoption (validation libraries, package
  restructure) in the reference implementation** — see FD-6.
