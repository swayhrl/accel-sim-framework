# DTC-L1 M5 Experiment Matrix

Status: **HISTORICAL MATRIX WITH M5.0BT SUPERSESSION — DO NOT USE STALE CAP-256/PTX-ONLY WORDING**

> Active supersession: exact trace capture/qualification gates M5.0C;
> formal replay is 80 SM, cap10240, ratio-zero and payload-aware after M5.0BT.

Parent validated anchors:

- Core M1-M4 final: `cdeec769fd0c1be12b45d58536ecb81074d4b415`.
- Framework M1-M4 final: `56369da33dc5f48fc9ac071fd122fde4b35bd8c9`.
- Core M5 branch: `hrl/decoupled-l1-m5-v0`.
- Framework M5 branch: `hrl/decoupled-l1-exp-m5-v0`.

M1-M4 are frozen validated infrastructure. M5 exists to expose the performance benefit and causal behavior of the already-implemented RTL mechanism in the simulator. The primary reproduction target is **mechanism/trend fidelity**, not numerical matching to the thesis' +22%/+30% numbers. If performance is weak or opposite to expectation, M5 must determine whether the cause is implementation/modeling, workload/input fidelity, downstream platform behavior, or a genuine mechanism limitation. It must not tune the design to a target speedup.

The thesis experiment logic reproduced by M5 is:

`traditional L1 structural limits -> fewer concurrent misses -> DTC removes limits -> more concurrent misses / better latency hiding -> performance`.

Paper-facing figures in scope:

- Figure 4.2: traditional L1 structural-stall breakdown.
- Figure 4.5: Base vs IO-DTC vs OO-DTC performance.
- Figure 4.7: average concurrent miss requests.
- Figure 4.8: logical-cache sensitivity.
- Figure 4.9: physical-cache sensitivity and IO passive-release deadlock pressure.
- Figure 4.10: pending-instruction-buffer sensitivity.

Figure 4.6 area is a separate track and is not a blocker for M5 performance experiments.

`MODERN_OO_SECTOR` is **not** part of Figures 4.2-4.10 and must not appear in paper-reproduction plots. It is an extension study only after whole-line paper-mode results are stable.

---

## 0. Common experiment contract

### 0.1 Paper-mode defaults

Unless a sensitivity experiment explicitly overrides one item, use the frozen M1-M4 defaults:

| Quantity | PAPER_BASE | PAPER_IO | PAPER_OO |
| --- | ---: | ---: | ---: |
| Mode | 1 | 2 | 3 |
| Logical L1 / Tag capacity | 16KB | 16KB | 16KB |
| Line size | 128B | 128B | 128B |
| Logical associativity | 4-way | 4-way | 4-way |
| Baseline PIB | 8 | -- | -- |
| DTC PIB | -- | 256 | 128 |
| Traditional L1 MSHR | 32 | not a DTC capacity | not a DTC capacity |
| Physical Cacheline Array | conventional 16KB data array | 80KB / 640 lines | 80KB / 640 lines |
| Tag banks | 4 | 4 | 4 |
| Tag service | 1 request/bank/cycle, max 4 | same contract | same contract |
| Physical allocation width | n/a | 4/cycle | 4/cycle |
| Lower issue width | source/frozen | 1 request/SM/cycle | 1 request/SM/cycle |
| Global DTC lower outstanding cap | n/a / source baseline | 256 | 256 |
| Ref Count | n/a | n/a | 13-bit default |
| SM count | 8 paper-mode target; verify actual config | same | same |

The M5.0 platform audit must verify every row against the actual runtime configuration before formal runs. If the current source option map differs, update the option map and the experiment manifest; do not silently assume the table is active.

The current simulator normally coalesces a warp in one simulator pass. This is a deliberate simulator abstraction shared across variants; do not claim exact RTL-cycle fidelity to the thesis' two 16-thread coalescers. A 16-vs-32 coalescer-width sensitivity belongs to an extension/robustness study, not the primary paper reproduction.

