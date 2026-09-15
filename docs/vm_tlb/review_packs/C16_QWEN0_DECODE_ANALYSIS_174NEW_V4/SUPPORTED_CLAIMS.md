# Supported claims

- All three Decode containers and every declared artifact independently hash-close.
- The 98 selected direct `GLOBAL + MREF` static rows close exactly as executed or proven-zero.
- Access kind is derived only from each hash-bound static row; width is exact only for a matching explicit SASS mnemonic.
- Per-shard start-address footprints, and touched-range footprints for exact-width subsets, are formal within that shard's process-local address space.
- Object attribution uses only the same shard's hash-bound `C16_ADDRESS_CONTEXT_V1`; unmatched addresses remain `UNKNOWN_RUNTIME`.
- The consolidated table is an analysis baseline, not a physical whole-kernel absolute-VA union.

Unsupported: cross-replay absolute-VA union as a physical footprint, cross-shard temporal order, reuse distance, cross-process object joins, and object-relative comparison without an exact matched semantic identity.
