# Payload handle and sidecar contract

## Active M1 contract

1. The global payload ID is the canonical payload identity.
2. Resident tag `i` maps to payload ID `i` under the only supported policy (`static`).
3. The bank class is `payload_id % 4`; existing bank arbitration consumes the same class.
4. The L2 tag-sidecar entry holds `{payload_id,generation}` for the resident tag.
5. A live handle must match slot generation and owner. Fill/completion checks both before mutating terminal state.
6. Admission failure rolls back the store reservation and tag-sidecar assignment together.
7. Bypass IDs are present only as substrate capacity. No production M1 path allocates or emits bypass traffic.
8. Releasing a bypass ID increments generation, so a prior handle cannot become valid after reuse.

The contract deliberately leaves Unified Payload Pool, RO pending-state, TVD, and headroom unimplemented.