### 0.2 Formal result identity

Every FORMAL run is keyed by:

`{core_sha, framework_sha, config_sha256, workload_source_sha, binary/PTX_sha256, input_sha256, parser_schema}`.

Raw logs remain external. Committed evidence contains compact JSON/CSV plus a raw-log index with path, bytes, SHA-256, command, and classification.

If simulator behavior/timing changes after a FORMAL run, invalidate all affected downstream formal results and rerun them. If a change is instrumentation-only, Codex may retain existing performance cycles only after an exact sentinel differential proves no timing/dynamic-operation change; counters that did not previously exist still require reruns.

### 0.3 Performance metric

For each workload:

`speedup(IO) = cycles(PAPER_BASE) / cycles(PAPER_IO)`

`speedup(OO) = cycles(PAPER_BASE) / cycles(PAPER_OO)`.

Use end-to-end `gpu_tot_sim_cycle` under identical workload/input/unrelated configuration. Exact dynamic instruction and source-domain Load/Store/Atomic/FENCE_OP counts must match across the triplet. Application output/self-check must match when available.

Aggregate labels:

- `GM-CE`: geometric mean over the seven thesis cache-efficient compute workloads.
- `GM-GP`: geometric mean over all ten thesis general-purpose compute workloads. This is **our compute-only label**, not the thesis GM-ALL.
- `GM-ALL-PAPER`: reserved until the five graphics workloads are truly available in a source-backed graphics path.

Never call a compute-only aggregate `GM-ALL`.

### 0.4 Figure 4.7 concurrent-miss definition — frozen for M5

The primary metric is the user's chosen source-independent lifecycle definition:

> A miss becomes live when an L1/DTC new miss is committed into the lower-request ownership system and remains live through local lower-request queuing and in-flight service until the final lower response completes that request.

Pending-hit merges do not create a second live request. A DTC duplicate generated after logical-Tag eviction is a distinct committed lower request and therefore is counted as another live miss.

Implement common counters for Base/IO/OO:

- `live_miss_current` per SM;
- `live_miss_sum_cycles` per SM;
- `live_miss_sample_cycles`;
- `live_miss_peak` per SM;
- global current/sum/peak;
- create/complete conservation.

Primary plotted metric:

`avg_concurrent_misses_per_sm = sum_over_all_SM_and_sampled_cycles(live_miss) / (num_SM * sampled_kernel_cycles)`.

Also emit the unscaled GPU-total cycle average for audit. Sampling begins when the first kernel is active and ends after the last kernel and all modeled memory state drain. All variants must use the same sampling boundary definition.

Do not compare Base MSHR occupancy to IO/OO NoC occupancy under the same label. The common miss-lifecycle counter is the only Figure-4.7 formal metric.

---

# M5.0 — Fidelity Lock

M5.0 is mandatory before any formal Figure 4.x run. Its purpose is to establish that the workload, input scale, platform, Tag/coalescer service, and metric definitions exercise the intended mechanism rather than an accidental simulator artifact.

## M5.0A — Branch/anchor and reproducibility lock

### Work

1. Verify both M5 branches descend exactly from the validated M1-M4 heads above.
2. Build Core release mode and run all DTC CTests.
3. Rerun one LEGACY, PAPER_BASE, PAPER_IO, PAPER_OO VecAdd sentinel and compare against M4 closeout.
4. Create `docs/dtc_l1/m5/FORMAL_ANCHOR.md` recording source/config/toolchain/runtime-library identity.
5. Create a resumable result registry keyed by the formal identity tuple so Goal mode never blindly reruns a completed configuration.
6. Calibrate safe parallel simulation concurrency from measured host CPU/RAM use; do not oversubscribe merely to shorten wall clock.

### Acceptance

- M1-M4 CTests pass.
- Sentinels have no behavior/accounting regression.
- Both worktrees clean after checkpoint.
- A reproducible formal-anchor record exists.
- Batch runner can resume without duplicating completed valid runs.

