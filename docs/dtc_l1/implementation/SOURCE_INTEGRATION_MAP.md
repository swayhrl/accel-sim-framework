# DTC-L1 source integration map (M1.0)

Status: `VERIFIED_SOURCE` audit completed against the active goal worktrees on
2026-09-02.  This document is navigation and ownership evidence; it does not
change the frozen M0 architecture.

## Active source resolution

| Item | Resolved source | Evidence |
| --- | --- | --- |
| Framework | `swayhrl/accel-sim-framework:hrl/decoupled-l1-exp-m1m4-v0` at `ff26ef4642fdf10d353fb7d981b931afb25291a8` | Framework worktree `git rev-parse HEAD` before M1 review-pack closeout |
| Core | `swayhrl/gpgpu-sim:hrl/decoupled-l1-m1m4-v0` at `48b0be73833fc89fcf833349e82886ddc6d883b0` | Core worktree `git rev-parse HEAD` |
| Build selection | Framework `gpu-simulator/CMakeLists.txt` consumes `$GPGPUSIM_ROOT` as an explicit out-of-tree CMake subproject; `gpu-simulator/setup_environment.sh` clones only when that variable is absent/unusable | Framework files `gpu-simulator/CMakeLists.txt:74`, `gpu-simulator/setup_environment.sh:92-128` |

The active Framework worktree deliberately has no
`gpu-simulator/gpgpu-sim/` checkout.  All project builds/runners must therefore
export `GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-decoupled-l1-m1m4` before
running the Framework setup/build.  This makes the Core SHA above the actual
built source, rather than relying on a fresh clone or an ambient checkout.

## Existing request lifecycle

| Lifecycle point | Current owner and source-backed navigation | DTC integration role |
| --- | --- | --- |
| Dynamic memory instruction and coalescing | `warp_inst_t::generate_mem_accesses`, `memory_coalescing_arch`, and `memory_coalescing_arch_atomic` in `src/abstract_hardware_model.cc` | Preserve this coalescer.  Build DTC 128B references by grouping its existing sector accesses; do not replace coalescing. |
| Memory-pipeline entrance | `ldst_unit::issue` and `ldst_unit::cycle` in `src/gpgpu-sim/shader.cc`; dispatch invokes `memory_cycle` | Admission/backpressure point for the common Base/IO/OO lifecycle.  The modeled PIB must be after coalescing and before DTC line work. |
| L1D line access | `ldst_unit::process_memory_access_queue_l1cache`, `L1_latency_queue_cycle`, and `memory_cycle` in `src/gpgpu-sim/shader.cc` | Keep `LEGACY` on the current path.  Route enabled paper modes through a separate timing/lifecycle layer rather than changing `LEGACY` cache results. |
| Conventional tag probe and replacement | `tag_array::access`/`tag_array::fill` in `src/gpgpu-sim/gpu-cache.cc` | Paper Base keeps these semantics.  DTC needs its own logical Tag-to-physical mapping because conventional tag storage couples tag/block allocation. |
| Conventional MSHR/merge/full | `mshr_table::{probe,full,add,mark_ready,next_access}` and `baseline_cache::send_read_request` in `src/gpgpu-sim/gpu-cache.{h,cc}` | Paper Base uses this source behavior.  DTC reads must not use this table as their capacity or merge gate. |
| Lower-request queue/injection | `baseline_cache::m_miss_queue` and `baseline_cache::cycle` in `src/gpgpu-sim/gpu-cache.cc`; network injection uses `mem_fetch_interface::push` | DTC requires its own bounded request-credit/issue model before injection, while preserving lower L2/NoC/DRAM behavior. |
| Fill/response path | `shader_core_ctx::accept_ldst_unit_response` -> `ldst_unit::fill` -> `ldst_unit::cycle`; L1 fill enters `baseline_cache::fill` and MSHR completions drain via `next_access` | DTC fills must dispatch by allocation identity and wake modeled dependencies before the owning instruction can retire. |
| Dynamic completion/writeback | `ldst_unit::writeback`, `writeback_complete`, and `shader_core_ctx::warp_inst_complete` in `src/gpgpu-sim/shader.cc` | The PIB lifetime ends at this true modeled completion point, not at lower-request issue or fill arrival. |

## Identity and lifetime evidence

- `warp_inst_t::issue` assigns `m_uid` from the Core-global
  `warp_inst_sm_next_uid` (`src/abstract_hardware_model.cc`); copied
  `warp_inst_t` instances in a `mem_fetch` retain it.  Use `{sid, warp_uid}` as
  the dynamic-instruction key, retaining the existing stream/warp fields for
  diagnostics.
- `mem_fetch` assigns monotonically increasing `m_request_uid` and exposes it
  through `get_request_uid()` (`src/gpgpu-sim/mem_fetch.{h,cc}`).  It is safe
  provenance for a lower request while that request exists.
- A lower response cannot be routed only by the current logical Tag: the
  baseline fill path looks up its original `mem_fetch` object in
  `baseline_cache::m_extra_mf_fields`, but a DTC logical tag may have been
  evicted and its physical line reused.  DTC will attach an explicit immutable
  `{phys_id, generation}` allocation identity to each DTC-owned lower request
  and verify it on fill.  This is a `PROVISIONAL_MODEL` representation that
  implements the `USER_CONFIRMED` stale-fill rule without changing L2/NoC/DRAM.

## Non-load navigation for M4 audit

| Operation | Source-backed path |
| --- | --- |
| Store | `ldst_unit::memory_cycle` creates/queues accesses; `data_cache` write-policy handlers in `src/gpgpu-sim/gpu-cache.cc` issue requests; `shader_core_ctx::store_ack` consumes acknowledgements. |
| Atomic | `warp_inst_t::memory_coalescing_arch_atomic`; `mem_fetch::isatomic`/`do_atomic`; atomic state is marked in `mshr_table` and executed in the current memory/writeback flow. |
| Fence | `ldst_unit::writeback` has `WB_CLIENT_FENCE`; ordering/pending state is owned by the current core/warp pipeline. |
| Architectural L1 bypass | `ldst_unit::memory_cycle`: `CACHE_GLOBAL`, disabled L1D, or `gmem_skip_L1D` sends the existing `mem_fetch` directly to the interconnect; response handling applies the same bypass decision. |

M4 must perform its separate detailed source-backed semantics audit before it
changes any of these paths.  No M4 policy was inferred from this navigation map.

## Config, statistics, and framework plumbing

- Core options are registered in `shader_core_config::reg_options` in
  `src/gpgpu-sim/gpu-sim.cc`, including L1 geometry, bank count/latency and
  `-gpgpu_gmem_skip_L1D`.
- Standard cache statistics print through `gpgpu_sim::print_stats` and
  `gpgpu_sim::shader_print_cache_stats` in `src/gpgpu-sim/{gpu-sim,shader}.cc`.
- Framework trace/build orchestration consumes `$GPGPUSIM_ROOT` from
  `gpu-simulator/setup_environment.sh`; reusable result parsing is rooted in
  `util/job_launching/get_stats.py`.

## M1 integration decision

There is no unresolved architecture-semantic ambiguity in the M1.0 mapping.
The implementation will add a default-off project timing/lifecycle component
beside the existing L1D path, with explicit mode/configuration controls.  The
`LEGACY` path will not instantiate or consult it, which provides the required
neutrality boundary.
