# stress/

Test suites and their reports.

| File | What it is |
|---|---|
| `test_ledger.py` | Deterministic validation/chain suite (incl. the K-series regression battery) |
| `test_governance.py` | Governance-engine suite: simulated Ring-2 activation, ASCII-narrowing dry-run, negative deltas, issue #7 G1–G5 regressions (position-correct audit replay, ruleset structural validation, genesis digest binding, inline-whitelist authority, UCUM syntax) |
| `test_canonical_properties.py` | Hypothesis property tests for the s7 invariants, incl. an independent RFC 8785 cross-check |
| `fuzz_validator.py` | Deterministic mutation fuzzer: any mutant either seals clean or gets a citable rejection — never a crash |
| `volume_test.py` | ~9,000-record volume test of seal/verify/determinism/tamper/save-load |
| `VOLUME_TEST_REPORT.md` | Report of the current (rebuilt) volume test |
| `VOLUME_TEST_REPORT-2026-07-09.md` | The recovered original pre-loss report (historical record; documents the findings that shaped the value grammar) |

All of these run in CI on every push and pull request.
