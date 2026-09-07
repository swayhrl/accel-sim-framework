# B9 final report

**B9_FINAL_STATUS: `EXECUTION_PACK_READY_AFTER_A_TERMINAL`**
**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

B9 is ready as a future execution package, not as permission to run it. The
ready determination is static: B simulator SHA-256 matches the frozen value,
all E01--E06 target configuration stacks parse to their required control
values, every planned delta is whitelisted, required telemetry exists in the
frozen B source/export path, and shell/Python/dry-run checks pass.

The package freezes 16 future jobs: 12 E01--E06 simulator smoke arms, E07/E08
single-worker RSS calibrations, and E09/E10 sequential 16-kernel streaming
mining arms. The helper defaults to no execution and requires explicit
`--enable-execution`, external A-terminal attestation, pre-job resource gate,
correct binary hash, fresh arm outputs, and per-arm continuation. It cannot
overwrite B1--B8 evidence. E09/E10 additionally require their E07/E08 partial
artifact and calibrated peak/span values.

A's committed checkpoint changes observation requirements, not B performance
expectations: a decode paper arm had fewer TLB misses yet more cycles than A
generic. Thus every E01--E06 arm records cycles/IPC plus L1/L2 TLB, MSHR,
PWQ, walker, PWC, PTE request/response/DRAM/wait, object attribution, and
realized controls. Missing telemetry is `NOT_AVAILABLE`, never zero.

No E01--E10 experiment, simulator, B worker, trace generation, rebuild, or
full ROI scan was started. Window A/C private resources were not accessed or
changed. Window A evidence was read only from the supplied committed object.
All outputs remain `SPECULATIVE_DIAGNOSTIC`; future results remain bounded to
their exact ROI, kernel, binary, config, and provenance gates.
