# Incremental TVD metadata cost

No new payload data array and no new allocator. Directory capacity <=128; integration REUSES existing WAD addresses, not a second 128-address CAM. Data budget is Lane 1's 1168/1160 slots; standalone tests still use the historical 1152-slot arbiter and are not B16/U_WB experiments.

Per existing directory entry, account separately: payload pointer 11 bits; payload generation Gp; 3 state bits; 4 valid-sector bits; 4 dirty-sector bits; reader count R; replacement age A; stale directory-ticket generation Gd if not reusable from existing state. Incremental bound: `128 * (22 + Gp + R + A + Gd)` bits, minus explicitly reused existing fields. Gp/Gd/A/R are unresolved physical-width parameters, not C++ sizes.

Read lease sidecar in the existing request/descriptor carries slot index7, Gd, payload ID11+Gp, sector mask4, forwarding1, active1: `24 + Gd + Gp` bits/live lease. Charge actual bounded response/descriptor capacity; this module allocates no second descriptor pool.

Software timestamps, counters and exact LRU ages are instrumentation/control prototypes, not synthesized SRAM area. Lookup costs one extra cycle after tag miss. TVD reads use the same bank arbiter. Promotion copies zero data but can cause a separately charged dirty victim WB. Dirty after-lower-accept retention slot-cycles are distinct from WB staging slot-cycles; no negative storage credit is claimed.
