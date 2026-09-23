# C16 E1 Shared-Residency Mechanism Feasibility Design V1

## 1. Project-level review decision

The producer and strict consumer labels remain frozen and are not overwritten.

Project-level action for this stage:

`DESIGN_REVIEW_AUTHORIZED_WITH_TRAFFIC_CAVEAT`

This authorizes:
- mechanism design review;
- bounded real-hardware feasibility experiments;
- simulator/code-path mapping.

It does **not** authorize:
- a paper claim that traffic is target-specific;
- full NVBit/address tracing;
- Accel-Sim mechanism implementation;
- mechanism performance simulation.

Rationale:
- raw evidence independently matches;
- isolated policy efficacy is strong;
- natural target timing benefits are large and target-specific;
- all abstract mechanism-requirement dimensions are descriptively supported;
- the strict consumer gate failed only because the frozen DRAM threshold did not pass.

The traffic caveat remains mandatory.

---

## 2. Scientific questions

### Q1 — latency/traffic decoupling

Why does target persistence yield a large target-specific timing benefit while aggregate semantic DRAM bytes are not target-specific?

### Q2 — shared budget

Can one fixed persisting-L2 budget be shared across multiple compressed qweight regions while retaining material local benefits?

### Q3 — end-to-end relevance

Can shared persistence improve full decode-step latency, not just one selected module?

### Q4 — mechanism shape

What minimum hardware abstraction is justified by the evidence:
- protected quota?
- static reservation?
- elastic protected quota?
- replacement priority?
- software/PC/region identity?

---

## 3. Part A — exact critical-path NCU diagnosis

### Target points

Primary:
- L0 up D3
- L14 up D3
- L0 down D3

Conditions:
- SETASIDE_ONLY
- PERSIST_TARGET
- PERSIST_MATCHED_UNRELATED

For L0 up D3 additionally include:
- BASELINE

Maximum:
- L0 up: 4
- L14 up: 3
- L0 down: 3
= 10 profiles.

### Metric discovery

Before profiling, query installed NCU metric availability.

Do not hard-code metric names from another NCU release.

Resolve exact available metric names/units for these categories where supported:

1. kernel duration / elapsed cycles;
2. L2 read lookup hit sectors or hit rate;
3. L2 read miss sectors;
4. DRAM read sectors/bytes;
5. long-scoreboard / memory-dependency stall;
6. memory-pipe or LSU utilization;
7. achieved active-warps / occupancy as a secondary control.

Required:
- exact metric name
- unit
- NCU query receipt

If one category is unavailable, record unavailable; do not invent a substitute formula.

### Per-kernel interpretation

AWQ semantic module has GEMM + reduction.

Do not aggregate percentages blindly.

For additive sectors/bytes/cycles where semantically additive, preserve:
- per-kernel values
- semantic sum.

For percentages/stall fractions:
- preserve per-kernel only unless NCU documents an aggregation.

Primary diagnostic:
- identify whether the timing benefit is concentrated in GEMM or reduction;
- determine whether target persistence changes L2-hit behavior or memory-stall behavior more strongly than total DRAM bytes.

No cache-causality claim beyond the measured policy intervention.

---

## 4. Part B — rotating-window persistence qualification

CUDA stream access-policy exposes one active window at a time.

Before full-model shared-budget experiments, qualify whether lines previously accessed as persisting remain useful after the stream window is changed to another qweight region without resetting the persisting-L2 state.

### Isolated two-region sequence

Use exact standalone M1 AWQ modules:

- A = L0 up qweight/module
- B = L14 up qweight/module

Sequence under one full persisting-L2 set-aside:

1. reset;
2. set window A with hitRatio 0.5;
3. execute A twice;
4. switch window B with hitRatio 0.5, no reset;
5. execute B twice;
6. switch window back to A with hitRatio 0.5, no reset;
7. profile/measure A.

Matched control:
- perform the same window-switch API calls but with a non-persisting/zero-hit policy supported by the local runtime.

If hitRatio=0 on a persisting window is unsupported or semantically ambiguous, extend helper with exact `cudaAccessPropertyNormal` control after inspecting local headers.

Record:
- API switch latency on CPU;
- requested/actual set-aside;
- window transitions;
- no reset between A/B/A;
- exact target identity.

NCU target A:
- L1/L2/DRAM base metrics;
- critical-path metric subset from Part A if qualified.

This part only qualifies the rotating-window experiment.
It is not itself the final mechanism result.

---

## 5. Part C — shared fixed-budget natural full-model experiment

Use accepted:
- Qwen2.5-7B AWQ;
- S2_TEXT 2048-token prefix;
- D0-D3 tokens;
- exact occurrence SHA authority.

