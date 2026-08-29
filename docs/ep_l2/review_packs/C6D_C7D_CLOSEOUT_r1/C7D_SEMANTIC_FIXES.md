# C7d semantic ambiguity fixes

The existing compatibility counters remain emitted with their historical,
coarse meanings. C7d does not silently rename them in parser or analyzer.

| Invalid old interpretation | Exact replacement field(s) | Production source |
| --- | --- | --- |
| `block_descriptor == descriptor_pool_full` | `c7d_descriptor_pool_full_block`; separately `c7d_line_mshr_full_block` and `c7d_per_address_cap_block` | `mshr_table::full_reason()` -> `l2_access_plan` -> `memory_sub_partition::cache_cycle()` |
| `block_wad == WAD_full` | `c7d_wad_full_events`; separately `c7d_wad_hazard_events` and `c7d_wad_hazard_wait_cycles` | `l2_cache::preview_access()` and WAD ownership completion in `memory_sub_partition::set_done()` |
| `block_lower == scheduler_block` | `c7d_dram_scheduler_full_block`; separately issue/credit/ReturnQ/DRAM-to-L2 fields and scheduler occupancy | `memory_partition_unit::dram_cycle()` |
| `payload_block == payload_capacity_block` | `c7d_payload_service_port_denial` and `c7d_payload_capacity_allocation_denial` | `ep_l2_payload_store` state and L2 request/return paths |

The primary C6d/C7d bank conflict rate is exactly:

`bank_true_conflict_ops / bank_logical_ops`

It is not `bank_conflicts / bank_attempts`; that older ratio included the
pre-fix mandatory staging/retry bookkeeping.