### Handoff to M5.0B

Create `handoffs/M5_0A_ANCHOR.md` with parent/final SHAs, build/test commands, runtime-library hash, runner concurrency, and exact next-step workload-audit list.

---

## M5.0B — Recover all ten thesis compute workloads

The thesis Table 4.1 compute set is:

### Cache-efficient

`bicg, atax, gemv, mvt, syrk, gesu, syr2k`

### Cache-inefficient

`spmv, 2mm`

### Compute-intensive

`conv2d`

The first provenance audit must explicitly test the likely naming aliases from thesis descriptions:

- `gemv` -> canonical PolyBench `gemver`? Thesis description: vector multiplication and matrix addition.
- `gesu` -> canonical PolyBench `gesummv`? Thesis description: scalar/vector/matrix multiplication.
- `conv2d` -> canonical PolyBench `2DConvolution` / current `pb_2dconv` source-equivalent?

These are hypotheses until source/algorithm comparison confirms them.

### Resolution order

For every workload, Codex must continue resolving rather than stop at a missing ready binary:

1. search the active workload checkout and existing wrappers;
2. compare source algorithm and thesis description;
3. search canonical PolyBench/Parboil source already available or fetch canonical source if network is allowed;
4. reconstruct/build a wrapper using the same simulator/PTX toolchain;
5. record source commit/version and exact mapping status;
6. choose a deterministic input using the policy below.

Mapping states:

- `EXACT_MATCH`;
- `SOURCE_EQUIVALENT_CONFIRMED`;
- `SOURCE_EQUIVALENT_STANDARD_INPUT`;
- `UNRESOLVED` only after documented exhaustive audit; an unresolved ready binary must never be replaced by a different algorithm.

### Input policy

The thesis states that benchmark scale was chosen so GPU execution lanes remain fully loaded but does not provide exact numeric input sizes in the available text. Therefore:

1. use the benchmark suite's canonical/default paper input when identifiable;
2. otherwise use a standard named dataset size (prefer PolyBench LARGE/EXTRALARGE or canonical Parboil inputs);
3. select the smallest standard dataset that demonstrably gives work to all 8 SMs and sustains more than a trivial single wave of CTAs where the algorithm permits;
4. choose scale using **Base-only occupancy/work-amount evidence**, never by choosing the input that gives DTC the largest speedup;
5. record all dimensions/dataset names/hashes.

SpMV receives special audit because the M4 `fidapm05` run only reached Base PIB peak 3 and therefore did not exercise the thesis' claimed PIB-limited behavior. Codex must inspect the canonical Parboil inputs and launch/workload scale rather than accepting the M4 input as paper-equivalent by default.

### Acceptance

- All ten algorithms have source-backed mappings and reproducible build/run commands.
- `gemv/gemver`, `gesu/gesummv`, and `conv2d/2DConvolution` are explicitly resolved.
- Every workload has deterministic source/PTX/input provenance.
- Selected input scales satisfy the full-load policy without DTC-result tuning.
- A one-mode Base smoke completes and output/self-check is valid for all ten.

### Handoff to M5.0C

Create/update `implementation/M5_COMPUTE_WORKLOAD_MANIFEST.md` and `handoffs/M5_0B_WORKLOADS.md`. The handoff must include all ten workload IDs, mapping status, algorithm proof, source SHA, PTX/binary hash, input dimensions/hash, launch geometry, and any known runtime cost.

---

## M5.0C — Platform/config fidelity audit

### Work

Audit actual runtime values and source integration for:

- SM count and occupancy limits;
- L1 line size, size, ways, banks, latency;
- Base PIB=8 and MSHR=32;
- Base/IO/OO common Tag-bank service semantics;
- IO PIB=256 and OO PIB=128;
- logical 16KB Tag geometry;
- physical 80KB / 640-line pool;
- allocation width 4;
- lower issue width 1/SM/cycle;
- configured global lower cap and any **natural source downstream cap** that may be smaller;
- coalescer width/transaction geometry;
- L2/NoC/DRAM settings;
- store/atomic/bypass source path;
- current compiler/PTX target.

