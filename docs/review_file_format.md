# Review-file format 1.0.0

**Status: settled by founder decision 2026-07-17** (decision record at
the end of this file). This defines the canonical review-file format
that `process_hash` commits to (SCHEMA s7.4). It is deliberately NOT
one of the six genesis-hashed documents: the format evolves by
governance record like any other rule, and `review_format_version`
travels inside each review file so a verifier knows which rules
applied.

## What the review file is

One review file per proposed fact, holding the complete public record
of how that fact passed the pipeline: the proposal, every automated
flag, every objection and its resolution, and the final decision. When
the fact seals, `process_hash = SHA-256(JCS(review file))` is sealed
with it — so the review can never be rewritten after the fact without
detection, exactly as the fact itself cannot.

## Design constraints

- **Deterministic bytes.** The review file is JSON; its canonical byte
  form is its RFC 8785 (JCS) serialization — one canonicalization law
  in the project, not two.
- **Append-only in spirit.** A review accretes events (flags,
  objections, resolutions). Entries are never edited or deleted; a
  correction is a new entry. The file is frozen at the instant of seal
  and its hash taken then.
- **Contributor pseudonymity (invariant 6 / P8).** Participants appear
  only as opaque `SK-USR-` IDs. The review file MUST NOT contain real
  names, emails, or platform handles — those live only in the deletable
  contributor registry, so right-to-erasure never touches a sealed
  `process_hash`.
- **NFC UTF-8, not ASCII.** A review is human discussion and may
  legitimately contain non-ASCII prose (an objection written in Hindi,
  a Devanagari label under discussion). The s7.2 ASCII tripwire applies
  to `fact` records, not to review files.

## Structure

```json
{
  "review_format_version": "1.0.0",
  "fact_id": "SK-R1-PHYS-9f3a2c81d4e0",
  "triple_hash": "9f3a2c81d4e0...<full 64 hex>",
  "batch_ref": null,
  "proposal": {
    "proposed_by": "SK-USR-000007",
    "proposed_at": "2026-08-01T12:00:00Z",
    "triple": { "...": "the exact triple submitted" },
    "derivation": { "type": "si_exact_definition",
                    "recipe_hash": "<sha256 of the recipe artifact>" },
    "sources": [ { "source": "SK-SRC-000001", "edition": "CODATA 2022",
                   "retrieved": "2026-08-01" } ]
  },
  "annotations": [
    { "at": "2026-08-01T12:00:03Z", "by": "machine",
      "tool_version": "check_mandatory_conditions.py@1.0.0-rc.1",
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

- **Recipe artifacts** are separate files pinned by `recipe_hash`
  (SHA-256 of the artifact's bytes). They live in the same repository
  and mirrors as review files — shared fate, no new availability risk.
  Batch rows all pin the same artifact.
- **`batch_ref`** (P11): for a batch-proposed fact, the `fact_id`-style
  identifier of the shared batch review (ingestion script + source pin
  + spot checks). `null` for individual proposals.
- **`decision.outcome`**: `sealed` | `withdrawn` | `held`. A held
  proposal (unresolved objections, P6) keeps a living, unsealed review
  file in the public review zone — visible forever, hashed never.
- **Timestamps**: `at` fields are convenience labels. The authoritative
  timeline is the Git commit history of the public review — the
  independently witnessed record.

## What a verifier does with it

1. Recompute `SHA-256(JCS(review file))`; check it equals the sealed
   `process_hash`.
2. Confirm `fact_id` / `triple_hash` match the sealed fact.
3. Fetch the recipe artifact; check its SHA-256 equals `recipe_hash`;
   run it.
4. Re-run the machine annotations (at the recorded `tool_version`) and
   confirm the recorded results.
5. Confirm `decision.outcome == "sealed"` and
   `decision.unresolved_objections == 0` (P6).

These steps ship in the verifier SDK (post-genesis build item) so
"audit the process" is a one-command exercise.

## Decision record (founder, 2026-07-17)

1. **Recipes are referenced by content hash**, not inlined — recipe
   artifacts are stored and mirrored alongside review files; batch rows
   deduplicate to one pinned artifact. (Mirrors the `process_hash`
   pattern itself.)
2. **`process_hash` is computed only at seal.** Held proposals have no
   sealed hash; their review files stay live and unsealed in public.
3. **One review file per fact, plus `batch_ref`** to the shared batch
   review — each fact keeps its own record, ID, and dispute window
   (P11).
4. **Git history is the authoritative timeline**; self-asserted `at`
   fields are convenience, not proof.
5. **Machine annotations name their `tool_version`** so every flag is
   reproducible.
