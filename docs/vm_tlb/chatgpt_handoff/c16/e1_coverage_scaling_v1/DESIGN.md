# C16 E1 Fixed-Budget Protected-Coverage Scaling Design V1

## 1. Purpose

The shared-residency stage proved two facts at the same time:

1. multiple selected qweight-backed modules can remain materially faster under one fixed persisting-L2 budget;
2. protecting only three modules improves full decode by less than 0.5%.

The second fact is currently dominated by coverage: those three modules occupy only about 1.74% of a stable decode step.

This stage therefore asks:

> As the protected up_proj coverage expands from one layer to all 28 layers while the total persisting-L2 budget stays fixed, how do local retention, Amdahl opportunity, and full-decode benefit scale?

No simulator is run in this stage.

---

## 2. Frozen hardware/runtime authority

Model:
`Qwen/Qwen2.5-7B-Instruct`

Deployment:
accepted AWQ full-model path.

Input:
accepted S2_TEXT 2048-token prefix.

Decode:
exactly four deterministic greedy steps.

Expected accepted tokens:
`[23578, 11, 323, 3950]`

GPU:
RTX4080.

Fixed requested persisting-L2 set-aside:
`33,947,648 B`

Expected runtime query-back:
`37,748,736 B`

Every fixed-budget coverage condition must preserve both values.

No package, driver, backend, dtype, model revision, tokenizer, or kernel implementation change is allowed.

---

## 3. Stage A — full FFN opportunity census

Before changing protection coverage, measure where decode time actually goes.

### Modules

For every layer 0..27, census:

- `mlp.gate_proj`
- `mlp.up_proj`
- `mlp.down_proj`

Runtime must independently verify:
- all 28 layers exist;
- each requested module exists;
- module class/backend;
- qweight presence/shape/bytes/contiguity.

If one role is not an accepted AWQ qweight-backed module family, mark that role unsupported rather than silently substituting another operator.

### Native census

Condition:
`CENSUS_FFN_NO_PERSIST`

- no persisting window;
- no persisting set-aside;
- 7 fresh processes;
- accepted token/SHA sequence;
- CUDA events around every requested FFN projection occurrence;
- no inner-loop synchronize;
- decode-step timing D0-D3.

Resolve event times only after the normal step/run completes.

### Opportunity metrics

For each stable decode D1-D3 and each fresh run compute:

- sum of all 28 up_proj times / decode-step time;
- sum of all 28 gate_proj times / decode-step time;
- sum of all 28 down_proj times / decode-step time;
- sum of all 84 FFN-projection times / decode-step time.

Also report by role:
- per-layer median timing;
- layer distribution;
- top-1 / top-4 share;
- min / median / max.

These are measured execution-time shares, not causal speedup predictions.

---

## 4. Layer-selection order for nested up_proj coverage

Primary scaling uses only `up_proj` so operator/backend/qweight geometry remains homogeneous.

Freeze this deterministic layer order:

`[0, 14, 27, 7, 20, 3, 10, 17, 23, 5, 12, 25, 1, 2, 4, 6, 8, 9, 11, 13, 15, 16, 18, 19, 21, 22, 24, 26]`

This order begins with already accepted anchors 0 and 14, then expands by a deterministic farthest-from-selected rule.

Primary prefix counts:

- N1
- N2
- N4
- N8
- N14A
- N28

Exact sets:

- N1 = first 1
- N2 = first 2
- N4 = first 4
- N8 = first 8
- N14A = first 14
- N28 = all 28

Composition holdout:

- N14B = the complement of N14A.

N14A and N14B are separate same-count layer-composition controls.

No layer set is selected after observing timing data.

---

## 5. Stage B — primary FAIR fixed-budget coverage scaling

For every layer set S with size N:

### CONTROL_S

- fixed requested set-aside = 33,947,648 B;
- runtime query-back must equal 37,748,736 B;
- before each selected layer's up_proj in PREFILL and D0-D3:
  - issue the exact full-qweight window update;
  - hitRatio field = `1/N`;
  - hitProp = NORMAL;
  - missProp = NORMAL;
  - target_persisting = false;
- no persistence is active.

### FAIR_S

Identical API update schedule and budget, except each selected layer's up_proj update is:

- full exact qweight window;
- hitRatio = `1/N`;
- hitProp = PERSISTING;
- missProp = STREAMING.

Important:

`1/N` is a CUDA policy hint only.
It is not interpreted as exactly 1/N of lines or bytes being retained.

