# MVP-14B2.9 Knowledge Graph Assembly

- Entity nodes: 46
- Proposition nodes: 2
- Literal nodes: 52
- Event nodes: 19
- Edges: 80

## Invariants
- Every graph edge points to existing nodes.
- Every graph edge has verified source evidence.
- Character beliefs remain proposition nodes and are not promoted to world-state facts.
- Graph assembly consumes only trusted Entity / Relation / Event stores.
- Node and edge identifiers are deterministic.