Create a current, non-stale `M5_CONFIG_KNOB_MAP.md`. The old M2-era knob map is not sufficient evidence.

### Special fidelity audit: Tag-bank behavior

M4 ATAX showed many Base Tag-bank conflicts while IO reported zero. Before formal performance, determine whether this is:

- a legitimate consequence of identical 4-bank/1-per-bank service under different request timing;
- an implementation mismatch in how Base vs DTC submits Tag requests;
- or an instrumentation-definition mismatch.

Do not disable Tag-bank timing to improve speedup. If service semantics are inconsistent, fix the implementation while preserving the frozen 4-bank contract and rerun M1-M4 sentinels.

### Acceptance

- Every common default is verified from config/source rather than assumed.
- Base/IO/OO unrelated GPU configuration is identical.
- Any natural downstream cap is explicitly documented.
- Tag-bank service is semantically consistent or a source-backed repair is completed and regressed.
- `M5_CONFIG_KNOB_MAP.md` is current.

### Handoff to M5.0D

`handoffs/M5_0C_PLATFORM.md` contains the exact formal base config, all permitted per-figure overrides, source anchors, and a list of downstream platform differences from the thesis that may affect numerical performance but do not invalidate mechanism testing.

---

## M5.0D — Metric/instrumentation lock

### Required common metrics

1. End-to-end cycles and dynamic operation counts.
2. Figure-4.7 common live concurrent misses, as defined in section 0.4.
3. Figure-4.2 paper-equivalent structural stall categories.
4. PIB occupancy/peak/full.
5. Base MSHR entry/merge pressure.
6. true Tag/cacheline allocation failures, separate from Tag-bank arbitration conflict.
7. lower/miss-queue/downstream capacity pressure.
8. DTC valid hit / pending hit / new miss.
9. lower request traffic and duplicate-after-eviction traffic.
10. physical free/min/peak/no-free/partial-allocation pressure.
11. IO HOL ready-younger metrics.
12. OO out-of-order retire, active Ref, reclaim, merge/wakeup metrics.
13. lower issue/outstanding and bandwidth/traffic proxies available from the source.

### Figure 4.2 category contract

The thesis categories are:

- Waiting instruction buffer full;
- Tag & Cacheline allocation failure;
- MSHR capacity failure;
- Miss Queue / downstream request-queue failure.

M5 must map actual source events into these categories. `TAG_BANK_CONFLICT` is **not silently treated as Tag & Cacheline allocation failure**. Keep arbitration conflicts as a separate diagnostic channel. If the existing source does not expose true Tag/cacheline allocation-vs-MSHR-vs-miss-queue reasons, add source-backed counters and directed tests.

Primary Figure-4.2 denominator:

`sum(primary paper-equivalent structural stall cycles for the four categories)`.

Also publish a full diagnostic denominator that includes Tag-bank/other pipeline stalls. If an unprojectable stall dominates execution, M5.0E must diagnose it before formal interpretation.

### Directed counter tests

Create deterministic cases that independently force and observe:

- PIB full;
- Tag/cacheline allocation failure;
- MSHR entry/merge capacity failure;
- miss queue/lower-capacity failure;
- Tag-bank arbitration conflict;
- concurrent-miss create/complete lifecycle.

Require exact conservation and no double counting of the primary reason.

### Acceptance

- All paper-equivalent metrics have one common definition across modes.
- Figure-4.7 create/complete counts close exactly and current live count drains to zero.
- Figure-4.2 directed cases hit the intended source reason and primary categories reconcile exactly.
- Strict parser schema includes all required fields.
- Instrumentation does not alter timing on sentinel differentials unless a previously incorrect behavior is deliberately repaired and revalidated.

### Handoff to M5.0E

