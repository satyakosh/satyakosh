# ledger/

`ledger.py` is the reference implementation: canonicalization, hashing,
validation, sealing, chain verification.

The sealed chain itself will also live here — and it is **empty on
purpose**: nothing seals until the Genesis Window completes, because
every record, including record 0, must pass its process in public.

When the chain exists, verify it with the standalone verifier:
`python verify.py <chain.json>` (repo root -- one file, stdlib only,
independent of this engine), or in depth via
`Ledger(...).verify(full=True)`.
