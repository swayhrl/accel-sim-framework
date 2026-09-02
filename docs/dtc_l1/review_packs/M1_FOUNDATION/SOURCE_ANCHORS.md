# Source anchors

M1.0 navigation is in `../../implementation/SOURCE_INTEGRATION_MAP.md`.

The B07 defect was in Core `src/gpgpu-sim/shader.cc`,
`ldst_unit::L1_latency_queue_cycle()`: the true L1-hit completion path called
`warp_inst_complete()` without retiring the Paper Base PIB UID. Core commit
`06aa534a` pairs it with idempotent `dtc_l1_retire()`. Final drain asserts are
in `gpgpu_sim::shader_print_dtc_l1_stats()`.

M1 resource sources are:

- PIB/Tag model: `src/gpgpu-sim/dtc-l1-common.h`;
- L1 entry and Tag timing hook: `ldst_unit::process_memory_access_queue_l1cache()`;
- conventional MSHR source behavior: `baseline_cache::send_read_request()`;
- lower token acquire/release: `gpgpu_sim::{dtc_l1_try_acquire_lower_request,dtc_l1_complete_lower_request}`;
- aggregate counters: `gpgpu_sim::shader_print_dtc_l1_stats()`;
- strict summary parser: `util/dtc_l1/parse_dtc_l1_summary.py`.