`handoffs/M5_0D_METRICS.md` freezes metric formulas, source event anchors, parser schema version, directed-test results, and plot-column names.

---

## M5.0E — Pilot behavior/fidelity triage

Run Base/IO/OO on at least these sentinels before launching all formal experiments:

- ATAX: known M4 resource pressure and speedup;
- SpMV: thesis high-benefit case whose current M4 input did not fill PIB;
- 2MM: thesis high-benefit cache-inefficient workload;
- Conv2D: compute-intensive contrasting case.

For each, emit:

- speedup;
- Base Figure-4.2 structural-stall breakdown;
- average concurrent misses;
- PIB/MSHR/Tag/physical/downstream pressure;
- DTC request traffic and duplicate ratio;
- IO HOL / OO OOO-retire evidence.

### Performance anomaly classification

A surprising slowdown or missing benefit is not a Goal stop. Apply `M5_PROBLEM_RESOLUTION_POLICY.md` and classify:

1. **Implementation/modeling**: Base has intended pressure but DTC does not remove it or common service differs incorrectly.
2. **Workload/input fidelity**: Base never reaches the paper-discussed bottleneck, launch/input scale is too small, or algorithm/input mapping is wrong.
3. **Downstream/platform**: DTC increases concurrent misses but performance is capped by L2/NoC/DRAM/natural outstanding limits.
4. **Traffic side effect**: duplicate/new traffic offsets latency hiding.
5. **Genuine mechanism limitation**: implementation and workload are sound but this application does not benefit.

Do not tune parameters to force a positive result.

### Acceptance

- Every sentinel is correctness-clean.
- Each surprising result has a documented root-cause classification, not just a speedup number.
- SpMV paper-equivalence is not accepted while it still trivially underutilizes Base PIB without a source/input explanation.
- No known implementation fidelity issue remains open before FORMAL Figure runs.

### Handoff to M5.1

Create `review_packs/M5_0_FIDELITY_LOCK/` and `handoffs/M5_0E_FIDELITY_PASS.md`, naming the frozen FORMAL behavior SHA and exact ten-workload set. After this handoff, continue automatically to M5.1.

---

# M5.1 — Figure 4.2 Baseline Motivation

## M5.1A — Counter mechanism proof

Reuse M5.0D directed tests and add any workload-level sanity needed to prove the four thesis structural categories reflect actual Base source stalls.

### Acceptance

- Primary paper-equivalent categories are mutually exclusive per counted stall cycle.
- Their sum equals the paper-equivalent structural-stall total.
- Full diagnostic stalls reconcile with paper-equivalent + Tag-bank/other categories.
- No category is inferred from a performance result.

## M5.1B — Ten-compute Base formal runs

Configuration:

- PAPER_BASE;
- L1 16KB, 128B, 4-way;
- PIB 8;
- MSHR 32;
- frozen common formal config.

Run all ten compute workloads.

Outputs:

- per-workload four-category fractions;
- AVG/GM-GP descriptive aggregate where meaningful;
- full diagnostic stall table;
- raw counts and total stall cycles.

### Acceptance

- All ten output/provenance checks pass.
- All primary stall cycles reconcile.
- If thesis-discussed high-spatial-locality workloads do not show meaningful PIB pressure, diagnose workload/input/config before accepting the figure.
- **Do not require** the thesis averages 79% / 6.5% / 2.1% as pass thresholds; compare them after the mechanism is established.

### Handoff to M5.2

Create:

- `generated/m5_fig4_2_stalls.csv`;
- `analysis/M5_FIG4_2_INTERPRETATION.md`;
- `handoffs/M5_1_FIG4_2.md`.

The handoff must state which bottleneck categories dominate each workload and which differences from the thesis are attributed to workload/platform rather than implementation.

---

# M5.2 — Figures 4.5 + 4.7 Main Mechanism Result

Treat performance and concurrent misses as one coupled experiment. Do not publish a speedup bar without the miss-concurrency explanation.