### In-run policy lifetime

- reset before the whole condition;
- no persisting-L2 reset between selected layers/tokens;
- reset after the whole condition.

### Native repetitions

For every CONTROL/FAIR condition:

- 7 fresh processes;
- exact prefix/token sequence;
- all 28 up_proj occurrence input/output SHA values frozen and checked;
- time all 28 up_proj calls, selected and non-selected;
- time D0-D3 decode steps;
- record every policy update and CPU update duration.

Timing all 28 up_proj calls in every condition keeps event instrumentation constant across N.

### Primary comparisons

Every FAIR_S is compared only against its matched CONTROL_S.

Do not compare FAIR_N directly against CONTROL_M with M != N.

---

## 6. Coverage/Amdahl accounting

For every set S and stable D1-D3, compute from run-aligned raw data:

### SELECTED_TARGET_SHARE

`sum(control selected-up_proj time) / control decode-step time`

This is the measured Amdahl ceiling if the selected modules became zero-time.

### SUMMED_LOCAL_SAVING

`sum(control selected-up_proj time - fair selected-up_proj time)`

### OBSERVED_DECODE_SAVING

`control decode-step time - fair decode-step time`

### REALIZATION_RATIO

`OBSERVED_DECODE_SAVING / SUMMED_LOCAL_SAVING`

when the denominator is positive.

Do not clamp the ratio.

Also compute:

- non-selected up_proj aggregate timing effect;
- selected-layer material-benefit fraction;
- median/P25/P75/min/max selected-layer timing benefit;
- API-overhead total per run;
- decode benefit versus selected target share.

This stage must explicitly distinguish:

1. limited coverage;
2. local-benefit dilution as N grows;
3. failure of local savings to realize at whole-decode level.

---

## 7. Local materiality

For each selected layer at D3:

`MATERIAL_LOCAL`

if:
- FAIR timing is at least 5% lower than matched CONTROL;
- effect exceeds combined timing dispersion.

For each coverage set report:

- material selected-layer count;
- material selected-layer fraction.

No requirement that every layer pass.

---

## 8. Whole-decode materiality and stage labels

Stable decode uses D1-D3.

For each S compute the run-level stable mean:
`mean(D1,D2,D3)`

Whole-decode effect is FAIR_S versus matched CONTROL_S.

A point is statistically/materially positive if:
- benefit > combined dispersion;
- benefit > 0.

The stage-level N28 label is:

### COVERAGE_SCALING_SYSTEM_RELEVANT
- N28 whole-decode benefit >= 2%;
- benefit > combined dispersion.

### COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD
- N28 whole-decode benefit > combined dispersion;
- benefit > 0;
- benefit < 2%.

### COVERAGE_SCALING_LOCAL_BUT_NOT_SYSTEMIC
- N28 whole-decode benefit is not materially positive;
- but at least 50% of selected N28 layers retain MATERIAL_LOCAL.

### COVERAGE_SCALING_NOT_SUPPORTED
- N28 whole-decode benefit is not materially positive;
- and fewer than 50% of selected N28 layers retain MATERIAL_LOCAL.

### POLICY_SCALING_UNQUALIFIED
- policy/runtime/semantic identity cannot be qualified.

The previous shared-stage label remains frozen separately.

---

## 9. Stage C — N14 composition holdout

Compare N14A and N14B descriptively:

- selected target share;
- median local benefit;
- material-layer fraction;
- whole-decode benefit;
- realization ratio.

No winner/ranking is needed.

Purpose:
ensure the coverage curve is not an artifact of choosing one favorable half of the layers.

---

## 10. Stage D — bounded critical-path scaling profiles

Reuse the accepted runtime-resolved NCU metrics:

Required base:
- `l1tex__t_bytes.sum`
- `lts__t_bytes.sum`
- `dram__bytes.sum`

Accepted critical-path categories when still available:
- kernel duration;
- L2 read hit sectors;
- L2 read miss sectors;
- DRAM read bytes;
- long-scoreboard stall;
- LSU utilization;
- active warps.

Re-query exact metric availability/version before use.

Profile D3 only.

Primary points:

### Layer0 up_proj
- CONTROL_N1 / FAIR_N1
- CONTROL_N8 / FAIR_N8
- CONTROL_N28 / FAIR_N28

### Layer14 up_proj
- CONTROL_N2 / FAIR_N2
- CONTROL_N8 / FAIR_N8
- CONTROL_N28 / FAIR_N28

