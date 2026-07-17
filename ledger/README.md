# ledger/

`ledger.py` is the reference implementation: canonicalization, hashing,
validation, sealing, chain verification.

The sealed chain itself will also live here — and it is **empty on
purpose**: nothing seals until the Genesis Window completes, because
every record, including record 0, must pass its process in public.

When the chain exists, verify it with `Ledger(...).verify(full=True)`
(a standalone verifier CLI ships with the Genesis Window).
