# conformance/

Language-agnostic conformance vectors for the Satyakosh chain format.
The format is three open standards — JSON, RFC 8785-style canonical
serialization under the no-floats rule, SHA-256 — and the normative
specification is SCHEMA.md. Python is a reference convenience, not a
dependency: an implementation in any language conforms if it
reproduces `vectors.json`.

## The contract

An implementation CONFORMS if:

1. For every `jcs`, `triple_hash`, `content_hash`, and `chain_link`
   case it reproduces the expected canonical bytes and digests
   exactly.
2. For every `chains` case it reproduces the `chain_head` and the
   `intact` verdict.

Finding **message text** is deliberately NOT part of the contract:
hostile input may surface under different labels across languages
(a stored JSON float is a citable canonicalization refusal in
Python, but a language whose parser reads `1.0` as the integer `1`
will surface the same corruption as a hash mismatch instead). The
intact/not-intact verdict must agree; the wording may differ.

## What an implementer must get right

- **NFC first.** Every string is Unicode-NFC-normalized before
  serialization. The two NFC vectors (decomposed vs composed `é`)
  must produce byte-identical canonical output.
- **Key order is code-point order.** Object keys sort
  lexicographically by Unicode code point — not by UTF-16 code unit
  (they differ for astral-plane keys), not locale-aware.
- **Integers only.** No number in canonical form is ever a float
  (SCHEMA s7.1); quantity values are strings under the s7.3 grammar.
  Refuse or surface any float you encounter — it can only be hostile.
- **Minimal JSON escaping, UTF-8 output.** `"` and `\` escaped;
  C0 controls escaped (`\n`, `\t`, `\b`, `\f`, `\r`, else `\u00XX`);
  everything else emitted as literal UTF-8 bytes — never `\u`
  escapes for non-ASCII.
- **Condition sort.** A triple's conditions sort by `property`, ties
  broken by the condition object's canonical bytes.
- **content_hash** hashes the record body with `content_hash` and
  `prev_record_hash` removed. **chain head** folds
  `sha256(ascii(content_hash + prev_link))` from 64 zeros.

## Regeneration

`tools/make_conformance_vectors.py` regenerates `vectors.json`
deterministically from the reference implementation; CI runs it with
`--check` on every push, so the committed vectors can never drift
from the code. The standalone Python verifier (`verify.py`) and the
browser JavaScript verifier (satyakosh.org/verify.html, in the
website repository) are both held to these vectors.