### Layer27 up_proj
- CONTROL_N4 / FAIR_N4
- CONTROL_N28 / FAIR_N28

Maximum primary profiles: 16.

Use:
- application replay;
- cache-control none;
- exact semantic occurrence;
- complete policy history before selected occurrence.

Aggregation:
- additive bytes/sectors/cycles only where category semantics allow;
- stall/utilization/occupancy remain per-kernel.

Purpose:
measure whether local critical-path benefit degrades as protected coverage increases.

---

## 11. Stage E — conditional unpartitioned-intent control

The FAIR policy explicitly reduces hitRatio as N grows.
The proposed future elastic quota does not pre-partition an exact equal share per target.

Therefore a bounded secondary control is preauthorized only if:

- N28 FAIR selected-layer material fraction >= 0.50;
- and N28 whole-decode benefit is < 2%.

Then run:

### CONTROL_FULL_N8
- same N8 update schedule;
- NORMAL/NORMAL;
- hitRatio field = 1.0.

### FULLHINT_N8
- same N8 update schedule;
- all selected windows PERSISTING;
- hitRatio = 1.0.

### CONTROL_FULL_N28
- same N28 update schedule;
- NORMAL/NORMAL;
- hitRatio = 1.0.

### FULLHINT_N28
- same N28 update schedule;
- all selected windows PERSISTING;
- hitRatio = 1.0.

The set-aside remains fixed at one full-qweight request.

Interpretation:

- this intentionally over-subscribes the persisting intent;
- it does not imply all target lines can fit;
- it tests whether the FAIR 1/N hint is itself limiting the observed coverage curve.

Native:
7 fresh processes per condition.

NCU:
if FULLHINT_N28 changes whole-decode benefit by >=0.5 percentage points versus FAIR_N28, profile L0/L14 D3 CONTROL_FULL_N28 vs FULLHINT_N28.

---

## 12. No simulator in this stage

This stage does not:

- run Accel-Sim;
- mutate GPGPU-Sim;
- capture NVBit/full address traces;
- implement ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1.

The simulator mechanism remains a design candidate only.

The coverage curve decides whether a simulator implementation is worth authorizing.

---

## 13. 109 review pack

Create:

`docs/vm_tlb/review_packs/C16_E1_COVERAGE_SCALING_109_V1/`

At minimum:

- `UPSTREAM_AUTHORITY.json`
- `FFN_OPPORTUNITY_CENSUS_CONTRACT.json`
- `FFN_OPPORTUNITY_CENSUS.tsv`
- `FFN_OPPORTUNITY_ANALYSIS.json`
- `LAYER_SELECTION_MANIFEST.json`
- `COVERAGE_POLICY_CONTRACT.json`
- `COVERAGE_NATIVE_TIMING.tsv`
- `COVERAGE_DECODE_STEP_TIMING.tsv`
- `COVERAGE_POLICY_OVERHEAD.tsv`
- `COVERAGE_SCALING_ANALYSIS.json`
- `N14_COMPOSITION_HOLDOUT.json`
- `COVERAGE_NCU_INDEX.tsv`
- `COVERAGE_CRITICAL_PATH_ANALYSIS.json`
- `FULLHINT_TRIGGER_DECISION.json`
- `FULLHINT_ANALYSIS.json`
- `STAGE_DECISION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Preserve all raw native/NCU/policy evidence.

Update the scientific log.

---

## 14. 174-new parallel role

174-new should execute one large CPU-only Goal:

1. independently close the already completed shared-residency producer using raw evidence;
2. apply the latest shared-consumer hardening;
3. freeze the coverage-scaling consumer contract before coverage producer data is available;
4. implement opportunity/Amdahl/coverage/fullhint consumers and synthetic tests;
5. audit the accepted RTX4080 simulator platform authority and historical C12 cross-layer evidence;
6. fetch the coverage producer once after prep and consume if available;
7. otherwise stop READY.

No simulator run.

---

## 15. Next-step authorization after closure

Only after 109 + independent 174 closure may ChatGPT choose among:

- `AUTHORIZE_BOUNDED_TRACE_AND_FIRST_SIMULATOR_MECHANISM`
- `EXPAND_OPERATOR_FAMILY_BEFORE_SIMULATOR`
- `STOP_RESIDENCY_MECHANISM_SYSTEM_CASE_WEAK`
- `REVIEW_REQUIRED`

Neither producer nor consumer auto-authorizes simulator implementation.
