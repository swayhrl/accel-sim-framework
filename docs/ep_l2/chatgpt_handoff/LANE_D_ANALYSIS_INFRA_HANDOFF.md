# EP-L2 Lane D — Analysis / Cost / Opportunity-Prep Handoff

Owner: dedicated Codex Window D.

## Objective

Use the time while simulation lanes run to prepare all analysis infrastructure needed for the calibration decision, quantify descriptor512 hardware plausibility, and prepare timing-neutral opportunity-study scaffolding without implementing or claiming functional RO/TVD/Unified mechanisms.

Lane D should minimize simulator-core edits. Prefer Framework analysis/docs branches; any Core scaffold must be isolated and must not be consumed by formal/calibration runs before review.

Suggested Framework branch:

```text
hrl/ep-l2-cal-analysis-v0
```

If an opportunity scaffold later needs Core changes, use a separate branch such as:

```text
hrl/ep-l2-opportunity-scaffold-v0
```

## D1 — Finish temporal analysis tooling

The interim 22/26 pack already contains L2 and DRAM 5K window records, but the current summary mostly counts rows.

Implement analysis that reports per workload/variant, and later per calibration cell:

```text
Descriptor window avg/p50/p95/max
fraction of windows near descriptor capacity
fraction of windows at descriptor capacity
Line-MSHR window avg/p50/p95/max where available
L2->DRAM occupancy window avg/p50/p95/max
scheduler occupancy window avg/p50/p95/max
scheduler-full-active window fraction
internal ReturnQ window avg/p95/max
window read/write bytes
window bandwidth-util p50/p95/max
channel max/mean or CV-style imbalance metric
burst duration / consecutive high-pressure windows where robust
```

Keep `measured zero` distinct from `field missing`.

Audit temporal cardinality explicitly:

```text
configured L2 slice count
configured DRAM channel count
unique slice/channel IDs observed
expected vs actual row counts
```

If a producer defect is found, update the workboard immediately; do not silently repair formal raw data.

## D2 — Joint calibration analyzer

Prepare an analyzer that can ingest incrementally:

```text
D256 formal baseline
D512 mirror
D256 + L1 META-HR
D256 + L1 BANK-HR
D512 + L1 META-HR
D512 + L1 BANK-HR
```

The analyzer should join by:

```text
workload
variant
source SHA
config hash
descriptor capacity
L1 config class
```

and produce both absolute values and deltas against the matching baseline.

Required outputs should support:

```text
cycle speedup
descriptor pressure movement
Line-MSHR pressure movement
L1 pressure movement
WAD/payload/bank movement
actual lower traffic/bytes
scheduler/BW movement
temporal burst/sustained change
```

Do not compare mismatched provenance/config cells.

## D3 — Descriptor 256 -> 512 hardware-cost analysis

Quantify the proposed hardware metadata cost, not C++ host-container overhead.

Audit the logical descriptor fields needed in hardware, for example as actually represented by the model/proposed design:

```text
valid/free state
requester identity / routing metadata
sector/request mask
response bookkeeping
pointer/index to line-MSHR/transaction state if required
any ordering/state bits
```

Produce a range if some physical bit widths are architecture-dependent.

Report:

```text
bits/descriptor
bytes/descriptor
256-entry bytes/slice
512-entry bytes/slice
incremental bytes/slice
incremental bytes/chip for 64 slices
percentage of 144 KiB/slice unified payload budget
percentage of 9 MiB chip payload budget
comparison with tag/MSHR/WAD metadata where defensible
```

Clearly separate:

```text
VERIFIED model fields
hardware mapping assumptions
upper/lower bound estimates
```

The purpose is to decide whether D512 is plausible baseline provisioning rather than performance tuning.

## D4 — Baseline decision template

Prepare, but do not prematurely fill, a decision document with these cases:

```text
D256 retained
D512 promoted
L1 BASE retained
L1 baseline requires recalibration
```

Decision evidence must include:

```text
performance sensitivity
pressure movement
hardware plausibility
cross-workload generality
negative controls
whether a cheaper/simple resource increase subsumes the claimed EP-L2 opportunity
```

No final baseline decision is owned by Lane D alone.

## D5 — Opportunity-study scaffold only

After Lane B establishes stable descriptor parameterization, Lane D may prepare reusable timing-neutral shadow infrastructure for the later opportunity stage:

```text
per-address shadow record API
kernel/epoch tagging
bounded event logging / aggregation
shadow lifetime tracking
analysis hooks
unit tests
```

It may prepare interfaces for future:

```text
RO eligibility/shadow
TVD reuse shadow
payload-role complementarity
```

but must not yet implement a functional cache-policy mechanism or publish opportunity performance results.

Do not assume RO no-MSHR motivation. The calibrated bottleneck result will determine whether RO should primarily target MSHR lifetime, descriptor lifetime, tag residency, or another resource.

## D6 — Continuous analysis while lanes run

Lane D may consume completed runs incrementally and generate provisional summaries, but must label them with exact completion scope and never mix incomplete D512/L1 matrices into a final aggregate.

When new Lane A/B/C artifacts appear, refresh analysis without changing simulator raw results.

## Acceptance criteria

Lane D closeout for the calibration phase requires:

```text
[ ] temporal distributions and cardinality audit implemented
[ ] calibration analyzer handles all planned cells with provenance guards
[ ] descriptor hardware-cost report produced with assumptions explicit
[ ] baseline-decision template ready
[ ] no functional opportunity mechanism contaminates calibration source/results
[ ] analysis outputs distinguish causal events, occupancy, retries, and unavailable fields
```

## Deliverables

Publish:

```text
docs/ep_l2/codex_handoff/LANE_D_LATEST.md
docs/ep_l2/review_packs/CALIBRATION_ANALYSIS_INFRA_r1/
docs/ep_l2/calibration/DESCRIPTOR_METADATA_COST.md
```

Recommended analysis artifacts:

```text
TEMPORAL_DISTRIBUTIONS.csv
CHANNEL_IMBALANCE.csv
CALIBRATION_MATRIX.csv
CALIBRATION_DELTAS.csv
BASELINE_DECISION_TEMPLATE.md
TELEMETRY_SEMANTICS.md
```

If opportunity scaffold is created, use its own review pack and branch; do not merge it into calibration source.

Update workboard rows:

```text
D-COST
CAL-ANALYSIS
OPP-PREP
```

## STOP boundaries

Do not modify or rerun Lane A formal jobs.
Do not independently create D512 semantics; consume Lane B's published base.
Do not independently change L1 configs; consume Lane C's definitions.
Do not declare `BASELINE-DECISION` PASS.
Do not implement functional RO no-MSHR, TVD, or Unified borrowing before reviewed calibration convergence.