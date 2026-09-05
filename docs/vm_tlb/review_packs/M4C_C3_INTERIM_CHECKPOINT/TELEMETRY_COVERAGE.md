# Telemetry coverage

`IMPLEMENTED`: translation L1/L2, MSHR/PWQ/walker/PWC/PTE/latency/object and L2-TLB victim matrix; L1D access/hit/miss/sector/MSHR/reservation/bytes/object; L2 data/PTE/object access/pressure/replacement/L2→DRAM; bounded ROI/per-kernel/window records.

`EXISTING_REUSED`: native global DRAM read/write, latency, channel/bank distribution, row-locality, cache, interconnect and queue stats where exposed. `OFFLINE_DERIVED`: immutable trace lines/sectors/pages/footprint/hotness/cross-kernel overlap. `NOT_AVAILABLE`: exact L1 victim and object-specific Weight/KV/PTE × channel/bank/row attribution after identity is lost. `NOT_YET_VALIDATED`: full-formal exports until C3 completes. No checkpoint telemetry change is made.
