# Open semantic boundaries

`C16WARP1` contains lane starting addresses, not access widths.  The hardening decoder accepts only an explicit width-bearing static opcode when it exactly equals the SASS mnemonic.  Bare `STG.E` remains `WIDTH_UNKNOWN`; its page/line values are explicitly start-address buckets, not touched-range claims.

Every V2 MREF shard is a distinct replay selected by immutable `C16_WARP_STATIC`.  The raw containers carry one object map without a per-shard process/address-space binding, stable object-relative normalization, or repeatability/layout-equivalence proof.  Therefore all active events remain `UNKNOWN_RUNTIME`; object unions are unsupported.

Per-shard starting-address footprints and exact static-MREF executed/zero closure remain FORMAL.  Cross-shard absolute VA/page/line unions are retained only as `REPLAY_UNION_DIAGNOSTIC`; no whole-launch physical footprint, temporal order, reuse distance, or global hardware order is claimed.
