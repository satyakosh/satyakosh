# Review-file format — DRAFT PROPOSAL (A18)

**Status: DRAFT for founder review. Not frozen, not authoritative.**
This proposes the canonical review-file format that `process_hash`
commits to (SCHEMA s7.4: "SHA-256 of the raw review-file bytes"). It
must be settled before the Genesis Window opens, because the window's
first sealed facts each carry a `process_hash` that third parties have
to be able to recompute and audit. Until it is frozen, `process_hash`
seals an opaque blob and the "trust through process" claim (MISSION
principle 2) is unverifiable.

This is a decision, not a mechanical derivation — it defines what "a
review" *is* on the ledger. The founder should treat every SHOULD/MUST
and every open question below as a fork to settle explicitly.

## What the review file is

One review file per proposed fact, holding the complete public record
of how that fact passed the pipeline: the proposal, every automated
flag, every objection and its resolution, and the final decision. When
the fact seals, `process_hash = SHA-256(canonical review-file bytes)`
is sealed with it — so the review can never be rewritten after the
fact without detection, exactly as the fact itself cannot.

## Design constraints (inherited, not up for grabs)

- **Deterministic bytes.** Like every hashed artifact, the review file
  needs one canonical byte form. Proposal: reuse the existing machinery
  — JCS (RFC 8785) + SHA-256 — so there is one canonicalization law in
  the project, not two. The review file is JSON.
- **Append-only in spirit.** A review accretes events (flags,
  objections, resolutions). Entries are never edited or deleted; a
  correction is a new entry. The file is frozen at the instant of seal
  and its hash taken then.
- **Contributor pseudonymity (invariant 6 / P8).** Participants appear
  only as opaque `SK-USR-` IDs. The review file MUST NOT contain real
  names, emails, or GitHub handles — those live only in the deletable
  contributor registry. This keeps right-to-erasure intact: deleting a
  registry row never touches a sealed `process_hash`.
- **Not necessarily ASCII.** Unlike a `fact` record, a review is human
  discussion and may legitimately contain non-ASCII prose (an objection
  written in Hindi, a Devanagari label under discussion). So the review
  file is NFC UTF-8 like the genesis record, NOT ASCII-restricted. It
  is not a `fact` record and the s7.2 tripwire does not apply to it.

## Proposed structure

```json
{
  "review_format_version": "1.0.0",
  "fact_id": "SK-R1-PHYS-9f3a2c81d4e0",
  "triple_hash": "9f3a2c81d4e0...<full 64 hex>",
  "proposal": {
    "proposed_by": "SK-USR-000007",
    "proposed_at": "2026-08-01T12:00:00Z",
    "triple": { "...": "the exact triple submitted" },
    "derivation": { "type": "si_exact_definition", "recipe": "..." },
    "sources": [ { "source": "SK-SRC-000001", "edition": "CODATA 2022",
                   "retrieved": "2026-08-01" } ]
  },
  "annotations": [
    { "at": "2026-08-01T12:00:03Z", "by": "machine",
      "check": "grammar", "result": "pass" },
    { "at": "2026-08-01T12:00:03Z", "by": "machine",
      "check": "mandatory_conditions", "result": "pass" }
  ],
  "objections": [
    { "id": "OBJ-1", "at": "2026-08-03T09:00:00Z", "by": "SK-USR-000012",
      "body": "Trailing-zero precision does not match the source edition.",
      "resolution": { "at": "2026-08-05T10:00:00Z", "by": "SK-USR-000007",
                      "outcome": "corrected",
                      "body": "Value amended; see proposal.triple." } }
  ],
  "window": { "opened": "2026-08-01T12:00:00Z",
              "closes_no_earlier_than": "2026-08-31T12:00:00Z" },
  "decision": { "outcome": "sealed", "at": "2026-09-02T00:00:00Z",
                "unresolved_objections": 0 }
}
```

### Field notes / open questions for the founder

1. **Recipe embedding vs. reference.** Ring 1 derivations carry a
   runnable recipe. Inline it in `proposal.derivation.recipe` (fully
   self-contained review file, larger bytes) OR reference it by content
   hash to a separate artifact (smaller, but now two hashes to audit)?
   Recommendation: **inline** for v1 — self-containment beats brevity
   for the founding facts.
2. **`decision.outcome` enumeration.** Proposed: `sealed` | `withdrawn`
   | `held` (unresolved, stays in review forever per P6). Is `held` a
   terminal state that ever gets a review file hashed, or does
   `process_hash` only exist for `sealed`? Recommendation: `process_hash`
   is computed only at seal, so a held proposal has no sealed hash —
   its review file lives unsealed in the public review zone.
3. **Batch proposals (P11).** For a batch, does each fact get its own
   review file (referencing the shared batch review) or does the batch
   review file cover all rows? Recommendation: **each fact its own
   file**, with a `batch_ref` field pointing at the shared
   ingestion-script/source-pin review — matches P11's "each fact still
   receives its own record, ID, and dispute window."
4. **Timestamp trust.** `at` timestamps are self-asserted by
   participants. Should the review file bind to something external (the
   Git commit timestamps of the PR, which are independently witnessed)?
   Recommendation: treat Git history as the authoritative timeline and
   note that `at` fields are convenience, not proof — the PR's commit
   graph is the witnessed record.
5. **Machine annotation reproducibility.** An `annotation` with
   `by: "machine"` SHOULD name the checker version so the flag can be
   reproduced. Add `tool_version`?

## What a verifier does with it

Given a sealed fact and its published review file:
1. Recompute `SHA-256(JCS(review_file))` and check it equals the sealed
   `process_hash`. (Tamper-evidence for the process, mirroring the
   fact's own content hash.)
2. Confirm `review_file.fact_id` / `triple_hash` match the sealed fact.
3. Re-run the machine annotations against the proposal and confirm the
   recorded results.
4. Confirm `decision.outcome == "sealed"` and
   `decision.unresolved_objections == 0` (P6: seal only after
   objections resolve).

Steps 1–4 are implementable in the same reference module as
`ledger.verify` and SHOULD ship in the verifier SDK (post-genesis
build item) so "audit the process" is a one-command exercise, not a
code read.

## Next step

Founder settles the five open questions, then this file loses its
`.draft` suffix and its wording is folded into SCHEMA s7.4 / a new s13.
It does **not** need to be one of the six genesis-hashed documents (the
review format can evolve by governance record like any other rule), but
the version string (`review_format_version`) travels inside each review
file so a verifier knows which rules applied.
