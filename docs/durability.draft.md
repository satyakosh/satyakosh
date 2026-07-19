# Durability & external anchoring 1.0.0 (DRAFT)

**Status: drafted 2026-07-19, pending founder review.** This defines
the availability and anchoring layer — how the ledger survives the
loss of any single host, and how "which chain is the real one?" stays
answerable without trusting any platform. It is deliberately NOT one
of the genesis-hashed documents: mirrors and cadences are operational
choices that evolve with the infrastructure, recorded here and in Git
history, not sealed. Open founder decisions are listed at the end.

## What this layer is — and is not

The trust root does not live here. A bare clone of this repository
plus `verify.py` verifies every sealed byte with zero reference to any
host: content-addressed fact IDs, the hash chain, the genesis-declared
digests (`verify.py CHAIN.json --repo .`). GitHub is a venue and a
copy — per the review-file doctrine (docs/review_file_format.md),
platform URLs are convenience, never evidence, and the complete review
record of every fact is committed content that clones with the repo.

What this layer adds is the answer to two failure modes the chain
cannot answer alone:

1. **Availability.** Today the repository has one always-on public
   copy. A host outage, account action, or jurisdictional block would
   not damage a single sealed byte — but it would take the public
   record offline until a private copy resurfaces. A project whose
   promise is "check, forever" should not have a single point of
   availability failure.
2. **Wholesale substitution.** Sealed records are hash-chained, not
   signed — the chain's integrity is internal, and no key makes any
   holder a trust root. A forger who regenerates an entire alternative chain
   from genesis produces internally valid hashes. What refutes such a
   chain is not any internal check but comparison against
   independently held copies and anchored chain heads: the forger must
   beat every mirror, every anchor, and the signed Git timeline
   simultaneously, and the difficulty of that is the guarantee.

## Mirrors

Target state (each item is independent of the others):

| Mirror | What it holds | Trigger |
|---|---|---|
| Software Heritage | Full repository history, permanently archived | "Save code now" request at each release; SWH also crawls autonomously |
| Independent forge (Codeberg or GitLab) | Live push mirror of `main` | Push-mirror on every push, or manual push after each session |
| Zenodo (versioned DOI) | Release snapshots, citable | Each tagged release from rc1 onward (aligns with the existing "PyPI at rc1" sequencing) |
| Founder offline copy | Full clone + the two recovery zips | Refreshed after every session (already practiced since the 2026-07-15 loss) |

Mirror accounts are founder-held. No mirror is load-bearing for
verification; every mirror is load-bearing for availability, and each
additional independent copy raises the cost of wholesale substitution.

## Chain-head anchoring

From genesis onward, after the genesis seal and after every sealed
batch:

1. Append a row to `anchors/ANCHORS.md` (in-repo, committed and
   signed like everything else):
   `| date | records | chain_head | sha256(ledger file) | git commit |`
2. Push, so the row propagates to every mirror in the same act.
3. Snapshot the repository page or release with the Internet Archive
   (save-page-now), so the anchor row exists in an archive that is not
   a Git host.
4. (Optional, founder decision 3 below) stamp the chain head with
   OpenTimestamps for a blockchain-anchored proof of existence at a
   cost of one small file — the only step that would introduce a
   non-Git external format.

The anchor log is corroboration, not authority: the chain remains
self-verifying, and a verifier who distrusts the log simply ignores
it. Its value is that the same short string ends up in many
independently operated places at known dates.

## Dispute doctrine — "two chains claim to be Satyakosh"

Resolution order, mechanical first:

1. **Internal integrity.** Run `verify.py CHAIN.json --repo DIR` on
   both candidates. A candidate with findings loses immediately.
2. **Anchor agreement.** Compare each candidate's historical chain
   heads against the anchor rows held by the mirrors and archives. The
   candidate consistent with the independently archived anchors wins.
   A forged chain must have beaten every archive at every date.
3. **Genesis identity.** The genesis record's content hash, and the
   founding date corroborated outside the system entirely (the
   trademark filing's priority date matches the genesis anchor date).
4. **Git continuity.** The signed commit timeline (FD-1/FD-4: every
   commit Verified, history not rewritable) on the surviving mirrors.

A verifier needs only steps 1–2 in practice; 3–4 exist so that even a
catastrophic loss of all live hosts leaves the question decidable from
archives and public filings.

## What stays platform tooling

Pull requests, Actions, Discussions, and issue threads are venue
(review happens there; the record is the committed review file). CI is
convenience (every check it runs is a committed script anyone can run
locally). Discovery (stars, search) is replaceable. Loss of any of it
is an inconvenience, never an integrity event.

## Open founder decisions

1. **Which forge for the push mirror** — Codeberg (nonprofit,
   Forgejo) or GitLab (larger, commercial)? One is enough; two is
   cheap.
2. **Timing** — recommendation: Software Heritage save + forge mirror
   live BEFORE the Genesis Window opens (both are minutes of work);
   Zenodo at rc1 as already sequenced. The window's reviewers will ask
   the single-point-of-failure question.
3. **OpenTimestamps** — adopt, or rely on mirror-plus-archive
   diversity alone? (Zero runtime dependency either way; the .ots
   proof is just a committed file.)
4. **Anchor cadence floor** — per sealed batch is the natural event;
   is a calendar floor (e.g. quarterly even with no new batches)
   wanted so archives see liveness?
