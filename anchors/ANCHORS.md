# Chain-head anchor log (docs/durability.md, FD-33)

One row per sealed batch, plus a quarterly heartbeat. Each row is
committed and signed like everything else and propagates to every
mirror in the same push; the .ots files are OpenTimestamps proofs
(pending attestations upgrade to Bitcoin block attestations after
aggregation — run `ots upgrade` on them any time after ~a day).
The anchor log is corroboration, not authority: the chain remains
self-verifying, and a verifier who distrusts this log simply
ignores it.

| date | records | chain_head | sha256(chain.json) | git commit | note |
|---|---|---|---|---|---|
| 2026-07-20 | 1 | f3995a8fe67fc6adb949a99bd8bf146ced6a95c74881f0dd5910050aeebe4615 | b7884b5b9f9ac39a9513e6b8b169cbde69c39401272ea58a171148fd12daf65e | 1d1a35e | GENESIS. Record 0 sealed 2026-07-20T11:05:55Z; content_hash ebd53369…; .ots stamped by 3 calendars (genesis_record.json.ots) |
