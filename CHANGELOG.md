# Changelog

Public versioning starts at 1.0.0. Version numbers track the
canonical-byte contract (SCHEMA.md s10).

## 1.0.0-rc.1 (Genesis Window candidate) — 2026-07
- First public version. Internal draft lineage renumbered.
- P11 batch-proposal mechanism added to the pipeline policy.
- ASCII invariant scoped to fact records; genesis defined as NFC UTF-8.
- Genesis record enumerates six founding-document hashes plus the inline
  whitelist.
- Validator hardening (2026-07-16): record 0 must be genesis; duplicate
  canonical triples refuse to seal; fact seals refuse while any ruleset
  in force carries operative placeholders; the intake tool flags unknown
  derivation types; malformed proposals get citable rejections, not
  crashes.
- Intake tool CLI + input hardening; property-based canonicalization
  tests (stress/test_canonical_properties.py) including a byte-for-byte
  cross-check of the JCS implementation against an independent RFC 8785
  library.

## Internal prehistory (never public, preserved for the record)
- v0 (2026-07-07): first prototype — schema, five CODATA seed facts,
  ledger engine, live tamper-detection demo. PyPI 0.0.1 name reservation.
- v2.0 (2026-07-09): semantic-triple restructure; JCS canonicalization;
  content-addressed IDs; D1-D8 locked.
- v2.1: typed object union; typed conditions; value grammar one-byte-form;
  ~130-fact semantic stress test; ~9,000-record volume test.
- v2.1-rc2 (2026-07-09): witnessed mandatory-condition ruleset; external
  four-perspective review closed with no hash-breaking findings.
- 2026-07-15: local working copy lost; repository rebuilt from session
  transcripts and the locked decision record (see RECOVERY_NOTES.md).
