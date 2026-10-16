# Producer source map

All paths in swayhrl/gpgpu-sim at c197c14d8292e8c2aa522711f4125ed5624b5549, consumed base 126394be46b15f55b9756d43eb9ca9a9baae1c84.

| Path | Actual responsibility |
|---|---|
| src/gpgpu-sim/ep-l2-tvd-cache.inc | tvd_install_victim, reclaim_one, frontend, response_commit, promote, epoch_cleanup, summary; uses R0 preview_free/reserve/release/transfer/pin/unpin/request/inspect/handle_live |
| src/gpgpu-sim/ep-l2-tvd-directory.h | sole combined metadata authority, state table, preview/commit revision, lease, WB transitions, sector mask checks; no allocator |
| src/gpgpu-sim/ep-l2-ft-cache.inc | real replacement retention and rollback, mandatory reservations, actual lower_accepted hook, role transfer, actual lower packet/byte counters, TVD summary appended to FT output |
| src/gpgpu-sim/gpu-cache.cc | includes production implementation, routes promotion before ordinary FT access, set_done/allocator/directory transition |
| src/gpgpu-sim/gpu-cache.h | defaultOFF flags/mode checks, sole allocator TVD role/state, total ownership, Tag tvd_bind, WAD queries, epoch cleanup; no second descriptor pool |
| src/gpgpu-sim/l2cache.cc | cache_cycle frontend before generic WAD, actual queue space/bank service; admission and response audit, queue push then response_commit |
| src/gpgpu-sim/l2cache.h | narrow cache pointer accessor for actual production fixture |
| src/gpgpu-sim/gpu-sim.cc | new defaultOFF config switches |
| tests/ep_l2/test_tvd_production.cc | actual memory partition, subpartition, mem_fetch, queue, simpleDRAM producers and independent UID/sector-version reference |
| CMakeLists.txt | excluded-by-default production fixture linked to same simulator libraries |

No whole historical feature branch is required for integration: the 10-file minimal patch applies to exact R0 and its resulting blobs were compared to the frozen producer commit. The old independent-directory fixture/runner are intentionally omitted from that patch; its previous seven groups were not rerun this round.
