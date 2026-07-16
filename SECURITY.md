# Security policy

Satyakosh's security surface is unusual: there are no servers, accounts,
or secrets to steal. What can be attacked is the *guarantee* — that
sealed bytes are what they claim to be and that nothing enters the chain
except through the pipeline. Breaking that guarantee, or showing how it
could be broken, is the most valuable contribution this project can
receive.

## What counts as a security finding

- Canonicalization ambiguity: two byte-forms for the same claim, or a
  divergence between `ledger.py` and RFC 8785 (JCS)
- Hash or chain-integrity weaknesses: a tamper `verify()` misses, a
  collision-handling gap, a way to alter history undetected
- Validator bypass: a record that seals despite violating SCHEMA s11,
  the value grammar (s7.3), the ASCII tripwire (s7.2), mandatory
  conditions, or the admissibility map
- Unicode attacks the homoglyph/invisible-character tripwire misses
- Intake-gate weaknesses: malformed proposals that crash rather than
  receive a citable refusal
- A scope violation (SCOPE S1-S7) that the rules as written would
  wrongly allow to seal

Label typos, rendering issues, and documentation errors are welcome too
— as ordinary public issues, not security reports.

## How to report

Default to a **public GitHub issue**. Public adversarial review is this
project's design, not a courtesy: most findings are safest in the open.

If you believe public disclosure before a fix would enable tampering
with data others already rely on, use GitHub's private vulnerability
reporting ("Report a vulnerability" under the repository's Security
tab) and it will be handled and disclosed publicly after a fix.

## Recognition

There is no monetary bounty. Per PIPELINE_POLICY P10, validated catches
during the Genesis Window earn **permanent sealed inscription on the
chain itself**; after the window, RING2.md s9 extends the same
recognition. A hash-breaking flaw found during the window restarts the
window — finding one is not an embarrassment to be managed but the
system working as designed.
