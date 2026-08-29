# C7e telemetry source map

| Resource | Exact producer | Output schema / fields | Notes |
|---|---|---|---|
| L1D | `src/gpgpu-sim/shader.cc`, `gpu-sim.cc` | `EPL2L1V1`: accesses, misses, line alloc, MissQ, MSHR entry/merge/RW-pending, bank/latency conflict | L1D only; app cumulative and kernel interval deltas |
| Tag way | `src/gpgpu-sim/l2cache.cc:memory_sub_partition::cache_cycle` | `c7e_tag_way_alloc_need`, `c7e_tag_way_alloc_block` | Need counts only new-line sector misses; no generic reservation inference |
| Line MSHR | same preview path + production counters | `c7e_line_mshr_need`, `c7d_line_mshr_full_block` | Independent demand denominator |
| Descriptor / cap | same preview path + production counters | `c7e_descriptor_need`, `c7d_descriptor_pool_full_block`, `c7e_per_address_cap_check`, `c7d_per_address_cap_block` | Independent full/cap demand denominators |
| WAD | production WAD lifecycle in `gpu-cache.cc`, exported in `l2cache.cc` | `c7d_wad_*` | Kernel WAD lifetime is explicitly unavailable rather than re-labeled cumulative data |
| Payload | production payload store sampling | `c7d_resident_*`, `c7d_bypass_*`, service-port and capacity denial fields | Port denial remains distinct from capacity denial |
| Bank | C6d payload arbitration | `bank_logical_ops`, attempts, grants, retry, true conflicts/events, waits; per-bank and op-class fields | True conflict denominator is logical ops |
| MissQ / L2→DRAM | `l2cache.cc` production queue decisions | `c7d_missq_full_block`, `c7d_l2_to_dram_full_block` | Not mapped to a generic lower cause |
| DRAM issue | real L2→DRAM pop/accept points | `c7e_dram_issue_attempt`, successful read/write issue/bytes | Attempts and successful issues are separate |
| DRAM channel | `memory_partition_unit::dram_cycle` | `EPL2DRAMV1` application + `interval=5000_cycle` windows | Scheduler and ReturnQ occupancy/full are time-weighted per channel |
| DRAM return path | real return dequeue path | `c7e_dram_to_l2_return_path_block` | Separate from internal ReturnQ occupancy/full |

Parser: `util/ep_l2/parse_epl2_b0.py`.  It retains the terminal record for
each cumulative L1D application producer and DRAM channel, while preserving
kernel and 5K interval records.  Analyzer:
`util/ep_l2/analyze_target_baseline.py`.
