# S1 design and bounded-resource cost

Arm: `S1_PARTITION_HIT_SERVICE`.

## Scientific role

S1 is an oracle for transient data availability at the existing L2
subpartition. It is not a data buffer and not a hardware proposal. It asks
whether the R101R2 O2 opportunity survives after restoring normal L1 behavior,
request interconnect delivery and the accepted partition-side hit resources.

It must not be interpreted by subtracting its response from O2 or B0 as a
runtime fraction attributable to L1, interconnect or cache.

## Placement

The only functional hook is in
`memory_sub_partition::cache_cycle`, after:

1. ordinary coalesced access construction;
2. accepted VM translation;
3. normal L1 behavior;
4. normal request interconnect delivery;
5. insertion at the existing `m_icnt_L2_queue` head.

Consequently, an L1 hit never reaches S1. There is no S1 hook in
`ldst_unit` or another SM-side path.

Classification uses the preserved SimVA and asserts the accepted identity
mapping at the partition hook:

`SimVA == SimPA == routed request address`.

Only a 32-byte ordinary global LDG, LDGSTS or WRITE fully contained in one
current live A/B/X region can use S1. Atomic, unsupported, dead, partial,
multiple-region and invalid-range requests fail closed to the ordinary
hierarchy.

## Existing finite resources reused

The accepted RTX4080/V1 configuration provides 16 L2 subpartitions and a
sector L2 with:

- 128-byte line;
- 32-byte atom/data-port width;
- existing `icnt-to-L2`, `L2-to-DRAM`, `DRAM-to-L2` and
  `L2-to-icnt` finite queues with their accepted configured sizing;
- one normal L2 access attempt per subpartition cache cycle;
- existing response queue and return interconnect arbitration.

S1 calls `l2_cache::awma_s1_partition_hit` only when the existing L2 data
port and output conditions permit the normal access attempt. That method
charges the existing hit data-port bandwidth and L2 hit statistics. The
ordinary L2 tag/data arrays are not probed, allocated or updated for the
oracle data. The existing HIT reply handling pushes the original
`mem_fetch` to the existing `m_L2_icnt_queue`.

No S1 request queue, ready queue, response port, cache way, victim buffer or
cross-subpartition path exists. Formal telemetry observes maximum existing
ingress/return occupancies of 61/64 and 365,356 qualified-head cycles blocked
by the existing full return queue; these are observations, not new configured
resources.

The accepted configuration has `gpgpu_l2_rop_latency=0`; S1 therefore does
not invent a nonzero latency. Its modeled latency is the exact accepted hit
path: existing queue wait, one data-port service quantum, response queue and
return interconnect/arbitration.

## Activation and OFF behavior

The functional selector is:

`AWMA_R101R3_SERVICE_MODE=none|s1_partition_hit`

and defaults to OFF when absent. Diagnostic queue/backpressure counters use
the separate selector:

`AWMA_R101R3_DIAGNOSTICS=0|1`.

R101R2 O2 remains separately selectable and cannot be combined with S1.
The transient replacement mechanism remains `none`.

Kernels 1-3 use the normal hierarchy. S1 can serve only kernels 4-6 under the
accepted sidecar ROI markers.

## Correctness accounting

S1 records:

- served reads, LDG reads, LDGSTS reads and writes;
- request and active bytes;
- fail-closed categories;
- duplicate application;
- context service;
- ingress/return maximum occupancy;
- cycles with a qualified head blocked by existing DRAM-output, return-output
  or L2 data-port state;
- subpartition participation mask.

LDGSTS returns through the existing DEPBAR path, LDG through the existing
scoreboard path, and writes through the existing store-ACK path because the
original `mem_fetch`, reply conversion and return path are retained.

Terminal correctness additionally relies on the accepted whole-GPU,
translation, cache, interconnect and memory drain gates. S1 has no private
outstanding queue to hide at termination.

## Cost boundary

S1 adds control predicates and counters in the simulator but no modeled data
capacity. Its oracle-data source has no realizable storage cost. Therefore S1
may localize a useful service point, but it cannot be promoted as a finite
hardware mechanism or compared as area/energy evidence.