### Fixed global budget

Use one full-qweight requested set-aside:
`33,947,648 B`
with runtime actual query-back preserved.

The total set-aside is held constant across all shared conditions.

### Conditions

#### SETASIDE_ONLY
Existing matched reservation control.

#### ROTATE_CONTROL_3
At the same selected module boundaries as SHARE3:
- perform same number/order of stream-policy updates;
- no data is marked persisting.

This isolates host/API-switch overhead.

#### SINGLE_L0_UP
- L0 up window
- hitRatio 1.0

Re-run only if needed for exact same rotating harness; existing single-target authority remains a comparison reference.

#### SHARE2_UP
Targets:
- L0 up
- L14 up

At each corresponding module invocation:
- set exact target qweight window;
- hitRatio 0.5.

Expected aggregate eligible bytes:
~ one qweight total across two regions.

#### SHARE2_L0
Targets:
- L0 up
- L0 down

Each:
- hitRatio 0.5.

#### SHARE3
Targets:
- L0 up
- L14 up
- L0 down

Each:
- hitRatio = 1/3.

The target qweight window remains the full exact qweight interval.
The total persisting-L2 set-aside remains fixed.

No reset between selected-module switches inside one full-model run.
Reset before and after each fresh-process condition.

### Native repetitions

For every new condition:
- 7 fresh processes;
- exact token/SHA closure;
- target occurrence timing for all 12 accepted occurrences;
- decode-step timing;
- full policy-switch receipts;
- CPU policy-switch overhead per update.

Primary:
- D1/D3 stable decode steps;
- L0 up D3
- L14 up D3
- L0 down D3

D0 remains secondary.

---

## 6. Part D — shared-budget NCU

Profile D3 only for the three selected targets.

Required conditions:

L0 up D3:
- SETASIDE_ONLY
- ROTATE_CONTROL_3
- SINGLE_L0_UP
- SHARE2_UP
- SHARE2_L0
- SHARE3

L14 up D3:
- SETASIDE_ONLY
- ROTATE_CONTROL_3
- SHARE2_UP
- SHARE3

L0 down D3:
- SETASIDE_ONLY
- ROTATE_CONTROL_3
- SHARE2_L0
- SHARE3

Maximum:
6 + 4 + 4 = 14 profiles.

Use:
- application replay
- cache-control none
- exact semantic selector

Required base metrics:
- L1/TEX bytes
- L2 bytes
- DRAM bytes

Also collect qualified critical-path metrics from Part A when replay cost remains bounded.

Every profile must preserve the complete policy transition receipt establishing the natural state before the selected occurrence.

---

## 7. Shared-policy analysis

### Local-retention benefit

For each target under a shared condition:

`LOCAL_TIMING_BENEFIT = timing(ROTATE_CONTROL_3) - timing(SHARED)`

normalized to ROTATE_CONTROL_3.

Material:
- >=5% lower;
- > combined dispersion.

### Whole-decode benefit

For stable D1-D3:

compare each shared condition against:
- SETASIDE_ONLY;
- ROTATE_CONTROL_3.

Define:
`MATERIAL_DECODE_BENEFIT`

if median step latency is:
- >=2% lower than ROTATE_CONTROL_3;
- and effect > combined dispersion.

The lower 2% threshold is intentional because the protected modules are a subset of a full decode step.

Report both absolute ms and percent.

### Multi-target retention

`MULTI_TARGET_RETAINED`

if at least two selected targets preserve material local timing benefit in the same shared condition.

### Policy-overhead accounting

Report:
- median CPU stream-policy update time;
- GPU decode-step effect;
- whether the API-control condition itself changes decode latency.

Do not claim a hardware mechanism speedup from host API overhead-contaminated results.

---

## 8. Stage-level outcomes

Allowed outcomes:

### SHARED_RESIDENCY_END_TO_END_SUPPORTED
Requires:
- rotating-window qualification PASS;
- MULTI_TARGET_RETAINED;
- MATERIAL_DECODE_BENEFIT vs ROTATE_CONTROL_3;
- semantic identity unchanged.

### SHARED_RESIDENCY_LOCAL_ONLY
Requires:
- multiple local target benefits;
- no material whole-decode benefit.

### SHARED_RESIDENCY_SINGLE_TARGET_ONLY
Only one target retains a material benefit under shared quota.

### ROTATING_WINDOW_POLICY_UNQUALIFIED
Window switching cannot preserve/establish valid persistence semantics or control overhead cannot be isolated.

### SHARED_RESIDENCY_NOT_SUPPORTED
Shared policy does not retain local benefits.

These labels do not override prior producer/consumer states.

---

