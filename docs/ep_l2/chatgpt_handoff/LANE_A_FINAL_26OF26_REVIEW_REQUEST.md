# EP-L2 Lane A — Final 26/26 Independent Review Request

Date: 2026-08-30

Purpose: prepare the completed C7e Target-Baseline campaign for independent ChatGPT acceptance review. This is a **review/analysis/packaging-only** stage. The formal simulator campaign is already complete and must remain immutable.

## Authoritative formal runtime identity

```text
Core runtime SHA:
  ece1a3a77c5628763e0a4605bfd1c639ee6a1495

Framework runtime SHA:
  f08d2ce857972fad73c4e1ab7162ba94c6336507

Frequency:
  850 MHz

Formal set:
  13 workloads x {B0-Legacy, B0-Banked} = 26 runs
```

Current final pack:

```text
docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_r1/
```

Current Codex report:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md
```

## Hard boundary

Do **not**:

```text
rerun any formal simulator job
rebuild or alter the formal runtime binary
edit/checkout/reset/clean the formal Lane-A runtime worktrees
change any runtime/config/trace semantic
start 1 GHz
start RO no-MSHR
start TVD
start Unified borrowing
silently replace any accepted formal row
```

All work in this request is read-only with respect to the formal run roots. Parser/reporting fixes may reprocess retained raw logs when producer data are sufficient.

## A. Freeze an explicit accepted 26-run set

Create a machine-readable table with exactly 26 accepted rows, for example:

```text
ACCEPTED_FORMAL_RUNS.csv
```

Each row must include at least:

```text
workload
variant
run directory
status = COMPLETE_VALID
Core SHA
Framework SHA
runtime_config_composite_sha256
trace identity/hash where available
terminal cycles
terminal instructions
normal exit
parser success
terminal_clean
payload consistency
raw-log path/hash
```

Require exactly one accepted row for every workload/variant pair.

## B. 3mm duplicate-write incident closeout — mandatory

The earlier duplicate-write affected 3mm output must never be part of the accepted 26.

Create:

```text
EXCLUDED_DIAGNOSTIC_RUNS.csv
3MM_REPLACEMENT_AUDIT.md
```

The audit must identify:

```text
- every affected/excluded 3mm diagnostic path;
- why it is invalid for formal use;
- the exact clean replacement B0-Legacy and B0-Banked paths used in the formal set;
- source/config/trace identities of the replacements;
- proof that aggregate scripts consume only the replacements;
- no duplicate accepted workload/variant keys.
```

Do not delete diagnostic evidence; quarantine/index it explicitly.

## C. Final acceptance matrix A-K

Create:

```text
FINAL_ACCEPTANCE_MATRIX.md
```

Evaluate the established final-26 gates with direct evidence paths:

```text
A. source/config uniformity
B. 26/26 completion
C. per-run provenance
D. terminal invariants
E. required parsed artifacts
F. mandatory C7e telemetry coverage
G. Legacy/Banked attribution sanity
H. temporal/kernel integrity
I. aggregate output completeness
J. interpretation discipline
K. review packaging / hashes / raw-log index
```

Do not rely on a top-level PASS label alone. Link each gate to tables/files that allow independent verification.

## D. Reprocess the full 26 with the reviewed Lane-D V3 analysis semantics

The original C7e runtime pair remains authoritative. Analysis code is a separate identity.

Use the reviewed Lane-D V3 analyzer semantics from exact analysis source:

```text
Framework analysis branch: hrl/ep-l2-cal-analysis-v0
reviewed source commit:
  cb83606eb8640382b7c1932d8981b70608d9d130
