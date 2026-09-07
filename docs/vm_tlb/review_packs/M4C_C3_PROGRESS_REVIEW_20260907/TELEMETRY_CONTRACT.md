# Frozen telemetry interpretation

The formal replay uses `M4C_MEMORY_TELEMETRY_V1` at telemetry level 2 with a
bounded window parameter of `1000000`.  Formal runs do not emit unbounded
per-access logs.

`FIXED_WINDOW` is formally named **`L1D_ACCESS_ATTEMPT_WINDOW`**: it advances
from `record_l1()`.  It is not an exact unique/coalesced-transaction window,
and must not be used to calculate exact transactions per memory instruction.
Existing per-kernel frontend transaction/instruction metrics retain their
existing definitions.

Native global DRAM channel, bank, read/write, latency, and row-locality
statistics are **EXISTING_REUSED**.  Object-specific Weight/KV/PTE attribution
by channel, bank, or row is **NOT_AVAILABLE**.  C4 must export the native
global statistics from existing `run.log` files without requesting replay;
offline immutable-trace analysis supplies locality and footprint metrics.
