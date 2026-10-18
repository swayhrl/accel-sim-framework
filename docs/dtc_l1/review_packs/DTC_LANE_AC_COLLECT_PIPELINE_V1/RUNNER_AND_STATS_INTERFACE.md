# Runner and normal statistics interface V1

No workload runner or old lock is invoked. This pack provides CPU component
qualification and an immutable handoff for independent Lane AG. It does not
authorize a full, canary, native or GPU run, or restore any historical launch.

ON: `-gpgpu_dtc_l1_mode 3 -gpgpu_dtc_l1_finite_service 1
-gpgpu_dtc_l1_collect_wb_pipeline 1`. Omitted/0 selects the original serial path.
K1 remains independently selectable; no performance outcome controls the switch.
No Tag/physical/PIB/clock/request/quota or runtime_stat/debuglimit option is retuned.

Normal `gpu_print_stat()->shader_print_dtc_l1_stats()` delegates through const
cluster/core/LDST methods to print one additional ON-only framed section:

```
DTC_COLLECT_WB_V1_SNAPSHOT_BEGIN version=1 sms=64 cycle=C
DTC_COLLECT_WB_V1_SUMMARY sm=0 ...
...
DTC_COLLECT_WB_V1_SUMMARY sm=63 ...
DTC_COLLECT_WB_V1_SNAPSHOT_END version=1 sms=64 cycle=C
```

Every configured SM prints exactly once, including inactive SMs. Rows are
lifetime-cumulative snapshots; select the last whole complete population,
never add snapshots. The original K1 section and all old public formats/meanings
are untouched. OFF absence is UNAVAILABLE, not an invented measured zero.

Units and sampling are per SM, absolute core cycle, at the first LDST writeback
invocation after WB arbitration and before/after the collection step. `samples`
counts unique collection-stage edges actually invoked; it is not automatically
a full-workload denominator. `first_cycle/last_cycle` use UINT64_MAX when no edge
was sampled. C is the original global_cycle getter, not a new stage clock.

- `eligible_ready_sum`: candidate-count sum at the post-WB/pre-collection scan;
  cacheable, fully admitted, data-ready, no older same-warp fence. Includes existing
  data-stage owners. `eligible_ready_cycles`: edges with at least one.
- `collect_idle_eligible_cycles`: no sector read despite an eligible candidate
  with remaining sectors and cycle>ready_cycle. Includes genuine two-bank
  backpressure; does not count the mandatory ready-cycle delay as an opportunity.
- `overlap_cycles`: same absolute cycle has a successful cacheable WB retirement
  AND at least one sector read, from distinct owners. Sidecar retirement is excluded.
- `result_occupancy_samples`, `collecting_occupancy_samples`: post-collection
  boolean occupancy integrals in sampled edges. Means divide by `samples`, only
  for this explicit denominator. `result_backpressure_cycles`: completed collector
  holding behind an occupied result at that sampling edge.
- `wb_arbitration_blocked_cycles`: result already old enough for WB, but no RFU
  attempt by the first collection sampling edge; this is a first-microstep witness,
  not a claim that later LDST microsteps cannot grant the WB.
- `wb_attempts/wb_denied_attempts`: actual pipeline RFU calls and denied calls;
  at most one attempt per absolute cycle. Successes=cacheable_retires.
- `collected_sectors`: count of original32B port grants. Multiply by32 for raw
  data-read bytes, including unused bytes. `retires/cacheable_retires/sidecar_retires`
  count original successful PIB retirements, not lanes or memory transactions.
- `sector_cycles_0..4`: exact per-absolute-cycle sector-consumption histogram.
  `retire_cycles_0..1`: exact retirement histogram. A WB grant on a later LDST
  invocation of the same absolute cycle updates its already-sampled bin; it does
  not add a second sample. Weighted bins equal total sectors/retirements.
- `last_cycle_sectors/retires`: most recently sampled absolute cycle, including
  later WB microsteps. Limits4/1. No per-cycle unbounded log is introduced.
- valid/UID fields describe current two stage owners. `buffered_sectors` and
  peak count retained raw sectors, not PIB entries. Capacity fields are bytes.

`scripts/parse_collect_wb.py` rejects missing/duplicate/truncated/unframed rows,
wrong versions, malformed or excessive fields, clock/sentinel mismatches, quota,
flow, histogram, owner or finite-capacity inconsistencies. It selects the last
whole frame and refuses a truncated final frame even after earlier valid ones.
Terminal use additionally requires both stages drained. This is a telemetry
section checker, not a full workload normal-terminal/ISA/conservation validator.
A future authorized runner must bind exact Core/config/ELF/library/parser/input
identities and full normal terminal evidence before interpretation.