```

Use an isolated analysis worktree/tool invocation. Never checkout this commit into the formal Lane-A runtime worktree.

Record separately in every review manifest:

```text
runtime_core_sha
runtime_framework_sha
analysis_framework_sha
```

For all 26 accepted rows, refresh/derive the corrected analysis outputs using the already-reviewed semantics:

```text
- C7e bandwidth_util -> lower_admission_byte_rate_norm
- native application-level physical DRAM data-bus utilization from the final complete 32-channel snapshot
- native DRAM weighted mean + p50/p95/max + n_cmd sum
- 64-slice / 32-channel 5K stream cardinality and exact time-group alignment
- scheduler / ReturnQ cycle fractions
- longest high-average-window-run semantics
- traffic-conditioned / traffic-weighted channel imbalance
- NOT_EMITTED distinct from measured zero
```

If the reviewed V3 analyzer needs only a D256 formal contract for this campaign, use its reviewed formal contract and actual runtime config hash. Do not invent new calibration deltas.

## E. Full 13-workload Target-Baseline analysis

Produce final 13-workload summaries. At minimum include:

```text
TARGET_BASELINE_FINAL_STATUS.tsv
target_baseline_comparison.csv
target_resource_pressure.csv
target_blocking_matrix.csv
target_bank_pressure.csv
target_lower_path.csv
target_l1_pressure.csv
target_temporal_summary.csv
target_kernel_summary.csv
TARGET_BASELINE_BOTTLENECK_ANALYSIS.md
TARGET_BASELINE_CLOSEOUT.md
```

For each workload report, using both variants where appropriate:

```text
cycles Legacy / Banked
Banked/Legacy cycle ratio
Tag-way need/block
Line-MSHR need/full/avg/p95/max
Descriptor need/pool-full/avg/p95/max
per-address-cap checks/blocks
WAD occupancy/full/hazard/lifetime evidence
Payload capacity/service denial
bank logical ops / true conflicts / wait
L1D accesses/misses/line-alloc/MSHR/merge/MissQ/RW-pending/bank-latency pressure
L2->DRAM queue pressure
DRAM issue/scheduler pressure
internal ReturnQ
DRAM->L2
native physical DRAM bus utilization
5K sustained-vs-bursty behavior
channel imbalance when traffic-conditioned evidence supports it
kernel-level heterogeneity when present
```

Use conservative labels such as:

```text
DOMINANT_OBSERVED_BLOCKER
SECONDARY_BLOCKER
HIGH_UTIL_NOT_BLOCKING
MIXED
NO_CLEAR_INTERNAL_BOTTLENECK
```

Do not infer causality from occupancy/retry counts alone. Do not quantify future RO/TVD/Unified opportunity from this baseline package.

## F. Explicitly reconcile prior interim findings

Create a short section/file:

```text
INTERIM_TO_FINAL_RECONCILIATION.md
```

State whether the four late runs (`gemm` and `3mm`, both variants) materially alter the 22/26 interim conclusions, especially:

```text
- shared descriptor pressure vs Line-MSHR pressure;
- per-address cap importance;
- Tag/set pressure;
- WAD pressure;
- payload capacity/service pressure;
- true B0-Banked contention after C6d;
- L1 competing pressure;
- lower-path / scheduler / native-DRAM-bandwidth behavior;
- sustained vs bursty pressure.
```

Do not extrapolate if evidence is weak.

## G. Review-ready pack

Do not overwrite or mutate the original final pack. Create a separate review-ready supplement, suggested path:

```text
docs/ep_l2/review_packs/TARGET_BASELINE_FINAL_26OF26_C7E_REVIEW_READY_r1/
```

Suggested contents:

```text
README.md
FINAL_ACCEPTANCE_MATRIX.md
ACCEPTED_FORMAL_RUNS.csv
EXCLUDED_DIAGNOSTIC_RUNS.csv
3MM_REPLACEMENT_AUDIT.md
SOURCE_AND_ANALYSIS_ANCHORS.md
FORMAL_PROVENANCE_AUDIT.csv
TELEMETRY_COMPLETENESS.md
INTERIM_TO_FINAL_RECONCILIATION.md
TARGET_BASELINE_BOTTLENECK_ANALYSIS.md
TARGET_BASELINE_CLOSEOUT.md
analysis/*.csv
RAW_LOG_INDEX.tsv
VALIDATION_SUMMARY.md
SHA256SUMS
```

Keep large raw logs out of Git; index their immutable paths/hashes.

## H. Handoff

Update:

```text
docs/ep_l2/codex_handoff/LATEST_REPORT.md
```

with:

```text
Stage: Final Target Baseline — ChatGPT independent review ready
Status: TARGET_BASELINE_26RUN_REVIEW_READY
runtime Core SHA
runtime Framework SHA
analysis Framework SHA
26/26 accepted
excluded diagnostic run count
3mm replacement audit PASS/FAIL
A-K self-gate summary
review pack entry point
```

Push documentation/analysis outputs to:

```text
hrl/ep-l2-exp-v0
```

Then STOP. Do not start Opportunity Study, 1 GHz, RO, TVD, or Unified.

## Independent-review note

Codex's self-gate result is not the final acceptance decision. ChatGPT will independently verify the source/config uniformity, accepted-run set, 3mm replacement, telemetry semantics, full 13-workload aggregates, and interpretation before accepting or rejecting `TARGET_BASELINE_26RUN_PASS`.