## 9. Part E — mechanism design review on 174-new

CPU-side only.

Inspect the actual Accel-Sim/GPGPU-Sim code at the accepted repository state.

Identify exact implementation locations for:

- L2 cache line metadata;
- replacement state/update;
- cache insertion;
- eviction/victim selection;
- memory request fields available at L2:
  - address
  - PC
  - access type
  - warp/CTA/kernel identity where available.

Do not assume a field exists without code evidence.

### Candidate mechanisms

Evaluate at least:

#### M0 — static protected partition
- fixed protected ways/quota;
- tagged lines use protected space;
- simple but may waste capacity.

#### M1 — elastic protected quota
- protected lines may occupy up to quota;
- normal lines borrow unused protected capacity;
- when protected line arrives above pressure, normal lines are preferred victims;
- protected-vs-protected replacement remains recency-based.

#### M2 — priority insertion/eviction without hard partition
- target lines inserted at high priority;
- target lines demoted only after reuse/lifetime expiration;
- no dedicated ways.

For each:
- metadata bits;
- lookup path changes;
- replacement critical-path changes;
- expected area/control complexity qualitatively;
- mapping to measured 8/16/24/32/full budgets;
- failure modes.

### Identity source review

Separate:

1. Oracle/software-region tag:
   - exact qweight address interval;
   - strongest first simulator test;
   - not a final autonomous mechanism.

2. Static PC/signature:
   - requires stable load-PC relationship;
   - may need bounded trace evidence.

3. Dynamic reuse classifier:
   - highest complexity;
   - defer unless simpler mechanisms fail.

### Required design recommendation

Do not choose by novelty alone.

Select one **first simulator mechanism** based on:
- evidence fit;
- minimal implementation complexity;
- interpretable experiment;
- ability to separate residency-policy benefit from classifier quality.

The expected first simulator mechanism should normally use an oracle/software tag so the first experiment measures replacement-policy efficacy independently of detection accuracy.

No code implementation in this stage.

---

## 10. Simulator feasibility plan

174-new must output:

- exact source files/classes/functions to modify;
- exact new metadata/state;
- exact config knobs;
- baseline policies;
- required traces/workloads;
- whether existing trace format carries enough identity;
- if not, the minimum additional producer evidence needed.

If a bounded trace is needed later, specify the minimum trace scope.
Do not automatically authorize full trace.

---

## 11. 109 deliverables

Review pack:

`docs/vm_tlb/review_packs/C16_E1_SHARED_RESIDENCY_FEASIBILITY_109_V1/`

At minimum:

- `UPSTREAM_AUTHORITY.json`
- `CRITICAL_PATH_METRIC_AVAILABILITY.tsv`
- `CRITICAL_PATH_KERNEL_METRICS.tsv`
- `CRITICAL_PATH_ANALYSIS.json`
- `ROTATING_WINDOW_QUALIFICATION.json`
- `SHARED_POLICY_CONDITIONS.json`
- `SHARED_POLICY_NATIVE_TIMING.tsv`
- `SHARED_DECODE_STEP_TIMING.tsv`
- `SHARED_POLICY_NCU_INDEX.tsv`
- `SHARED_POLICY_ANALYSIS.json`
- `POLICY_SWITCH_OVERHEAD.tsv`
- `STAGE_DECISION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Raw evidence preserved.

---

## 12. 174-new deliverables

Review pack:

`docs/vm_tlb/review_packs/C16_E1_SHARED_RESIDENCY_DESIGN_REVIEW_174NEW_V1/`

At minimum:

- `UPSTREAM_DECISION_DIVERGENCE_AUDIT.json`
- `SHARED_EXPERIMENT_CONSUMER_CONTRACT.json`
- `CRITICAL_PATH_CONSUMER_CONTRACT.json`
- `CONSUMER_TESTS.tsv`
- `INDEPENDENT_SHARED_POLICY_ANALYSIS.json` when producer ready
- `ACCEL_SIM_L2_CODE_MAP.md`
- `MECHANISM_CANDIDATE_COMPARISON.md`
- `FIRST_SIMULATOR_MECHANISM_SPEC.md`
- `SIMULATOR_EXPERIMENT_PLAN.md`
- `TRACE_REQUIREMENT_DECISION.json`
- `FINAL_DESIGN_REVIEW.json`
- `NEXT_STEP_AUTHORIZATION.json`
- `SHA256SUMS`

---

## 13. Boundary

This stage does not authorize:
- full address trace;
- NVBit full-model capture;
- simulator code mutation;
- mechanism performance simulation.

The next stage may authorize a first simulator implementation only after:
- real-hardware shared-budget closure;
- design-review closure.
