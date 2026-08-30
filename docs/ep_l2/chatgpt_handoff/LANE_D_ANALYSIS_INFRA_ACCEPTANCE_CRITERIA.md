# EP-L2 Lane D — Analysis / Cost / Opportunity-Prep Acceptance Criteria

This is the authoritative self-gating contract for Lane D.

Lane D is primarily analysis/infrastructure. It may autonomously repair Framework analysis tooling and documentation until all mandatory gates pass. Any simulator-Core scaffold is optional, must be isolated, disabled by default, timing-neutral, and cannot be consumed by formal/calibration runs before review.

## D0. Isolation — mandatory

PASS only if:

```text
Lane D does not modify Lane A/B/C active runtime worktrees/results
analysis source lives in an isolated Framework branch/worktree
any optional Core scaffold lives in a separate branch/worktree
input data are read-only and identified by source/config manifests
```

## D1. Temporal-stream cardinality audit — mandatory first gate

Before interpreting 5K windows, prove the stream topology.

For each representative formal run report:

```text
configured L2 slice count
configured DRAM channel count
unique L2 window slice IDs
unique DRAM window channel IDs
window interval
expected row count from simulated duration/topology
actual row count
reason for any aggregation/reduction
```

PASS only if equality/differences in row counts are explained by verified producer/parser semantics.

If raw telemetry unexpectedly omits slices/channels, classify as producer defect and immediately update the workboard; do not compensate by fabricating/duplicating records.

## D2. Temporal-analysis implementation — mandatory

Produce per workload/variant and later per calibration cell:

```text
descriptor window avg/p50/p95/max
near-full descriptor-window fraction
full descriptor-window fraction
Line-MSHR window avg/p50/p95/max when emitted
L2->DRAM occupancy avg/p50/p95/max
scheduler occupancy avg/p50/p95/max
scheduler-full-active window fraction
internal ReturnQ avg/p95/max/full-active fraction
read/write bytes by window
bandwidth-util p50/p95/max
channel max/mean, coefficient-of-variation, or equivalent explicit imbalance measure
consecutive high-pressure/burst duration when robust
```

For percentile code, add small deterministic fixtures whose expected p50/p95/max values are known exactly.

Do not infer unavailable metrics; preserve explicit missing state.

## D3. Analyzer correctness — mandatory

The joint calibration analyzer must join/compare results using explicit keys including:

```text
workload
variant
source SHA
config hash
descriptor capacity
L1 config class
frequency
trace identity
```

It must reject or visibly flag incompatible provenance rather than silently merging it.

Add tests for:

```text
D256 vs D512 pairing
BASE vs META-HR vs BANK-HR pairing
missing cell
mismatched trace
mismatched source/config
measured zero vs missing field
duplicate record detection
```

## D4. Causality/calibration outputs — mandatory

As Lane A/B/C data arrive, generate comparison tables that include at least:

```text
cycles/speedup
descriptor need/block/occupancy
Line-MSHR pressure
L1 pressure
WAD pressure
bank conflict/wait
L2->DRAM/scheduler/BW
window burst/sustained/imbalance metrics
```

Do not automatically label a resource as causal from occupancy/event count alone.

The analyzer may compute screening labels but must expose the raw evidence used by the label.

## D5. Descriptor hardware-cost analysis — mandatory

Quantify the 256 -> 512 descriptor expansion as proposed hardware metadata, separately from simulator host-memory structures.

At minimum document:

```text
which fields a physical persistent descriptor needs
bits per field and assumption/source
bits/bytes per descriptor
incremental 256 extra descriptors per slice
incremental bytes per slice
incremental bytes across 64 slices
ratio vs resident payload capacity and other major metadata where meaningful
```

If field widths are not fixed by current design, provide a transparent range/sensitivity rather than inventing a single precise area number.

Do not count C++ pointers, STL/vector/map allocator overhead, debug counters, or host-only bookkeeping as physical hardware storage.

If estimating SRAM/area rather than raw bits, label modeling assumptions and technology dependency clearly.

## D6. Analysis/tool implementation verification — mandatory

For every new analysis script:

```text
unit/fixture tests PASS
real 22/26 or 26/26 data smoke PASS
schema/version check PASS
provenance mismatch detection PASS
git diff --check PASS
```

Generated outputs must be reproducible from documented command lines and input roots.

Never modify raw simulator logs to make parsing succeed.

## D7. Optional opportunity-study scaffold — strict gate

Lane D may prepare only reusable timing-neutral infrastructure such as:

```text
shadow-record interfaces
per-address observation state
kernel/epoch bookkeeping
output schema/parser stubs
```

It may not implement or claim functional:

```text
RO no-MSHR bypass
replaceable pending tags
TVD behavior
Unified borrowing
performance benefit
```

If Core code is added for scaffold:

```text
disabled by default
no admission/arbitration/state-transition input may read scaffold state
Release build PASS
directed bookkeeping tests PASS
instrumentation/scaffold OFF vs ON exact simulated timing equality on representative natural workloads
terminal no-leak/invariant checks PASS
```

Any enabled-state timing difference is a HARD STOP until explained/fixed.

## D8. Cross-lane ingestion — mandatory

Lane D must ingest data incrementally, but must not treat a dependency as final until the workboard row is DONE with exact evidence.

Expected milestones:

```text
Lane A 26/26 -> refresh final D256 analysis
Lane B D512_READY -> enable D512 schema/config support
Lane B D512_MIRROR_COMPLETE -> full D256/D512 comparison
Lane C D256 cells -> L1 causal screen
Lane C D512 cells/decomposition -> interaction analysis
```

## D9. Review pack / report — mandatory

Maintain:

```text
docs/ep_l2/codex_handoff/LANE_D_LATEST.md
```

and a browsable pack such as:

```text
docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/
```

with:

```text
temporal cardinality audit
temporal distribution outputs
joint analyzer schema/tests
descriptor hardware-cost report
provenance validation tests
commands/reproducibility notes
optional scaffold diff/tests/timing-neutrality evidence
open issues
SHA256SUMS
```

## Completion states

Lane D may report staged milestones:

```text
TEMPORAL_ANALYSIS_READY
CALIBRATION_ANALYZER_READY
D512_COST_READY
OPPORTUNITY_SCAFFOLD_READY   # only if optional scaffold completed correctly
```

The lane is convergence-ready when the required first three are complete and it can ingest Lane A/B/C without manual format surgery.

It must not declare `BASELINE-DECISION` itself.

## Hard stops

Stop and request review if completion would require:

```text
repairing missing formal telemetry by inventing data
modifying raw logs
changing Lane A/B/C experiment definitions
using incompatible provenance as if comparable
adding enabled Core scaffold that changes simulated timing/state behavior
implementing functional RO/TVD/Unified before baseline decision
```
