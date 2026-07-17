# registries/

Unsealed registries: append-only on IDs, freely correctable otherwise.

| File | Contents |
|---|---|
| `entities.json` | `SK-ENT-` IDs → domain, labels, description, same_as |
| `predicates.json` | `SK-PRED-` IDs → definitions (incl. epistemic hedges) |
| `sources.json` | `SK-SRC-` IDs — the whitelist; changes only via governance records |
| `contributors.json` | `SK-USR-` IDs → handle; opt-in and erasable |

Nothing in this directory is hashed into the chain except where genesis
or a governance record seals a snapshot hash.
