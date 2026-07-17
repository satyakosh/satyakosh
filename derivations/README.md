# derivations/

Runnable verification recipes, one per fact, named
`<triple_hash>.py`. Each recipe is pinned by its SHA-256: the review
file records it as `recipe_hash` (docs/review_file_format.md), freezing
the file — the recipe seals with the fact's process. Whether the recipe
hash additionally appears inside the sealed fact record itself
(`derivation.script`, per the recovered original SCHEMA s4.1) is under
founder reconciliation — see docs/rebuild_divergence_report.md.
