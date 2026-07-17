# Volume test report (rebuilt implementation)

The pre-2026-07-15 report was lost with the original working
copy; this report supersedes it and describes the rebuilt test
(stress/volume_test.py). Synthetic data only, validated
against the founding rulesets as committed (entity IDs
founder-confirmed 2026-07-17).

- Date: 2026-07-17 · Python 3.14.6 on Windows
- Scale: 9000 facts + 1 genesis record, fixed seed 20260707

| Check | Result | Detail |
|---|---|---|
| seal | PASS | 9000 facts + genesis in 1.3s (6863 seals/s) |
| verify clean chain | PASS | 0 findings expected, got 0 in 0.3s |
| verify(full) seal-time replay | PASS | 0 findings expected, got 0 in 1.7s |
| no near-duplicate flags | PASS | 0 flag(s) |
| deterministic chain head | PASS | 605ebebaffb57c8e... |
| duplicate refusal | PASS | 20/20 refused |
| tamper detection | PASS | 30/30 single-field mutations detected |
| chain intact after restore | PASS | verified |
| save/load round-trip | PASS | 11.5 MB ledger file |

Synthetic chain head: `605ebebaffb57c8e45dc02bf3ce6085fec84b6018f9b70fea2f3c7b9b3f560ef`

Re-run: `python3 stress/volume_test.py --report` (byte-reproducible).
