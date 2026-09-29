# Transient region contract

Runtime schema: `AWMA_TRANSIENT_L2_RUNTIME_V1`.

The strict derived sidecar contains:

- one `LINE_SIZE 128` record;
- one `EXPECTED_KERNELS N` record;
- one `EXPECTED_STREAM 0` record and 18 exact ordered `KERNEL` identities;
- exactly four initial `REGION id base limit generation live` records for
  A/B/X0/X1;
- 16 finite `PRE launch_ordinal region_id generation live` producer activations;
- 15 finite `POST completed_kernel_ordinal region_id generation live` deaths.

Raw producer bytes remain immutable. The consumer derives this view only after
verifying the producer commit, review manifest, stable simulator-input identity,
18 trace member hashes/order/header identities, terminal `drop=0/overflow=0`,
the four aligned non-overlapping regions, exact address intersections, and the
18 published kernel-boundary lifetime rows.

The producer publishes after-kernel states. The consumer starts each bounded
generation dead, activates a completely-written producer region at launch, and
applies only real deaths at completion. The first two normalization members have
no X0 intersection; X0 generation 1 activates at the third normalization launch.

Formal V1 admission requires every region base and size to be 128-byte
line-aligned. Unaligned/partial-line regions are outside the mechanism contract:
the policy's overlap-classification unit diagnostic is conservative for live
protection but does not establish safe dead-dirty drop when region-external
bytes share a line. No formal run admits such a descriptor.

No per-line last read, next access, future trace position, synthetic region,
unbounded descriptor, free capacity or other future-derived state is admitted.

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
