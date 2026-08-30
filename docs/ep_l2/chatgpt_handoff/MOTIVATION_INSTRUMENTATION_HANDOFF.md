# EP-L2 Motivation Instrumentation Handoff

Status: **AUTHORIZED — new isolated lane**

## 1. Objective

Build one timing-neutral motivation-instrumentation branch that can generate the two primary motivation figures from one workload replay per configuration:

1. **L2 reuse-distance distribution**;
2. **L2 miss-admission structural blocking breakdown**, with simultaneous shadow WBUF capacities 4/8/16.

This lane is independent from the running M0b and M3A work.

## 2. Required reading

Read before any implementation:

```text
docs/ep_l2/project_spec/README.md
docs/ep_l2/project_spec/RESEARCH_CHARTER.md
docs/ep_l2/project_spec/ARCHITECTURE_BLUEPRINT.md
docs/ep_l2/project_spec/EVIDENCE_AND_CLAIM_MODEL.md
docs/ep_l2/project_spec/MOTIVATION_FIGURES_PLAN.md
docs/ep_l2/project_spec/decisions/ADR-005-calibrated-research-baseline.md
docs/ep_l2/project_spec/decisions/ADR-009-motivation-wbuf-shadow-definition.md
docs/ep_l2/project_spec/EXPERIMENT_MODE_SWITCH_CONTRACT.md
```

Also read the reviewed M0a/integration state so that existing blocking semantics are not silently changed.

## 3. Source parent and isolation

Use the promoted M0a+M1 integrated development parent:

```text
Core:
1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e

Framework runtime parent:
d61ffd23c926a25fa463a3e6e955c885b45f0f8a
```

Create fresh isolated worktrees:

```text
Framework:
/workspace/worktrees/accel-sim-ep-l2-motivation/

Core:
/workspace/worktrees/gpgpu-sim-ep-l2-motivation/

Branch in each repository:
hrl/ep-l2-motivation-v0

Result root:
/workspace/results/ep_l2_motivation/
```

The permanent coordination worktree remains:

```text
/workspace/worktrees/accel-sim-ep-l2/
branch hrl/ep-l2-exp-v0
```

Do not use the coordination worktree as simulator source.

## 4. Configuration / mode contract

Add a separate default-OFF motivation telemetry option, for example:

```text
-gpgpu_ep_l2_motivation_stats 0/1
```

The exact option name may differ, but it must be explicit and default OFF.

Timing-neutral controls compare:

```text
M0A_ON + MOTIVATION_OFF + M1_STATIC
vs
M0A_ON + MOTIVATION_ON  + M1_STATIC
```

The only effective-config difference must be the motivation telemetry enable.

No functional mechanism is enabled.

## 5. Source audit before implementation

Create a source map that identifies exact production events for:

```text
frontend L2 demand reference
kernel/epoch boundary
real tag/set lookup / miss admission
resident line eviction
real dirty-victim WB packet creation
real WB lower-path acceptance
WAD allocation/hazard/full checks
Line-MSHR full/per-address-cap/ordering checks
descriptor-pool full checks
short MissQ/lower-queue admission checks
```

Freeze the actual primary admission order from source. Do not invent a chart-oriented order.

## 6. Reuse-distance profiler

### 6.1 Primary demand stream

Implement the reference stream exactly as defined in `MOTIVATION_FIGURES_PLAN.md`:

- 128-B normalized block address;
- frontend demand L2 references only;
- exclude L2-generated WB, fills/returns and internal retry bookkeeping;
- reset primary reuse state at kernel/epoch boundary.

Emit explicit included/excluded request-class counters so the stream can be audited.

### 6.2 Exact bounded stack distance

Compute exact reuse/stack distance through 1024 distinct blocks.

Required classification:

```text
<=8
9-16
17-32
33-64
65-128
129-256
257-512
513-1024
>1024
```

An address previously seen in the same epoch but outside the most-recent 1024 distinct blocks belongs to `>1024`.

A first touch is not a reuse instance and must not enter the nine-bin denominator.

Choose an implementation with bounded/acceptable host overhead. A validated order-statistics or equivalent exact-bounded algorithm is preferred over O(1024) scanning on every access.

### 6.3 Coverage state

Track enough per-epoch state to emit:

```text
eligible demand refs
reuse instances
unique lines
unique lines reused >=1 time
one-touch unique lines
```

### 6.4 Post-eviction supplement

Record timing-neutral real-eviction re-reference information:

```text
block address
eviction demand sequence index
eviction cycle
next demand re-reference sequence/cycle
```

Generate post-eviction reuse distance/time summaries without changing cache behavior.

## 7. Shadow WBUF 4/8/16

### 7.1 Frozen lifecycle

Follow ADR-009 exactly.

One real WB staging lifetime is:

```text
real WB packet creation
->
real successful lower-path / L2->DRAM acceptance
```

