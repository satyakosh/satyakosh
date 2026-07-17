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
| seal | PASS | 9000 facts + genesis in 0.9s (10032 seals/s) |
| verify clean chain | PASS | 0 findings expected, got 0 in 0.3s |
| verify(full) seal-time replay | PASS | 0 findings expected, got 0 in 1.1s |
| no near-duplicate flags | PASS | 0 flag(s) |
| deterministic chain head | PASS | 77bf9a05a8487a28... |
| duplicate refusal | PASS | 20/20 refused |
| tamper detection | PASS | 30/30 single-field mutations detected |
| chain intact after restore | PASS | verified |
| save/load round-trip | PASS | 11.6 MB ledger file |

Synthetic chain head: `77bf9a05a8487a28381be0756a1e4c47e40184415d5779eac5198f68e3862ccf`

Re-run: `python3 stress/volume_test.py --report` (byte-reproducible).
