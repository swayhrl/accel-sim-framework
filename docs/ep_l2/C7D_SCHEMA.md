# C7d EPL2B0V1 telemetry contract

C7d extends `EPL2B0V1`; it does not redefine any pre-existing field. Existing
`block_descriptor`, `block_wad`, `block_payload`, and `block_lower` remain
coarse compatibility observations and are not used as a specific-resource
synonym by the C7d analyzer.

## Exact admission fields

| Field | Producer meaning |
| --- | --- |
| `c7d_line_alloc_eligible` | Preview selected a line allocation attempt. |
| `c7d_line_alloc_block` | Exact all-reserved/set-allocation denial. |
| `c7d_tag_set_all_reserved_block` | Explicit subset of the preceding field. |
| `c7d_line_mshr_alloc_eligible`, `c7d_line_mshr_full_block` | Descriptor-aware preview's exact line-MSHR condition. |
| `c7d_descriptor_alloc_eligible`, `c7d_descriptor_pool_full_block` | Exact shared descriptor-pool condition. |
| `c7d_per_address_cap_eligible`, `c7d_per_address_cap_block` | Exact per-address descriptor-cap condition. |

## WAD and payload fields

`c7d_wad_full_events`, `c7d_wad_hazard_events`, and
`c7d_wad_hazard_wait_cycles` come from the actual preview conditions that
suppress a request before destructive eviction or same-address reuse.
`c7d_wad_lifetime_*` measures completed writeback ownership lifetimes.

`c7d_payload_service_port_denial` is a service-port denial, not a capacity
denial. `c7d_payload_capacity_allocation_denial` is separate and remains zero
for the static B0 mapping unless an actual capacity allocator denies ownership.
`c7d_resident_valid_*` includes VALID and DIRTY lines;
`c7d_resident_dirty_*` is the DIRTY subset; and
`c7d_resident_pending_sector_*` counts outstanding sector bits.

## C6c bank fields

`bank_logical_ops`, `bank_attempts`, `bank_grants`, `bank_retry_attempts`,
`bank_true_conflict_ops`, `bank_true_conflict_events`, and
`bank_wait_cycles` retain C6c semantics. The primary rate is
`bank_true_conflict_ops / bank_logical_ops`, not `bank_conflicts / attempts`.
C7d adds `c7d_bank{0..3}_*` per-bank fields and operation-class counters.

For `scope=kernel`, bank fields are launch-to-completion deltas. For
`scope=application`, they are application cumulative values. An overlapped
kernel record is a shared-resource interval delta, not disjoint attribution.

## Availability discipline

`parse_epl2_b0.py` preserves producer fields. `analyze_target_baseline.py`
emits `NOT_EMITTED_BY_EPL2B0V1` when the producer did not measure a requested
quantity; it never infers semantics from an unrelated coarse field.