## M5.2A — Ten Base/IO/OO formal triplets

Use the common defaults from section 0.1.

Run all ten compute workloads under PAPER_BASE, PAPER_IO, PAPER_OO. Reuse valid M5.1 Base results if the exact formal identity matches.

Required per-run outputs:

- cycles;
- dynamic op counts;
- output/self-check;
- avg/peak live concurrent misses;
- Base structural stalls;
- PIB occupancy/full;
- DTC valid/pending/new-miss;
- lower traffic/duplicate ratio;
- physical pressure;
- IO HOL;
- OO OOO retire/Ref/reclaim/merge.

## M5.2B — Formal performance aggregation

Produce thesis-style per-workload bars normalized to Base=1.

Compute:

- GM-CE over the seven cache-efficient compute workloads;
- GM-GP over all ten compute workloads;
- do **not** compute GM-ALL-PAPER yet.

The thesis +22%/+30% values are reference points only, not acceptance thresholds.

## M5.2C — Figure 4.7 concurrent-miss aggregation

Plot the frozen `avg_concurrent_misses_per_sm` for Base/IO/OO per workload and a compute aggregate.

Also compute:

- IO/Base concurrent-miss ratio;
- OO/IO ratio;
- speedup vs concurrent-miss increase correlation;
- traffic increase vs concurrent-miss increase.

### Acceptance

- Triplet dynamic op counts and workload identity match exactly.
- All memory ownership/accounting drains.
- Common live-miss counters conserve create==complete and current==0.
- Any workload with weak/negative speedup has a completed mechanism diagnosis according to M5.0E; it is not hidden or tuned away.
- Where Base structural pressure is high, either DTC increases concurrent misses or an implementation/platform root cause is established and resolved/documented.
- OO-vs-IO differences are interpreted using HOL/OOO-retire evidence, not assumed from label alone.

### Handoff to M5.3

Create:

- `generated/m5_fig4_5_performance.csv`;
- `generated/m5_fig4_7_concurrent_misses.csv`;
- `analysis/M5_MAIN_RESULT_CAUSAL.md`;
- `handoffs/M5_2_MAIN_RESULT.md`;
- `review_packs/M5_2_MAIN_RESULT/`.

The handoff must identify workload classes: Base-PIB-limited, Tag/line-limited, MSHR-limited, downstream-limited, compute-bound, and DTC-traffic-sensitive.

---

# M5.3 — Figure 4.8 Logical Cache Sensitivity

Primary thesis-style DTC sweep:

- logical size: 16KB, 32KB, 64KB;
- physical size: 80KB fixed;
- IO PIB 256, OO PIB 128;
- all other common defaults fixed;
- variants: PAPER_IO and PAPER_OO;
- ten compute workloads first.

Convert logical capacity by set count while keeping line size=128B and ways=4 unless source constraints require an equivalent parameterization:

- 16KB -> 32 sets x 4 ways;
- 32KB -> 64 sets x 4 ways;
- 64KB -> 128 sets x 4 ways.

Normalize each workload to the same variant's 16KB result for the Figure-4.8-style sensitivity statement. Emit per-workload and GM-CE/GM-GP.

### Supplemental Base capacity control

Run PAPER_BASE 16/32/64KB on the same ten workloads if the source supports clean capacity changes. This is not part of the Figure-4.8 bar set but strengthens the thesis claim that DTC is less sensitive to logical cache capacity than a conventional L1.

### Acceptance

- Only logical capacity changes inside each sweep family.
- Tag-bank mapping remains valid at all set counts.
- No change in physical capacity, PIB, lower limits, or workload identity.
- Performance trends are explained jointly with miss/new-miss rate and concurrent misses.
- If a larger logical cache materially hurts performance, diagnose Tag mapping/traffic/platform rather than discarding the point.

### Handoff to M5.4

