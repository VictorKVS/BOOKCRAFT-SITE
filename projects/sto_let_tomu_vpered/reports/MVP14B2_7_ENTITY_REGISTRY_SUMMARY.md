# MVP-14B2.7 Entity Registry

- Canon claims input: 95
- Entities registered: 46

## Entity types
- CHARACTER: 42
- CREATURE: 1
- OBJECT: 1
- TECHNOLOGY: 2

## Invariants
- Entity IDs are deterministic and unique.
- Entities are linked only to trusted canon claims.
- Referenced names must already exist in source mention extraction.
- The registry does not invent free-form entities from arbitrary text.