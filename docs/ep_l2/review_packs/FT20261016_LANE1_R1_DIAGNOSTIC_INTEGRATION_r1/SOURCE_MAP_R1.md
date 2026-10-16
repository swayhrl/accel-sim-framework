# R1 source map

Core be651ccfe7bd47c0bbd8c30fe6439ae3b60cf8de; producing Framework fb64d9520f20a562cc0db78b838d13f4599b49ce.

- gpu-sim.cc: three default-OFF ideal CLI registrations.
- gpu-cache.h/.cc: diagnostic WB-only extra backing through the sole bank arbiter; dynamically grown descriptor/Line-MSHR capacity; ordinary sector/order/response paths retained.
- ep-l2-ideal-reference.h and l2cache.h/.cc: diagnostic known-byte/opaque-version reference, older producer checks, actual hit delay/bank/L2-to-ICNT response and cleanup.
- ep-l2-ft-cache.inc, mem_fetch and all ordinary primary budgets remain byte-identical to R0.
- CMakeLists.txt: four explicit EXCLUDE_FROM_ALL producer validation targets.
- tests/ep_l2/ft20261016/r1: three-bit-only diagnostic overlays matching Lane 4 source. No new simulator runtime change in Framework.

STORAGE_AND_PORT_LEDGER.md from frozen R0 remains valid for R1 all-ideal-OFF. Enabled ideals explicitly relax declared resources and cannot enter implementation PPA/performance tables.
