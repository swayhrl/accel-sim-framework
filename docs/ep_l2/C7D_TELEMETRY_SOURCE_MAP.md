# C7d telemetry source map

| Analysis resource | Exact producer source | Notes |
| --- | --- | --- |
| Tag/set reservation | `l2_cache::preview_access()` and `memory_sub_partition::cache_cycle()` | `RESERVATION_FAIL` caused by tag replacement is separate from WAD conditions. `l2_char_storage_snapshot()` samples reserved lines and per-set maximum. |
| Line MSHR, descriptor pool, per-address cap | `mshr_table::full_reason()` carried in `l2_access_plan` | The three `EP_L2_BLOCK_*` reasons are emitted independently. |
| Descriptor chain depth | `mshr_table::descriptor_chain_snapshot()` | Fixed-buffer histogram, average/p95/max sampled from actual live target lists; not inferred from descriptor occupancy. |
| WAD | `l2_cache::preview_access()`, ownership set, `memory_sub_partition::set_done()` | Full/hazard events use real admission conditions; lifetime ends only at real writeback completion. |
| Payload roles | `ep_l2_payload_store` slot state | Live/VALID/DIRTY/pending-sector/bypass state is sampled at cache-cycle boundary. |
| C6c banks | `ep_l2_payload_store::request()` | C6c logical/attempt/grant/retry/true-conflict/wait counters are preserved; C7d adds per-bank and operation class. |
| Kernel bank deltas | `memory_sub_partition::begin/end_ep_l2_b0_kernel()` | Bank snapshot at kernel start is subtracted at completion. |
| MissQ/L2-to-DRAM | `memory_sub_partition` queues and admission inputs | Occupancy is sampled; exact local full admissions have dedicated C7d fields. |
| L1 | Native cache statistics in shader/cache path | `block_l1` stays coarse; no target-specific eligible/blocking aggregation is claimed. |
| DRAM scheduler/return path | `memory_partition_unit::dram_cycle()` and native `dram_t` | C7d records real issue eligibility, read/write issue, scheduler-full, ReturnQ/credit denial, DRAM-to-L2 full, and scheduler occupancy sampled at each eligible issue. `block_lower` is never reinterpreted as scheduler blocking. |

This map is deliberately conservative: unconnected telemetry is reported as
unavailable rather than guessed. None of these observations participates in
admission, queueing, arbitration, or cache state transitions.
