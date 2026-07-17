# Volume stress test — schema 1.0.0 validator/serializer/chain @ ~9,000 records

*Note: the schema was tested under its internal draft designation v2.1,
renumbered 1.0.0 at the first public commit. The tested bytes and rules
are identical; only the label changed.*

Diversity (3 semantic rounds) tested what categories the schema can hold;
volume tests whether the machinery holds at scale, including under attack.
`stress/volume_test.py`, deterministic seed 20260709. **Result: ALL PASS.**

| Test | Result |
|---|---|
| A1–A7 admissible categories (defined, measured, mathematical, conditional, taxonomic, derived-exact, multi-condition) | 7 × 1000/1000 valid |
| X1 inadmissible (statistical, documentary, causal, institutional) | 1000/1000 rejected, all by the admissibility gate specifically |
| X2 malformed/hostile (14 attack kinds: non-normalized notation, `+` signs, `-0`, uppercase E, JSON-number smuggling, leading-dot mantissa, spaced units, unsorted conditions, unknown IDs, off-whitelist source, bad timestamps, tampered triple_hash, exact-with-uncertainty) | 1000/1000 rejected |
| Notation attack (`1000`, `10e2`, `0.1e4`, `+1e3`, `1E3` = same number, illegal bytes) | 5/5 rejected by grammar; legal precision variants (`1e3` vs `1.0e3` vs `1.00e3`) correctly kept distinct |
| Exact-duplicate triple | detected |
| Near-duplicate heuristic (same subject/predicate/conditions, different value/unit) | fires as a warning (70 hits in hostile set), never a byte rule |
| Chain seal @ 1,000 records + 100 random tamper attempts | 100/100 detected |
| Determinism (independent re-serialization round-trip) | 0/1000 hash mismatches |
| v1 ASCII invariant on canonical bytes | 0/1000 violations |
| 12-hex fact-ID prefix collisions @ 7,000 facts | 0 (birthday p≈0.37 at 16M; escalation rule engages long before) |

## Findings that changed the schema (already folded into 1.0.0)
1. **Value grammar hardened to normalized scientific notation.** The earlier draft
   grammar let `1000` / `1e3` / `1.0e3` coexist — same number, different
   bytes, different hashes: duplicate detection silently defeated. 1.0.0
   admits exactly one byte-form per (number × precision); significant
   figures = mantissa digit count, preserved verbatim.
2. **Condition ordering needed a tie-break.** Two conditions may share a
   property (min/max range pairs). Sort by property alone is not a total
   order; 1.0.0 tie-breaks by the JCS bytes of the condition object.
3. **Unit-equivalence duplicates cannot be a byte rule.** `Cel` vs `K`
   restatements of one claim hash differently by design; caught instead by
   the near-duplicate *warning* routed to human review.
4. **v1 canonical bytes are provably pure ASCII** (IDs, codes, numbers,
   dates only) — the NFC rule is future-proofing for reserved types, now
   enforced as an explicit validator invariant.
