# Passive memo contract

- Execution remains frozen RTX4080/V1 OFF 10/80; all candidate modes are off.
- A lookup is observed once when a logical access first reaches the frozen
  head translation decision point. Retries are counted separately and never
  inflate memo lookups.
- A mapping enters the observer only after that same access naturally returns
  READY through the baseline controller and is legally applied.
- Identity is `(ASID, VPN, page_size, translation_generation,
  translation_access)`; the completion PPN must also match the recorded PPN.
  The current source exposes read/write/atomic as the permission-relevant
  access dimension; no unsupported permission field is invented.
- Memo state is keyed by `(shader id, dynamic warp-instruction uid)` and is
  destroyed when that instruction's accessq becomes empty. It never crosses
  an instruction, warp, CTA, or kernel.
- Capacities 1, 2, and 4 are observed in parallel. All use deterministic LRU;
  insertion happens only on natural completion and a legal hit updates recency.
- Reuse distance is the number of intervening natural completions in the same
  instruction. No trace position or future event is consulted.
- A provisional identity hit becomes a reported hit only after baseline
  completion confirms identity and PPN consistency.
- The observer never skips translation, consumes READY, changes queues,
  ordering, arbitration, cache/memory behavior, or downstream application.
