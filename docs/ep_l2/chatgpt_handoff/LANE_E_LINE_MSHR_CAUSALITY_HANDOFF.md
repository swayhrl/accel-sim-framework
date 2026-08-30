# EP-L2 Lane E — Line-MSHR Causality Probe

Owner: dedicated Codex Window E.

## Objective

Test whether the 128-entry L2 Line-MSHR limit that becomes visible after Descriptor-512 relief is a **causal performance bottleneck** or only the next admission/backpressure symptom.

This lane is a sensitivity experiment. `Line MSHR = 256` is **not** a proposed primary hardware baseline.

Do not enlarge MSHR resources until a desired story appears. Measure one justified headroom point and let the result determine the mechanism motivation.

## Evidence motivating the lane

The current Lane-B interim D512 evidence for `convolutionSeparable / B0-Banked` is unusually clean:

```text
D256 / MSHR128:
  cycles                       290,308
  descriptor_pool_full_block  3,373,327
  descriptor p95/max          256 / 256
  line_mshr p95/max           112 / 126
  line_mshr_full_block        0

D512 / MSHR128:
  cycles                       292,211
  descriptor_pool_full_block  0
  descriptor p95/max          321 / 427
  line_mshr p95/max           128 / 128
  line_mshr_full_block        931,416
  bank_true_conflict_ops      0
```

Thus descriptor relief naturally exposes exact Line-MSHR-full blocking without a Banked-contention confound, but D512 alone gives no speedup. Lane E asks whether relieving this new MSHR ceiling changes performance or merely moves pressure farther downstream.

A short negative control is also available:

```text
D512 / spmv / MSHR128:
  line_mshr max               125
  line_mshr_full_block        0
  per-address-cap block       ~20K
```

## Source identity and isolation

Use the frozen Lane-B D512 candidate as the semantic source parent:

```text
Core      878f80869ce212e779df20b6421e4dc7f987825d
Framework aae62b66685f15437cecf0193934f628e6fac6ae
D512 runtime composite SHA-256
          a7dc3ce28f5e54ca966d08a7e3548a844533a9bee08b63ea4d964cd9ec2c9416
```

The formal D256 semantic base remains:

```text
Core      ece1a3a77c5628763e0a4605bfd1c639ee6a1495
Framework f08d2ce857972fad73c4e1ab7162ba94c6336507
config    85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d
```

Lane B has already proved the descriptor-generalized Core configured at D256 byte-identical to formal C7e on `vectorAdd_4M`, `spmv`, and `scan`. Preserve that lineage.

Suggested isolated worktrees:

```text
Framework /workspace/worktrees/accel-sim-ep-l2-mshr-causality
Core      /workspace/worktrees/gpgpu-sim-ep-l2-mshr-causality
```

Suggested branches:

```text
Framework hrl/ep-l2-mshr-causality-v0
Core      hrl/ep-l2-mshr-causality-v0
```

Results:

```text
/workspace/results/ep_l2_line_mshr_causality/
```

Never modify Lane A/B/C/D active worktrees or result roots.

## E1 — Parameterization / telemetry audit

Before running MSHR256, audit every assumption that Line-MSHR occupancy cannot exceed 128:

```text
mshr_table line-entry capacity
full/full_reason logic
line occupancy counter/max
line occupancy histogram size
p95 calculation
kernel/window delta handling
parser/schema numeric handling
config plumbing / effective-config diff
review analyzer/tests
```

Search for hard-coded `128`, `129`, fixed line-histogram bounds, or assertions whose semantic role is Line-MSHR capacity.

The current `line_hist` path may clip p95 values above 128 even if the allocator itself is parameterized. If so, generalize telemetry only; do not change allocation/lifetime semantics.

## E2 — Observation-only source equivalence

If Core telemetry is generalized, prove the final Lane-E source at `Line MSHR=128` is behaviorally/timing equivalent to the frozen Lane-B source.

At minimum rerun:

```text
vectorAdd_4M / D512 / B0-Banked / MSHR128
convolutionSeparable / D512 / B0-Banked / MSHR128
```

Require exact equality for:

```text
gpu cycles
instructions
descriptor need/full
Line-MSHR need/full
per-address cap
L1 key counters
L2->DRAM / scheduler / DRAM bytes
bank true-conflict/wait
terminal invariants
```

Parsed CSV byte identity is preferred where the representation is unchanged.

## E3 — Directed boundary tests

Test Line-MSHR entry boundaries independently from Descriptor capacity and per-address cap.

At minimum cover:

```text
127 / 128 / 129 live line entries under capacity 256
255 / 256 live line entries
new distinct-line allocation at full capacity
release one line entry and allocate again
distinct addresses so per-address cap cannot fire first
descriptor capacity large enough so Descriptor pool cannot fire first
line occupancy telemetry >128 is not clipped
terminal no-leak / ownership consistency
```

The blocker at capacity must be the exact Line-MSHR-full reason, not descriptor/per-address/lower-path reason.

## E4 — Primary 2x2 causal matrix

Workload: `convolutionSeparable`  
Variant: `B0-Banked`  
Frequency: 850 MHz  
L1: BASE  
Per-address cap: 32  
All other resources/timing frozen.

Matrix:

```text
                          Line-MSHR 128       Line-MSHR 256
Descriptor 256            existing formal     NEW Lane-E run
Descriptor 512            existing Lane-B     NEW Lane-E run
```

The two new configurations change only the Line-MSHR entry capacity relative to the matching descriptor base.

The D512/MSHR256 row is `SPECULATIVE_PENDING_GATE` until the exact Lane-B D512 candidate receives `D512_PREFLIGHT_PASS`. Do not wait to launch it.

## E5 — Short negative control

Run:

```text
spmv / B0-Banked / D512 / Line-MSHR256
```

against the existing D512/MSHR128 row. Because MSHR128 has no exact Line-MSHR-full blocking here, this is a useful control against claiming that any MSHR enlargement automatically helps.

If the control changes cycles materially, investigate before making the convolution causal claim.

## Measurements

For each cell retain:

```text
cycles / instructions
Descriptor need/full/avg/p95/max
Line-MSHR need/full/avg/p95/max
per-address-cap checks/blocks
chain depth
L1 accesses/misses/blockers
WAD / payload / bank contention
L2->DRAM occupancy/full
scheduler occupancy/full/causal block
ReturnQ / DRAM->L2
DRAM read/write bytes
native final-complete 32-channel DRAM bus utilization when available
5K temporal Descriptor/MSHR/lower/scheduler distributions
terminal invariants
```

Do not call lower-admission normalization physical bandwidth.

## Causal interpretation

### Strong MSHR-causal result

```text
D512 MSHR128 -> MSHR256:
  Line-MSHR-full collapses materially
  AND cycles improve materially

while

D256 MSHR128 -> MSHR256:
  little/no improvement
```

This is strong evidence that Descriptor-256 masked an MSHR capacity bottleneck that becomes performance-relevant after descriptor relief. It materially strengthens RO no-MSHR motivation.

### Admission-throttle but downstream-limited

```text
Line-MSHR-full collapses
but cycle improvement <~2%
and lower/scheduler/native-DRAM pressure rises
```

Then MSHR128 is a real admission ceiling but not the final performance ceiling. RO no-MSHR cannot be justified as a simple capacity fix; any benefit must come from other semantics such as transaction/tag-lifetime decoupling or reduced downstream work.

### No causal MSHR evidence

If MSHR256 changes neither performance nor meaningful downstream behavior, classify the MSHR-full signal as largely symptomatic/backpressure for this workload.

### Still MSHR-limited at 256

If exact Line-MSHR-full remains substantial at 256, report it. Do **not** automatically increase to 512; further capacity calibration requires a separate hardware-cost/research decision.

## Output / review pack

Create:

```text
docs/ep_l2/codex_handoff/LANE_E_LATEST.md
docs/ep_l2/review_packs/LINE_MSHR_CAUSALITY_r1/
```

Include:

```text
README.md
SOURCE_ANCHORS.md
CONFIG_DIFF.md
MSHR128_EQUIVALENCE.md
BOUNDARY_TESTS.md
RUN_STATUS.csv
CONVOLUTION_2X2.csv
SPMV_NEGATIVE_CONTROL.csv
RESOURCE_MOVEMENT.csv
TEMPORAL_SUMMARY.csv
CAUSAL_INTERPRETATION.md
VALIDATION_SUMMARY.md
RAW_LOG_INDEX.tsv
SHA256SUMS
OPEN_ISSUES.md
```

Lane E uses its own analysis/reporting; do not modify the frozen Lane-D V3 analyzer merely to ingest this new experimental dimension.

## STOP boundary

Stop after `LINE_MSHR_CAUSALITY_PROBE_COMPLETE` and request ChatGPT review. Do not promote MSHR256 to the primary baseline, change Descriptor beyond the existing D256/D512 definitions, or implement RO/TVD/Unified mechanisms.
