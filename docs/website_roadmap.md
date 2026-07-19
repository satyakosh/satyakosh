# Website Roadmap

> Status: SETTLED 2026-07-19 (FD-31). The five open questions in the
> draft were founder-answered; the settled decisions section at the end
> records them. This document plans the public website only. It does
> not change SCHEMA, SCOPE, PIPELINE_POLICY, or any hash-critical
> document, and nothing in it gates the genesis freeze.

## Why this document exists

Settled in discussion 2026-07-19: volume (thousands to millions of facts)
comes from batch ingest pipelines with recipe-by-hash review
(`tools/ingest_codata.py` and successors, PIPELINE_POLICY P11), never from
humans typing into forms. The website's job is therefore not intake at
scale. Its job is:

1. Let anyone **search** the ledger and read any fact with its grounding.
2. Let anyone **verify** — or, better, learn to verify locally.
3. Let anyone **request** a fact or **report** an error, through a triage
   funnel that filters structurally before any human review.

## Principles (apply to every phase)

- **The website is never authoritative.** The chain plus a locally run
  verifier is authoritative. Every page that shows a fact links to the
  canonical bytes and to instructions for independent verification. A
  compromised website must never be able to lie undetectably; that is the
  whole design.
- **The website is read-only with respect to the chain.** No form on it
  writes to the ledger. Public input creates *proposals* that enter the
  normal pipeline (P1-P11). No seed bypass, no admin bypass — same rule
  as everywhere else.
- **No truth oracle.** Intake forms may check structure: duplicates
  against the chain, schema and unit validity (the real validator, not a
  reimplementation), and source-admissibility *class*. They must never
  "verify" a submission against web search or general online references
  — that would institutionalize exactly the circular consensus Satyakosh
  refuses (CLAUDE.md invariant 9).
- **Static-first.** Prefer a site generated from the ledger bytes over a
  live backend. Less to attack, less to maintain, nothing that can drift
  from the chain.
- **No contributor identity in hashed content.** If accounts ever exist
  (Ring-2 phase), they map to opaque, erasable `SK-USR-` IDs per SCHEMA;
  the website never puts a name into canonical bytes.
- Plain, short, operational English. Labels layer supplies all other
  languages; every language is a rendering, equal before the chain.

## Phase 0 — Now (pre-genesis, current phase)

Expected on the website now: **almost nothing.** Nothing web-related may
delay gates G1/G4/G6 or the freeze.

- [x] A single static page (GitHub Pages, repo `satyakosh/website`,
      domain satyakosh.org): what Satyakosh is (from MISSION.md), link
      to the repository, and "how to verify" pointing at `verify.py`.
      No backend, no accounts, no forms. Labeled pre-genesis honestly.
- [x] Domain: satyakosh.org (already purchased).
- [ ] Request-a-fact channel, zero-build version: a GitHub issue form
      ("Propose a fact" / "Report an error") with structured fields, plus
      a CI job that runs the real validator and duplicate check against
      the chain and comments its findings on the issue. GitHub accounts
      stand in for user creation; the triage trail is public and
      permanent.

## Phase 1 — Before the v1.0.0 launch (after genesis seals clean)

The read-only explorer. This is the public face of the ledger.

- [ ] **Fact search**: by label (any language in the labels layer), by
      entity ID, predicate, source, fact ID. Static index preferred.
- [ ] **Fact detail page**: rendered triple with labels, the canonical
      bytes, chain position, seal date, source and derivation (recipe
      hash, `derived_from` lineage), conditions, status
      (sealed / superseded / retired) with links along supersession
      chains. One click to the grounding receipt (verifier SDK output).
- [ ] **Chain head**: current head hash displayed prominently on every
      page, with the record count and last-seal date.
- [ ] **Verify page**: download the chain, run `verify.py`, expected
      output — written so a non-programmer can follow it.
- [ ] **Genesis page**: the genesis record rendered in full (it carries
      the only prose on the chain), with its hash.
- [ ] **Request-a-fact on the site**: a form that front-ends the Phase 0
      triage flow (same structured fields, same validator-backed checks:
      duplicate, schema/units, source-class). Submissions become public
      proposals in the pipeline; the form tells the submitter exactly
      what happens next and does not promise sealing.
- [ ] **Error reporting**: a first-class "report an error in this fact"
      link on every fact page, feeding the same triage channel.
      Corrections happen only through supersession — the page explains
      this.
- [ ] **Stats page** (small): facts by source, by domain, seal rate,
      proposal queue depth. Numbers only, no marketing.
- [ ] No user accounts in this phase. Proposals ride on the GitHub-backed
      channel underneath.

## Phase 2 — Before Ring-2 activation

Ring-2 means more sources, more domains, more proposers, and live
governance. The website grows the surfaces that make that scrutiny
public.

- [ ] **Governance explorer**: every governance record rendered
      (whitelist_change, ruleset_change, ucum_expansion, ascii_exemption,
      doc_supersession), plus `rules_in_force` shown as of any point in
      the chain — reconstructible from the chain alone, and the page says
      so.
- [ ] **Source registry pages**: each admitted source with its S1-S7
      admission audit trail from RING2.md; each candidate source with its
      open review.
- [ ] **Proposal tracking**: public status for every submitted proposal
      (received / triaged / in review / sealed / declined, with the
      citable reason). No silent drops.
- [ ] **Proposer accounts**, only if proposal volume demands more than
      the GitHub channel: accounts map to opaque `SK-USR-` IDs via the
      opt-in registry (erasable, per SCHEMA). Prerequisites: the legal
      wrapper exists (holding user data requires an institution), spam
      and abuse defenses, and a founder decision on moderation.
- [ ] **Review-queue visibility**: the public can see queue depth and
      age, so review capacity is an honest, visible number.
- [ ] **Reviewer tooling** (may be a separate private surface): batch
      review support aligned with the A18 review-file format
      (recipe-by-hash, per-fact + batch_ref).
- [ ] Security posture re-check before accounts: threat model, rate
      limits, SECURITY.md coverage extended to the website.

## Explicitly out of scope, permanently

- Public direct-write to the ledger, from any surface, ever.
- Truth-checking submissions against web search or "online references."
- Reputation-weighted governance and sealed ML feedback (already
  rejected in strategy triage, 2026-07-19).
- The website as the volume engine. Millions of facts arrive through
  ingest pipelines and batch review, or not at all.

## Settled decisions (founder, 2026-07-19 — FD-31)

1. **Domain:** satyakosh.org (already purchased).
2. **Repository:** the website lives in its own repo,
   `satyakosh/website`. This repository stays stdlib-only ledger +
   tools.
3. **Static page timing:** publish now, before the Genesis Window,
   labeled pre-genesis honestly.
4. **Request-a-fact form:** launches only after the first batch
   pipeline has run — not with the Phase 1 explorer — so an unserved
   queue is not the public's first impression.
5. **Hosting:** GitHub Pages. Free, HTTPS, deploys from committed
   bytes only (the site can never drift from its repo), nothing
   server-side to attack. Revisit a CDN in front only if
   chain-download bandwidth ever demands it.