WBUF release is **not** `set_done()`.

### 7.2 One-run multi-capacity shadow

Simultaneously evaluate:

```text
C=4
C=8
C=16
```

Maintain the actual set/count of real WB packets currently between creation and lower acceptance.

At every dirty-victim admission opportunity, derive trace-projected capacity pressure for each C from this same observed active-WB state.

No shadow capacity may alter real request ordering, admission, WB creation or lower issue.

### 7.3 WBUF metrics

Emit all metrics specified in `MOTIVATION_FIGURES_PLAN.md`, including real WB staging lifetime distributions.

## 8. Exclusive primary miss-admission classifier

Implement a non-mutating motivation classifier for frontend demand-miss admission.

For each WBUF capacity C, determine the first blocking class according to the audited production order:

```text
SET_ASSOC
MSHR_META
MISSQ_LOWER
WB_PATH
OTHER
```

Rules:

- exactly zero or one primary blocker per eligible attempt/cycle and capacity;
- no double counting in the stacked-bar accounting;
- `WB_PATH` may include mandatory WAD/order restriction and the shadow WBUF-C restriction;
- persistent descriptor-pool capacity belongs in `MSHR_META`, not `MISSQ_LOWER`;
- short lower-issue / lower-queue capacity belongs in `MISSQ_LOWER`;
- keep `OTHER` explicit during validation.

For every C, assert/check:

```text
SET_ASSOC + MSHR_META + MISSQ_LOWER + WB_PATH + OTHER
== projected_blocked_miss_admission_cycles_C
```

Do not claim the 4/8/16 shadow result is a counterfactual performance simulation.

## 9. Output schema

Create a distinct motivation record family/schema, not a semantic mutation of `EPL2B0V1` or `L2CHARV1`.

Suggested family name:

```text
EPL2MOTV1
```

Exact name may differ but must be versioned and unique.

Required parser outputs should include at least:

```text
motivation_summary.csv
reuse_distance.csv
reuse_coverage.csv
post_eviction_reuse.csv
blocking_breakdown.csv
wbuf_sensitivity.csv
wbuf_lifetime.csv
manifest.json
run_status.json
```

Retain per-slice/per-kernel data where needed for exact aggregation, but the primary plots are application-level.

## 10. Plotting outputs

Create deterministic plotting scripts and generate review previews:

```text
FIG1_L2_REUSE_DISTANCE_STACKED.svg
FIG1_L2_REUSE_DISTANCE_STACKED.png

FIG2_L2_BLOCKING_BREAKDOWN_WBUF8.svg
FIG2_L2_BLOCKING_BREAKDOWN_WBUF8.png

FIG2S_WBUF_4_8_16_SENSITIVITY.svg
FIG2S_WBUF_4_8_16_SENSITIVITY.png
```

Figure 1 nine reuse bins must sum to 1.0 per workload.

Figure 2 WBUF=8 four paper categories may be used only when diagnostic `OTHER <= 2%` for every plotted workload. Otherwise include `Other` and request review.

Also retain WBUF=4/16 complete tables even if only WBUF=8 is shown in the main preview.

Do not hard-code publication colors as scientific semantics; keep category ordering deterministic.

## 11. Validation sequence

Execute in this order:

```text
A. source map
B. implementation
C. Release build
D. directed reuse-distance fixtures
E. directed WBUF lifecycle/capacity fixtures
F. directed primary-block classifier fixtures
G. parser/aggregation/normalization tests
H. OFF/ON timing-neutral natural controls
I. pilot workloads
J. broad motivation set
K. review pack
```

Pilot workloads:

```text
vectorAdd_4M
convolutionSeparable
spmv
sad
```

After all correctness gates pass, launch broad workload runs in parallel where host resources permit:

```text
scan
vectorAdd_4M
convolutionSeparable
spmv
FWT_7_21
cfd_097k
dwt2d
sad
btree
gemm
```

Do not serially wait for `scan` before launching the other broad workloads.

## 12. Review deliverables

Publish:

```text
docs/ep_l2/codex_handoff/LANE_MOTIVATION_LATEST.md

docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/
  README.md
  SOURCE_MAP.md
  SOURCE_ANCHORS.md
  VALIDATION_SUMMARY.md
  FIELD_SEMANTICS.md
  WORKLOAD_STATUS.csv
  motivation_summary.csv
  reuse_distance.csv
  reuse_coverage.csv
  post_eviction_reuse.csv
  blocking_breakdown.csv
  wbuf_sensitivity.csv
  wbuf_lifetime.csv
  figures/
  validation/
  SHA256SUMS
```

Raw logs remain outside Git; publish a compact `RAW_LOG_INDEX.tsv`.

## 13. Stage stop state

Stop at:

```text
MOTIVATION_FIGURES_REVIEW_READY
```

Do not convert WBUF=4/8/16 shadow results into performance claims in this stage.