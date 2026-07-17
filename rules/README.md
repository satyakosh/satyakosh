# rules/ and rulesets/

Machine-readable rulesets whose hashes the genesis record enumerates.
Once genesis seals, these files are frozen: any change is a `governance`
record on the chain, never an edit here.

| File | What it is | Genesis field |
|---|---|---|
| `rules/admissibility_map.json` | Which derivation types may seal, and in which ring | `admissibility_map_hash` |
| `rulesets/mandatory_conditions.json` | Which conditions a fact class must state before it may enter review | `mandatory_conditions_hash` |

`ledger.py` refuses to seal — genesis or facts — while any operative
field in these files contains a placeholder marker. Commentary fields
(underscore-prefixed) are exempt.
