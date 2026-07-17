# derivations/

Runnable verification recipes, one per fact, named
`<triple_hash>.py`. Each recipe is pinned by its SHA-256 twice: as
`derivation.script` inside the sealed fact record (SCHEMA s4.1) and in
the frozen review file (docs/review_file_format.md) — sealing freezes
the file. Recipe artifacts are stored and mirrored alongside review
files.
