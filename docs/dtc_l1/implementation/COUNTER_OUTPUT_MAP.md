# DTC-L1 counter and output map

Status: `M1_IN_PROGRESS`.  This map distinguishes currently emitted Core text
counters from later required machine-readable outputs.

## Current Paper Base emission

When `-gpgpu_dtc_l1_mode 1` is active, the Core aggregates SM-local frontend
state in `gpgpu_sim::shader_print_dtc_l1_stats` and emits:

| Key | Meaning |
| --- | --- |
| `DTC_L1_mode` | selected Paper Base mode marker |
| `DTC_L1_pib_admits`, `DTC_L1_pib_retires`, `DTC_L1_pib_occupancy`, `DTC_L1_pib_peak_per_sm` | PIB accounting and occupancy |
| `DTC_L1_pib_full_events` | denied first-admission attempts due to full PIB |
| `DTC_L1_primary_stall_pib_full`, `DTC_L1_primary_stall_tag_bank`, `DTC_L1_primary_stall_lower_cap`, `DTC_L1_frontend_stall_cycles` | mutually exclusive primary-stall accounting for the defined DTC front-end domain |
| `DTC_L1_pib_occupancy_cycle_sum`, `DTC_L1_pib_occupancy_sample_cycles` | average-occupancy numerator/denominator |
| `DTC_L1_tag_requests`, `DTC_L1_tag_conflicts` | Tag work and arbitration blocks |
| `DTC_L1_tag_bank_<N>_requests` | per-Tag-bank service totals |
| `DTC_L1_baseline_mshr_entries` | effective Paper Base traditional-L1 MSHR capacity |
| `DTC_L1_lower_outstanding_cap`, `DTC_L1_lower_outstanding`, `DTC_L1_lower_outstanding_peak` | global bounded lower-request token state |
| `DTC_L1_lower_cap_full_events`, `DTC_L1_lower_requests_acquired`, `DTC_L1_lower_requests_released` | lower-cap blocking and token closure evidence |

The Core asserts `admits - retires == live_pib_entries` and
`live_pib_entries <= configured_pib_entries` on modeled LD/ST cycles.

## Required but not yet emitted

The M1 HARD closeout still requires the non-exclusive stall view, explicit
MSHR entry/merge accounting, parsable run summaries, and all later
physical/IO/OO/sector counters named in `COUNTER_INVARIANT_SPEC.md`.  No CSV
artifact is claimed until an actual parser and provenance-checked simulator run
produce it.
