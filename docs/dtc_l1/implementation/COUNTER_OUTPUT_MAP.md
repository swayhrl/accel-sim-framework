# DTC-L1 counter and output map

Status: `M3_OO_SECTOR_CLOSEOUT`. This map distinguishes emitted Core text
counters from later M4 workload-result outputs.

## Current Paper Base emission

When `-gpgpu_dtc_l1_mode 1` is active, the Core aggregates SM-local frontend
state in `gpgpu_sim::shader_print_dtc_l1_stats` and emits:

| Key | Meaning |
| --- | --- |
| `DTC_L1_mode` | selected Paper Base mode marker |
| `DTC_L1_pib_admits`, `DTC_L1_pib_retires`, `DTC_L1_pib_occupancy`, `DTC_L1_pib_peak_per_sm` | PIB accounting and occupancy |
| `DTC_L1_pib_full_events` | denied first-admission attempts due to full PIB |
| `DTC_L1_primary_stall_pib_full`, `DTC_L1_primary_stall_tag_bank`, `DTC_L1_primary_stall_lower_cap`, `DTC_L1_frontend_stall_cycles` | mutually exclusive primary-stall accounting for the defined Paper Base admission/Tag/lower-token domain; priority is PIB admission, then Tag arbitration, then lower-token retry at its source-backed L1 new-miss decision point |
| `DTC_L1_nonexclusive_pib_full_cycles`, `DTC_L1_nonexclusive_tag_bank_conflict_cycles`, `DTC_L1_nonexclusive_lower_cap_full_cycles` | independent resource-unavailable samples for the same three resources; M1 happens to observe each at its sole primary sampling point, while later modes may overlap them |
| `DTC_L1_baseline_mshr_entry_full_events`, `DTC_L1_baseline_mshr_merge_full_events`, `DTC_L1_nonexclusive_mshr_entry_full_cycles`, `DTC_L1_nonexclusive_mshr_merge_full_cycles` | conventional L1D MSHR retry observations, aggregated directly from L1D `cache_stats`; exposed independently and intentionally outside the Paper Base frontend primary domain because the retry occurs after admission/Tag timing in `L1_latency_queue_cycle` |
| `DTC_L1_pib_occupancy_cycle_sum`, `DTC_L1_pib_occupancy_sample_cycles` | average-occupancy numerator/denominator |
| `DTC_L1_tag_requests`, `DTC_L1_tag_conflicts` | Tag work and arbitration blocks |
| `DTC_L1_tag_bank_<N>_requests` | per-Tag-bank service totals |
| `DTC_L1_baseline_mshr_entries` | effective Paper Base traditional-L1 MSHR capacity |
| `DTC_L1_lower_outstanding_cap`, `DTC_L1_lower_outstanding`, `DTC_L1_lower_outstanding_peak` | global bounded lower-request token state |
| `DTC_L1_lower_cap_full_events`, `DTC_L1_lower_requests_acquired`, `DTC_L1_lower_requests_released` | lower-cap blocking and token closure evidence |

The Core asserts `admits - retires == live_pib_entries` and
`live_pib_entries <= configured_pib_entries` on modeled LD/ST cycles.

## Machine-readable summary parser

`util/dtc_l1/parse_dtc_l1_summary.py` converts a simulator log to the stable
`dtc_l1_summary_v1` JSON shape. In `--strict` mode it requires dynamic
instruction/cycle fields, configuration/workload files for SHA256 provenance,
and the required Paper Base closure fields whenever `DTC_L1_mode=PAPER_BASE`.
The parser records a caller-supplied result classification; it does not infer
scientific validity from a successful process exit.

## Current Paper IO emission

When `-gpgpu_dtc_l1_mode 2` is active, the Core emits the following compact
whole-line IO ownership and resource evidence in addition to the common lower
credit fields:

| Key family | Meaning |
| --- | --- |
| `DTC_L1_io_lower_{created,issued,responses}`, `DTC_L1_io_inflight_*`, `DTC_L1_io_responses_routed_*` | DTC-owned lower request lifecycle, immutable response routing, and drain closure |
| `DTC_L1_io_pib_*`, `DTC_L1_io_retire_count`, `DTC_L1_io_completion_dependency_*`, `DTC_L1_io_ready_but_writeback_blocked_cycles` | IO FIFO occupancy, finite writeback retirement, and dependency cardinality closure |
| `DTC_L1_io_{valid,pending}_hits`, `DTC_L1_io_physical_{allocations,releases}`, `DTC_L1_io_tag_evictions`, `DTC_L1_io_duplicate_after_eviction` | logical/physical hit, allocation, replacement, and pending-eviction traffic accounting |
| `DTC_L1_io_{partial_allocation,allocation_width_limited,no_free_physical}_events`, `DTC_L1_io_partial_*` | partial allocation and finite-pool pressure observability |
| `DTC_L1_io_physical_{allocated,free}_*` | physical-pool current, peak, and minimum-free state (current values aggregate across SMs; extrema are per-SM extrema) |
| `DTC_L1_io_hol_ready_younger_*` | scientifically meaningful FIFO HOL condition: an unready head with one or more ready younger entries |
| `DTC_L1_conventional_l1d_mshr_{entry,merge}_full_events` | independent conventional-L1D MSHR evidence; IO read requests must not use it as their capacity or merge mechanism |

The Core asserts at kernel drain that DTC IO inflight and PIB occupancy are
zero, created/issued/responded lower requests close, completion dependencies
close, and global lower credits return to zero.

The strict summary parser recognizes `PAPER_IO` and requires the essential IO
lower/PIB/dependency/credit closure fields before writing a provenance-bearing
summary.

## Current Paper OO emission

When `-gpgpu_dtc_l1_mode 3` is active, the Core emits:

| Key family | Meaning |
| --- | --- |
| `DTC_L1_oo_lower_{created,issued,responses}`, `DTC_L1_oo_inflight_current` | whole-line lower-request lifecycle and drain closure |
| `DTC_L1_oo_pib_occupancy`, `DTC_L1_oo_retire_count`, `DTC_L1_oo_out_of_order_retires` | random-access PIB and deterministic oldest-ready retirement evidence |
| `DTC_L1_oo_completion_dependency_{count,closed}`, `DTC_L1_oo_active_refs` | unique-128B dependency and Ref Count closure |

The strict parser recognizes `PAPER_OO` and requires lower/PIB/dependency/Ref
and lower-credit closure fields.

## Current modern OO-sector diagnostic emission

When `-gpgpu_dtc_l1_mode 4` is active, the Core emits:

| Key family | Meaning |
| --- | --- |
| `DTC_L1_sector_lower_{created,issued,responses}`, `DTC_L1_sector_inflight_current` | 32B single-sector lower-read lifecycle and drain closure |
| `DTC_L1_sector_{new_line_misses,new_requests,valid_hits,pending_hits}` | 128B physical allocation versus exact 32B readiness/request behavior |
| `DTC_L1_sector_fill_wakeups`, `DTC_L1_sector_completion_dependency_{count,closed}`, `DTC_L1_sector_active_refs` | per-sector wakeup, line-level completion cardinality, and Ref Count closure |
| `DTC_L1_sector_pib_occupancy`, `DTC_L1_sector_retire_count`, `DTC_L1_sector_out_of_order_retires` | random-access PIB lifecycle for sector diagnostic mode |

The strict parser recognizes `MODERN_OO_SECTOR` and requires all lower/PIB,
sector-request/wakeup, dependency/Ref, and lower-credit closure fields. This
is diagnostic implementation evidence, not M5 performance interpretation.

## Deferred beyond M3

The full M4 operation-semantic workload suite and all M5 performance claims
remain deferred. No CSV artifact is claimed until an actual parser and
provenance-checked simulator run produces it.
