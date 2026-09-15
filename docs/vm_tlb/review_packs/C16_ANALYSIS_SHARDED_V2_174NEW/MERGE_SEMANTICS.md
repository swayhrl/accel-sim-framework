# V2 merge semantics

`CTA_SHARDED_ALL_MREF` requires non-overlapping declared CTA IDs and a matching
model/input/scenario/function/code-object/launch-selector/static-MREF-set
identity in every child `RUN_MANIFEST`.  It produces per-shard and per-CTA
fingerprints plus set unions of page, line, address, static-MREF, object,
access, and width facts.  CTA children may be partial only when the logical
manifest declares expected child RUN_IDs; the output is then
`PARTIAL_SHARDS_PRESENT`.

`MREF_SHARDED_COMPLETE_SET` requires disjoint integer static-MREF groups.  The
union must exactly equal `selected_static_mref_indices`; otherwise analysis
fails closed.  Every parsed record must lie in its child's declared CTA/MREF
selector.

No aggregate contains a concatenated cross-shard stream.  Every merge writes
`aggregate_order_label=CROSS_SHARD_ORDER_PROHIBITED`,
`cross_shard_reuse_distance=UNSUPPORTED`, and receipt-level unsupported claims:
`CROSS_SHARD_ORDER`, `CROSS_SHARD_REUSE_DISTANCE`, and `GLOBAL_HARDWARE_ORDER`.
