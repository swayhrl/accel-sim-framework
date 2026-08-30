# Source diff summary

M1 replaces implicit static payload identity assumptions with an explicit, globally indexed substrate without changing the active behavior.

- The namespace contains 1,152 slots: resident IDs `0..1023` and reserved bypass IDs `1024..1151`.
- For the active static policy, resident tag `i` reserves exactly payload ID `i`; no allocator changes admission or replacement decisions.
- A payload handle carries ID plus generation. Freeing a bypass slot clears its owner/state and advances its generation, making stale handles invalid.
- The tag sidecar is indexed by the existing static L2 tag and records the canonical handle. Access/admission rollback restores both store and sidecar; fill accepts only the matching live owner/handle.
- Existing bank class is preserved by deriving it from `payload_id % 4`; legacy bank arbitration remains in force.
- `Unified`, `RO`, `TVD`, and adaptive/headroom controls remain disabled and are rejected if enabled. M1 does not produce bypass traffic.

This is infrastructure only, not a long-term functional mode bit.
