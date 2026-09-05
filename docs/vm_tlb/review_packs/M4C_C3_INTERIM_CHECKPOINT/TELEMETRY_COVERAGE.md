# Telemetry coverage

`IMPLEMENTED`: translation L1/L2, MSHR/PWQ/walker/PWC/PTE/latency/object and L2-TLB victim matrix; L1D access/hit/miss/sector/MSHR/reservation/bytes/object; L2 data/PTE/object access/pressure/replacement/L2→DRAM; bounded ROI/per-kernel/window records.

`EXISTING_REUSED`: native cache/DRAM/interconnect/queue stats where exposed. `OFFLINE_DERIVED`: immutable trace lines/sectors/pages/footprint/hotness/cross-kernel overlap. `NOT_AVAILABLE`: exact L1 victim and lost-identity per-object DRAM/channel/bank/row data. `NOT_YET_VALIDATED`: full-formal exports until C3 completes. No checkpoint telemetry change is made.