Create `generated/m5_fig4_8_logical_sweep.csv`, optional `m5_base_capacity_control.csv`, `analysis/M5_LOGICAL_SENSITIVITY.md`, and `handoffs/M5_3_LOGICAL.md`.

---

# M5.4 — Figure 4.9 Physical Cache Sensitivity / Release Mechanism

This experiment is compute-only in the thesis and therefore maps directly to the ten-compute M5 set.

Fixed:

- logical cache = 16KB;
- IO PIB = 256;
- OO PIB = 128;
- line = 128B;
- all unrelated configuration fixed.

Physical sizes from the thesis Figure 4.9 legend:

| Physical KB | Lines @ 128B |
| ---: | ---: |
| 16.5KB | 132 |
| 24KB | 192 |
| 32KB | 256 |
| 40KB | 320 |
| 48KB | 384 |

Variants: PAPER_IO and PAPER_OO.

Normalize each workload/config to that workload's **IO 32KB** result before cross-workload aggregation, matching the thesis normalization statement.

Required mechanism outputs:

- cycles / normalized performance;
- physical allocated/free/minimum;
- no-free events;
- partial-allocation entries/lines held;
- Tag evictions;
- IO release count / HOL;
- OO immediate/deferred/final-ref reclaim and active refs;
- watchdog/deadlock classification.

### Deadlock handling

The IO passive-release deadlock must emerge naturally. Never add a recovery path or special-case capacity.

A confirmed resource deadlock is represented in raw data as `EXPECTED_RESOURCE_DEADLOCK` / no numeric performance. A paper-style visualization may show a zero-height labeled DEADLOCK bar, but CSV must preserve the nonnumeric classification so it cannot be confused with a completed zero-performance run.

### Acceptance

- IO and OO use identical capacities at each point.
- Any deadlock is proven by physical/partial-allocation/FIFO no-progress evidence, not a timeout alone.
- OO reclaim invariants stay exact.
- The analysis establishes whether IO is more sensitive than OO and ties the difference to passive vs active release; exact 24KB/16.5KB cliff locations are reference trends, not hard thresholds under a different simulator/workload set.
- If no paper workload deadlocks at 16.5KB, retain the valid result and use pressure counters plus the already-validated directed deadlock mechanism; do not tune workload or architecture solely to force a zero bar.

### Handoff to M5.5

Create `generated/m5_fig4_9_physical_sweep.csv`, `analysis/M5_PHYSICAL_RELEASE.md`, and `handoffs/M5_4_PHYSICAL.md`.

---

# M5.5 — Figure 4.10 PIB Sensitivity / IO-vs-OO Retirement

Fixed as stated in the thesis:

- logical cache = 16KB;
- physical cache = 32KB / 256 lines;
- all unrelated configuration fixed.

Sweep DTC PIB entries:

`32, 64, 128, 192`

for PAPER_IO and PAPER_OO over the ten compute workloads.

Normalize each workload/config to that workload's **IO 128-entry** result before cross-workload aggregation.

Optional diagnostic only: IO=256 may be run to verify saturation because 256 is the primary implementation default, but it must not be inserted into the thesis Figure-4.10 reproduction bars.

Required mechanism outputs:

- cycles;
- PIB average/peak/full;
- IO head-not-ready/HOL-ready-younger;
- OO OOO-retire count;
- average concurrent misses;
- lower traffic;
- physical pressure.

### Acceptance

- PIB depth is the only mechanism knob changed within each sweep family.
- IO/OO retirement width remains 1 instruction/cycle.
- Analysis tests the thesis mechanism claim that OO is less PIB-capacity-sensitive because completed younger entries can retire/release independently.
- SpMV receives an explicit per-workload sensitivity report because the thesis cites it as strongly PIB-sensitive. If the resolved SpMV remains insensitive, explain the source/input/platform reason rather than selecting a different dataset by DTC speedup.
- Exact thesis declines (-16.2%, -2.06%, -32.7% SpMV) are comparison references, not pass thresholds.

### Handoff to M5.6

