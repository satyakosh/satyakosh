#!/usr/bin/env python3
"""Property-based tests for the canonicalization/hashing invariants
(SCHEMA s7). Complements the deterministic self-tests: Hypothesis
generates thousands of randomized records and asserts the invariants
that the whole chain depends on.

Test-only dependency: hypothesis (the reference implementation itself
stays stdlib-only). Optional: if the `rfc8785` package is installed,
every generated record is also cross-checked byte-for-byte against that
independent RFC 8785 implementation — the JCS-equivalence claim in
ledger.py's docstring is a Genesis Window review target.

Run:  pip install hypothesis          (optionally: pip install rfc8785)
      python3 stress/test_canonical_properties.py
"""
import json
import random
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ledger"))
import ledger as L

try:
    from hypothesis import given, settings, strategies as st
except ImportError:
    print("hypothesis not installed — run: pip install hypothesis")
    sys.exit(2)

try:
    import rfc8785
    HAVE_RFC8785 = True
except ImportError:
    HAVE_RFC8785 = False

MAX_EXAMPLES = 500

# ---------------------------------------------------------- strategies

ascii_key = st.text(
    alphabet=st.characters(min_codepoint=0x20, max_codepoint=0x7E),
    min_size=1, max_size=12)

# any JSON-representable string, including non-BMP and combining marks
any_string = st.text(min_size=0, max_size=24)

json_scalar = st.one_of(
    st.none(), st.booleans(), st.integers(min_value=-10**9, max_value=10**9),
    any_string)

json_value = st.recursive(
    json_scalar,
    lambda children: st.one_of(
        st.lists(children, max_size=4),
        st.dictionaries(ascii_key, children, max_size=4)),
    max_leaves=12)

# strings matching the s7.3 value grammar
grammar_value = st.from_regex(L.VALUE_RE, fullmatch=True)

ent_id = st.integers(min_value=1, max_value=999999).map(
    lambda n: f"SK-ENT-{n:06d}")

quantity = st.builds(
    lambda v, u, e: {"type": "quantity", "value": v, "unit": u,
                     "exact": e, "uncertainty": None},
    grammar_value, st.sampled_from(["m/s", "J.s", "kPa", "1", "Cel"]),
    st.booleans())

condition = st.builds(lambda p, o: {"property": p, "object": o},
                      ent_id, quantity)

triple = st.builds(
    lambda s, o, c: {"subject": s, "predicate": "SK-PRED-000001",
                     "object": o, "conditions": c},
    ent_id, quantity, st.lists(condition, max_size=5))

# ---------------------------------------------------------- properties

@settings(max_examples=MAX_EXAMPLES)
@given(json_value)
def p_jcs_deterministic_and_key_order_free(obj):
    """Same content, any key insertion order -> identical canonical bytes."""
    a = L.jcs(obj)
    if isinstance(obj, dict):
        items = list(obj.items())
        random.shuffle(items)
        obj = dict(items)
    assert L.jcs(obj) == a
    # canonical bytes must round-trip to an equal object (NFC-normalized)
    assert json.loads(a.decode("utf-8")) == L.nfc(obj)


@settings(max_examples=MAX_EXAMPLES)
@given(json_value)
def p_nfc_idempotent(obj):
    """Normalizing twice must equal normalizing once (jcs applies NFC)."""
    assert L.jcs(L.nfc(obj)) == L.jcs(obj)


@settings(max_examples=MAX_EXAMPLES)
@given(triple)
def p_triple_hash_condition_order_free(t):
    """Shuffling the conditions array never changes the triple hash."""
    h = L.triple_hash(t)
    shuffled = dict(t)
    shuffled["conditions"] = t["conditions"][:]
    random.shuffle(shuffled["conditions"])
    assert L.triple_hash(shuffled) == h


@settings(max_examples=MAX_EXAMPLES)
@given(triple, st.text(min_size=1, max_size=64))
def p_content_hash_excludes_chain_fields(t, junk):
    """content_hash covers content only; chain fields never affect it
    (SCHEMA s7.4)."""
    rec = {"record_type": "fact", "triple": t, "version": 1}
    h = L.content_hash(rec)
    rec["prev_record_hash"] = junk
    rec["content_hash"] = junk
    assert L.content_hash(rec) == h


@settings(max_examples=MAX_EXAMPLES)
@given(grammar_value)
def p_grammar_accepts_only_one_byte_form(v):
    """Every accepted value survives the grammar's own constraints:
    no '+', no uppercase E, no leading-zero exponent, single leading digit."""
    assert "+" not in v and "E" not in v
    if v != "0":
        mant, exp = v.split("e")
        assert not exp.lstrip("-").startswith("0") or exp in ("0", "-0")
        assert exp != "-0"
        lead = mant.lstrip("-")[0]
        assert lead in "123456789"


@settings(max_examples=MAX_EXAMPLES)
@given(grammar_value, st.sampled_from(["+", "E", " ", "."]))
def p_grammar_rejects_mutations(v, junk):
    """Guaranteed-invalid formatting mutations must be rejected.
    (Digits are NOT safe junk: "1e1" + "00" = "1e100", a valid value.)"""
    for mutant in (v + junk, junk + v, "0" + v, v + "e",
                   v.replace("e", "E", 1)):
        if mutant != v:
            assert not L.VALUE_RE.fullmatch(mutant), mutant


@settings(max_examples=MAX_EXAMPLES)
@given(triple, st.characters(min_codepoint=0x80))
def p_ascii_guard_catches_any_nonascii(t, ch):
    """Injecting any single non-ASCII character anywhere in a fact record
    must trip the s7.2 guard (homoglyph tripwire)."""
    rec = {"record_type": "fact", "triple": t}
    rec["triple"] = dict(t)
    rec["triple"]["subject"] = t["subject"] + ch
    normalized = unicodedata.normalize("NFC", ch)
    if not normalized or all(ord(c) < 0x80 for c in normalized):
        return  # NFC maps it into ASCII; guard correctly stays silent
    try:
        L._ascii_guard(rec)
        assert False, f"guard missed U+{ord(ch):04X}"
    except L.ValidationError:
        pass


if HAVE_RFC8785:
    @settings(max_examples=MAX_EXAMPLES)
    @given(json_value)
    def p_jcs_matches_rfc8785(obj):
        """ledger.jcs must be byte-identical to an independent RFC 8785
        implementation for Satyakosh's data shape (no floats)."""
        assert L.jcs(L.nfc(obj)) == rfc8785.dumps(L.nfc(obj))


# ---------------------------------------------------------- runner

if __name__ == "__main__":
    props = [v for k, v in sorted(globals().items()) if k.startswith("p_")]
    failed = 0
    for prop in props:
        try:
            prop()
            print("PASS -", prop.__name__)
        except AssertionError as e:
            failed += 1
            print("FAIL -", prop.__name__, "->", e)
    if not HAVE_RFC8785:
        print("SKIP - p_jcs_matches_rfc8785 (pip install rfc8785 to enable)")
    print(f"\n{len(props) - failed}/{len(props)} properties held "
          f"({MAX_EXAMPLES} examples each)")
    sys.exit(1 if failed else 0)
