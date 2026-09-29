# Source path map

This audit binds the accepted R101R3 Core source before any R101R4 long run.

| Boundary | Exact source anchor | Preserved behavior / R101R4 relevance |
| --- | --- | --- |
| Coalescing and access creation | `warp_inst_t::generate_mem_accesses`, `warp_inst_t::memory_coalescing_arch`, `memory_coalescing_arch_reduce_and_send` in `src/abstract_hardware_model.cc` | Produces the original coalesced `mem_access_t` and access queue. |
| Translation completion | `ldst_unit::memory_cycle` in `src/gpgpu-sim/shader.cc` | The head access remains pending until accepted VM translation returns READY; SimVA and SimPA remain distinct fields. |
| O2 / P0 placement | `ldst_unit::awma_pre_l1_try_admit`, called by `ldst_unit::memory_cycle` after translation/frontend observation and before `bypassL1D` / `process_memory_access_queue_l1cache` | P0 uses exactly the accepted O2 scientific placement. |
| L1 admission | `ldst_unit::process_memory_access_queue_l1cache` | Allocates the original `mem_fetch`, records coverage/provenance and enters the configured banked L1-latency queue. |
| L1 lookup/outcome | `ldst_unit::L1_latency_queue_cycle` -> `l1_cache::access` -> `data_cache::access` / `process_tag_probe` | Retains tag lookup, port use, HIT, MISS, HIT_RESERVED and RESERVATION_FAIL behavior. |
| L1 MSHR/reservation/merge | `data_cache::rd_miss_base` -> `baseline_cache::send_read_request` | Performs line reservation/replacement, MSHR allocation or merge and miss-queue insertion. |
| Lower-request dequeue | `baseline_cache::cycle`, gated by `m_level == L1_GPU_CACHE` | Waits for the finite L1D miss queue and calls the configured `mem_fetch_interface`; this is the legal P1 interception boundary after L1 miss state exists. Other cache instances remain baseline. |
| Request ICNT injection | `shader_memory_interface::full/push` -> `simt_core_cluster::icnt_inject_request_packet` | Normal lower-level requests enter the request interconnect here. |
| L2 partition ingress | `memory_sub_partition::push` in `l2cache.cc` | Performs ROP delay and insertion into the finite `m_icnt_L2_queue`. |
| L2 service | `memory_sub_partition::cache_cycle` -> `l2_cache::access` / DRAM queues | Normal L2 tags/data, MSHR, miss/writeback and finite partition queues. |
| Return ICNT | `simt_core_cluster::icnt_cycle` | Pops the network reply into the finite cluster response FIFO, then calls `shader_core_ctx::accept_ldst_unit_response`. |
| LD/ST response FIFO | `ldst_unit::fill`, then `ldst_unit::cycle` | Uses the existing finite LD/ST response FIFO. |
| L1 miss completion/fill | `ldst_unit::cycle` -> `m_L1D->fill` -> `baseline_cache::fill` | Restores original address/size, fills L1, marks the MSHR ready and consumes the normal L1 fill port. |
| Merged-read retirement | `m_L1D->access_ready/next_access` in writeback client 4 | Releases each MSHR waiter through the normal LD/ST writeback arbiter. |
| Bypass/global return | `m_next_global` in writeback client 3 | Normal bypass requests and O2/P0 loads reuse client 3 arbitration. |
| LDG completion | `ldst_unit::writeback` | Decrements pending writes and releases the scoreboard register exactly once. |
| LDGSTS completion | `ldst_unit::writeback` and `shader_core_ctx::unset_depbar` | Preserves pending-LDGSTS and DEPBAR release. |
| Store completion | WRITE_ACK handling in `ldst_unit::cycle` and `shader_core_ctx::store_ack` | Preserves sector ACK/token accounting. |

## P1 feasibility finding

A legal P1 can be placed at the L1 cache's lower-level `mem_fetch_interface`:
the miss has already allocated/merged normal L1 state, but the miss queue has
not yet injected the request into ICNT. A P1 wrapper can backpressure
`baseline_cache::cycle`, locally schedule the original `mem_fetch`, call
`set_reply`, and re-enter `ldst_unit::fill`. That route executes the
unchanged `m_L1D->fill` / MSHR-ready / client-4 completion path.

Therefore P1 is source-feasible if P0 survives; there is no need to pretend a
miss was an L1 hit. No P1 code or run is authorized before the P0 gate.
