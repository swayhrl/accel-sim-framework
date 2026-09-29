# M1 design and cost

Design: `BOUNDED_LIVE_RETENTION_DEAD_DROP` (`MODELING_DECISION`).

M1 does not increase L2 data capacity, MSHRs, queues, ports or victim storage.
It adds four bounded descriptors and per-line region/generation metadata.

## Logical hardware state

Each L2 line needs:

- transient-valid: 1 bit;
- region ID: 2 bits for A/B/X0/X1;
- generation: 8 bits.

Total: 11 bits/line × 524,288 lines = 720,896 bytes = 704 KiB, 1.0742% of
the modeled 64 MiB data capacity. This is additional metadata, not data
capacity.

Each descriptor logically contains 64-bit base, 64-bit limit, 2-bit region ID,
8-bit generation, valid and live bits: 140 bits/descriptor, 560 bits (70 bytes)
for four descriptors before physical implementation alignment.

The exploratory C++ representation uses 2 bytes/line (1 MiB, 1.5625% of data)
and 24 bytes/descriptor (96 bytes total) because of host-language layout. Both
logical and simulator-storage costs are disclosed.

## Control/timing boundary

- region comparison and victim priority are modeled as zero added cycles in
  this first pass;
- the admitted full replay has 16 launch-time producer activations and 15
  completion-time deaths; PRE never scans or drops and POST is the only death
  event;
- O1's whole-cache scan is explicitly `ORACLE_ZERO_COST_SCAN`;
- M1 has no tag sweep and discovers dead lines only on replacement;
- C0 metadata/control overhead is required only if M1 passes the promising
  gate; its source/config will be frozen first.
- formal B0/O1/M1 enable a matched diagnostic terminal drain that advances the
  existing GPU, cache, memory-partition and interconnect model until
  `gpgpu_sim::active()` and the independently tracked L2-writeback count are
  both zero; max-limit/deadlock and all queue gates must also close. It adds no
  port, bandwidth, capacity or faster latency and is default OFF;

## Correctness and telemetry scope

- formal regions are exactly 128-byte aligned; unaligned/partial-line
  descriptors are rejected by strict admission and are unsupported in V1;
- a dirty line classified live when evicted is latched non-dead and cannot be
  retroactively cancelled after a later POST death; source plus directed test 2
  establish this because there is no dedicated live-dirty counter;
- dead-victim selections include clean lines, while dirty-drop lines/bytes are
  the actual modified subset;
- forced-live eviction includes clean and dirty cases, and fallback is
  incremented by the same branch. Their equality proves internal accounting,
  not two independent liveness observations;
- `protected_victim_deflections` is observational and may overcount when an
  invalid way coexists with a valid baseline candidate. It is reported but not
  used as exact causal evidence or a decision gate;
- M1 versus B0 is the combined response of live-line priority and lazy
  dead-dirty drop. Drop bytes cannot be added directly to traffic savings
  because replacement changes later residency.

No claim is made that this metadata fits a real RTX4080 timing/area budget.

## Formal response

M1 drops 2,173,674 dirty dead-line transactions / 278,230,272 bytes and
reduces L2/DRAM writeback from 323,967,936 to 25,630,144 bytes (92.0887%).
It reduces modeled DRAM reads by 70.9360% and L2 misses by 19.3871%, while
all coverage, writeback completion and terminal gates pass.

Cycles improve from 15,374,861 to 15,297,575 (0.5027%), below the
preregistered 5% promising gate. The final outcome is
`R101_TRANSIENT_L2_TRAFFIC_RESPONSE_NO_CYCLE_GAIN`; C0 is not triggered.
