# Transient region contract

Runtime schema: `AWMA_TRANSIENT_L2_RUNTIME_V1`.

The strict derived sidecar contains:

- one `LINE_SIZE 128` record;
- one `EXPECTED_KERNELS N` record;
- exactly four initial `REGION id base limit generation live` records for
  A/B/X0/X1;
- finite `BOUNDARY completed_kernel_ordinal region_id generation live` records.

Raw producer bytes remain immutable. The consumer derives this view only after
verifying the producer commit, review manifest, stable simulator-input identity,
trace member hashes/order, terminal `drop=0/overflow=0`, exact four aligned
regions and lifetime rows. Missing initial live/generation state fails closed.

No per-line last read, next access, future trace position, synthetic region,
tile subset, or address inference is accepted.

Mode semantics:

- absent selector: default OFF, no metadata/output/behavior;
- `none`: observational region/generation metadata only;
- `oracle_dead_drop`: zero-cost boundary scan, resident dirty dead-generation
  lines invalidated without writeback;
- `bounded_live_retention`: lazy descriptor state, finite victim priority and
  dead dirty eviction drop; no whole-L2 scan.

Generation is an 8-bit positive non-decreasing value. Reversal or wrap asserts.
An old-generation line is dead after a descriptor advances. All formal
generation counts are far below 255.

Replacement order is exactly:

`invalid > dead transient > ordinary baseline-eligible > live transient`.

If only live transient ways are baseline-eligible, the baseline LRU/FIFO victim
is used and dirty data writes back normally. Reserved ways remain illegal.
