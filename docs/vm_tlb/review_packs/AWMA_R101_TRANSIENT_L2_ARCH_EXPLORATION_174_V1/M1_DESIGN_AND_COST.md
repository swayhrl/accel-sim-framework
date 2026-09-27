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
- O1's whole-cache scan is explicitly `ORACLE_ZERO_COST_SCAN`;
- M1 has no tag sweep and discovers dead lines only on replacement;
- C0 metadata/control overhead is required only if M1 passes the promising
  gate; its source/config will be frozen first.

No claim is made that this metadata fits a real RTX4080 timing/area budget.