Create `generated/m5_fig4_10_pib_sweep.csv`, `analysis/M5_PIB_HOL.md`, and `handoffs/M5_5_PIB.md`.

---

# M5.6 — Integrated Causal Analysis

This stage should reuse prior formal runs and avoid unnecessary simulator reruns.

Required analyses:

1. speedup vs increase in average concurrent misses;
2. speedup vs Base Figure-4.2 structural bottleneck fractions;
3. OO-vs-IO speedup vs IO HOL / OO out-of-order retire evidence;
4. physical-capacity performance vs free-line/no-free/reclaim pressure;
5. PIB-capacity performance vs PIB-full/HOL/concurrent-miss pressure;
6. DTC duplicate/lower-traffic increase vs benefit;
7. downstream saturation cases where concurrent misses rise but performance does not.

Produce a per-workload causal classification rather than one global explanation.

### Optional diagnostic ablation

If source/config permits without inventing new semantics, run a small non-paper ablation set on representative workloads:

- conventional Base with PIB enlarged while MSHR remains 32;
- conventional Base with PIB enlarged and MSHR enlarged;
- full DTC IO/OO.

This can separate PIB-only, MSHR, and Tag/physical effects. It is DIAGNOSTIC and must not be mixed into Figures 4.2-4.10.

### Acceptance

- Every major positive/negative performance result has a mechanism explanation backed by counters.
- No causal claim relies on a single peak metric when a cycle-average is available.
- Genuine mechanism limitations are retained, not tuned away.

### Handoff

Create `analysis/M5_CAUSAL_SYNTHESIS.md`, `generated/m5_workload_classification.csv`, and `review_packs/M5_6_CAUSAL/`.

---

# M5.G — Graphics Preparation in Parallel (nonblocking for compute)

Graphics preparation starts during M5.0 and proceeds independently. It must not delay the ten-compute path.

Thesis graphics set and settings:

- `jellyfish`: 13200 vertices, two 256x256 textures, 800x600;
- `cat-tex`: 43044 vertices, 512x512 texture, 800x600;
- `cube-tex`: 36 vertices, 512x512 texture, 800x600;
- `2D-tex`: 4 vertices, 128x128 texture, 256x256;
- `horse`: 21516 vertices, no texture, 800x600.

See `M5_GRAPHICS_PREP.md` for the detailed handoff.

Until a source-backed graphics execution path exists, do not compute `GM-ALL-PAPER` or claim direct glmark2 FPS reproduction.

---

# M5.7+ — Supplemental studies only after paper-mode compute closeout

These are not prerequisites for Figures 4.2-4.10:

- equal-storage/equal-area-oriented conventional L1 controls;
- `MODERN_OO_SECTOR` vs whole-line PAPER_OO;
- 16-vs-32 coalescer-width robustness;
- downstream outstanding/issue-width sensitivity;
- DTC-native no-Tag policy bypass from thesis Section 4.4, distinct from M4 architectural `.cg` bypass;
- area reconstruction/synthesis track.

Each extension must use separate labels and cannot overwrite paper-mode results.

---

# Continuous Goal progression

After user approval, the intended single persistent Goal is:

`M5.0 Fidelity Lock -> M5.1 Fig4.2 -> M5.2 Fig4.5+4.7 -> M5.3 Fig4.8 -> M5.4 Fig4.9 -> M5.5 Fig4.10 -> M5.6 Causal Synthesis -> M5_COMPUTE_READY_FOR_REVIEW`

Graphics preparation proceeds concurrently as a nonblocking side track.

At every substage, apply `M5_PROBLEM_RESOLUTION_POLICY.md`: ordinary missing workloads, build failures, assertions, counter gaps, timeouts, unexpected bottlenecks, or poor performance are **resolve-in-goal problems**, not automatic stop conditions.

Only researcher-decision boundaries that cannot be resolved from source/thesis evidence may pause the Goal. M5 execution is not authorized by this draft alone.
