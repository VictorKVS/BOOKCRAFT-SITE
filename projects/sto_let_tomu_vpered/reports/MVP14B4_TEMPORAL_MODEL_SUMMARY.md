# MVP-14B4 Temporal Model

- Canon claims input: 95
- Temporal anchors: 95
- Textual order edges: 94
- Review queue: 0
- Normalized world-time anchors: 0

## Semantics
- Current v1 models verified textual order only.
- TEXTUALLY_BEFORE means earlier in the primary source, not necessarily earlier in physical story time.
- No calendar/date/time values are invented.
- CHARACTER_BELIEF and WORLD_STATE scopes are preserved unchanged.

## Invariants
- Only trusted canon claims are temporally indexed.
- Every timeline item has a verified source anchor.
- Temporal IDs are deterministic.
- Textual ordering is explicitly separated from world-time semantics.