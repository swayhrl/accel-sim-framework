# Lane D observer counter semantics

Status: `D3B_OCCUPANCY_EXTENSION_EQUIVALENCE_PASS`.

Every counter in this document is `NEW_DIAGNOSTIC_TELEMETRY`; every runtime
row is `POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`.  The immutable FAST64
authority remains `hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e`.

## Existing observer families

The pre-D3B families retain the exact definitions in
`OBSERVER_TELEMETRY_SPEC.md`: allocation-to-ready intervals keyed by physical
id and generation, pending Tag evictions, IO pending-eviction-to-response
intervals, OO deferred-Tag-eviction-to-final-reclaim intervals, exact OO
duplicate-after-eviction, and terminal live-record count.  The source is
unchanged for these families; D3B only extends the observer with the four
integrals below.

## D1.6 time-integrated occupancy and in-flight requests

For each active IO or whole-line OO SM cycle, the observer records:

| Exported field | Exact increment | Unit |
| --- | --- | --- |
| `DTC_L1_{io,oo}_observer_sample_sm_cycles` | `+1` | active SM cycles |
| `DTC_L1_{io,oo}_physical_allocated_line_cycles` | `+ current allocated physical lines` | physical-line·SM-cycle |
| `DTC_L1_{io,oo}_physical_full_sm_cycles` | `+1` iff allocated lines equal configured `physical_lines` | active SM cycles at full pool |
| `DTC_L1_{io,oo}_inflight_request_cycles` | `+ current DTC lower in-flight map size` | lower-request·SM-cycle |

`physical_allocated_line_cycles / observer_sample_sm_cycles` is average
allocated physical lines per sampled active SM cycle.  `physical_full_sm_cycles
/ observer_sample_sm_cycles` is the pool-full active-SM-cycle fraction.
`inflight_request_cycles / observer_sample_sm_cycles` is average DTC lower
in-flight requests per sampled active SM cycle.  A zero sample denominator is
reported as undefined; none of these ratios is a probability or a causal
estimate.

### Source location and once-per-cycle proof

`shader_core_ctx::cycle()` is the sampling hook.  Its initial inactive guard
returns before sampling.  Otherwise it invokes
`ldst_unit::sample_post_fast64_observer_cycle()` exactly once, immediately
before it increments the existing per-SM `shader_cycles` statistic and before
any writeback/execute/read-operands/issue/fetch pipeline action.

The GPU CORE-clock loop calls each cluster's `core_cycle()` once; that function
calls every `shader_core_ctx::cycle()` once.  Thus the sample count has the
same source-level active-SM-cycle eligibility as `shader_cycles`.  This is
deliberately *not* placed in `ldst_unit::cycle()`: `shader_core_ctx::execute()`
calls functional units according to `clock_multiplier()`, and
`ldst_unit::clock_multiplier()` can equal `mem_unit_ports` or
`mem_warp_parts`, which need not be one.

At the hook, IO samples `io_frontend::allocated_lines()` and
`m_dtc_l1_io_inflight.size()`; OO samples `oo_frontend::allocated_lines()` and
`m_dtc_l1_oo_inflight.size()`.  The capacity comparison uses that frontend's
fixed `m_phys.size()`, which is initialized from the configured physical-line
capacity.  The state is sampled before this SM advances its pipeline for that
cycle.  Sector OO is intentionally outside this whole-line IO/OO counter
family.

### Isolation and lifecycle

The parser option remains default-off:
`-gpgpu_dtc_l1_post_fast64_telemetry 0`.  The frontends reject sampling when
it is off, so all new fields remain zero.  The sampler performs only additions
to observer state; no sampled value is read by lookup, victim selection,
admission, allocation/free selection, retirement/reclaim, lower scheduling,
response routing, completion, assertions, or a return value used by those
paths.

Aggregation is addition across SM-local observers.  The already-qualified
terminal live-record counter continues to cover only identity records, not
the four scalar integrals.

## Implementation and directed regression

The exact observer descendants are:

| Scope | Parent | D3B observer commit |
| --- | --- | --- |
| Core95 / non-2D | `95ccdb7a056f2d53f740d90869785cac6d4ee0f5` | `2fcde3eb3fce1502cc0f910cad6f807e530018c5` |
| Core658 / 2D | `6587238c60214d99491f4048e28ce8a3458c1509` | `857671dde39b5f34ca03f2be973aae15ead5aca1` |

The focused deterministic IO and OO fixtures exercise three samples with
allocated-line sequence `0,1,2` and in-flight sequence `0,3,4`; they require
sample count `3`, allocated integral `3`, full-pool count `1`, and in-flight
integral `7`, then drain their observer identity records.  On both descendants
`dtc_l1_m1_common_test`, `dtc_l1_bad_generation_test`, and
`dtc_l1_completion_accounting_test` pass.  D3B subsequently passed exact
telemetry-off/on qualification on NN and Btree in IO and OO; its retained
records are `generated/D3B_OCCUPANCY_EXTENSION_EQUIVALENCE.tsv`,
`generated/D3B_OCCUPANCY_EXTENSION_TELEMETRY.tsv`, and
`generated/D3B_OCCUPANCY_EXTENSION_INDEX.tsv`.
