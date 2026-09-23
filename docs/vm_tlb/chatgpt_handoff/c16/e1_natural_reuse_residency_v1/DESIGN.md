# C16 E1 Natural-Reuse / Residency Causal Closure Design V1

## 1. Scientific questions

This stage addresses three questions in one bounded package.

### Q1 — refill dynamics
After a controlled dense-memory perturbation, does an AWQ M1 target transition from a DRAM-heavy/slow first call back toward a DRAM-light/fast state over subsequent immediate reuses?

### Q2 — capacity knee
Does the pressure amount required to induce target DRAM refill align with the nominal residual-L2 budget:
`L2_bytes - target_module_state_bytes`
across q_proj/down_proj/up_proj?

### Q3 — natural reuse interval
Does the isolated WARM state survive the real interval between consecutive uses of the same module during full-model AWQ decode?

Q3 is the most architecture-relevant question.

No cache/TLB mechanism is designed in this stage.

---

# 2. Frozen authorities

Primary model family:
Qwen2.5-7B-Instruct / accepted RAW and AWQ deployments.

Reuse:
- accepted S2_TEXT input authority;
- accepted canonical same-input module authorities;
- accepted AWQ runtime/backend;
- accepted NCU semantic selector method;
- application replay + cache-control none.

No new model download.

---

# 3. Part A — post-pressure refill dynamics

## Targets

TEXT M1:

- q_proj RAW_FP16
- q_proj AWQ_FP16_INPUT
- down_proj RAW_FP16
- down_proj AWQ_FP16_INPUT
- up_proj RAW_FP16
- up_proj AWQ_FP16_INPUT

## State construction

For each point:

1. two target warmups;
2. DENSE_MEMORY_PRESSURE using the accepted 256 MiB pressure buffer;
3. synchronize;
4. execute six immediate target calls:
   `K1, K2, K3, K4, K5, K6`
   with no pressure or unrelated target call between them.

Target input bytes remain exactly unchanged across K1..K6.

## Native timing

- 9 independent sequence repetitions;
- CUDA-event time each K1..K6 separately;
- preserve all raw samples;
- record target input/output SHA;
- pressure outside timing.

Primary expected pattern for AWQ down/up:
- K1 slow;
- later K values recover toward warm timing.

RAW down/up control:
- much smaller K1→K6 change is expected because state exceeds L2.

q_proj is a fit-below-L2 control and may reveal implementation-specific retention behavior.

## Semantic NCU

For each of the six target points above, profile:
- K1
- K2
- K4

Metrics:
- l1tex__t_bytes.sum
- lts__t_bytes.sum
- dram__bytes.sum

Total:
`6 points × 3 call indices = 18 profiles`

Use application replay/cache-control none.

The exact replay must execute the dense pressure and preceding K calls before the selected Ki range.

No target kernel from another K may enter the selected range.

---

# 4. Part B — role-specific capacity-knee refinement

Use AWQ M1 only.

Nominal residual-L2 budgets:

- q_proj:
  `67,108,864 - 6,680,576 = 60,428,288 B ≈ 57.63 MiB`

- down_proj:
  `67,108,864 - 35,273,728 = 31,835,136 B ≈ 30.36 MiB`

- up_proj:
  same as down_proj.

These are hypotheses based on nominal capacity only, not exact effective cache capacity.

## Doses

### q_proj AWQ M1
`0, 32, 48, 56, 60, 64, 72, 96 MiB`

### down_proj AWQ M1
`0, 16, 24, 28, 32, 36, 48, 64 MiB`

### up_proj AWQ M1
`0, 16, 24, 28, 30, 32, 36, 40, 48, 64 MiB`

For every dose:
- two target warmups;
- dense-read exactly the prefix of the accepted pressure buffer;
- target timing;
- 7 repetitions.

## NCU

Collect target DRAM only:
`dram__bytes.sum`

for every listed AWQ dose.

The goal is to map refill onset with minimum profiler complexity.

Record:
- target DRAM bytes;
- target timing;
- ratio to 0-MiB state.

## Knee reporting

Do not force a hard “capacity theorem”.

For each role report:

- nominal residual-L2 budget;
- first dose where target DRAM exceeds:
  - 1 MiB absolute, and
  - 10% of module packed-state bytes;
- first dose where timing change is material under the existing 5%/dispersion rule;
- piecewise observed dose response.

Then compute:
`observed_dram_knee_mib - nominal_residual_l2_mib`

This delta is descriptive, not a pass/fail threshold.

---

# 5. Part C — natural full-model AWQ decode reuse interval

This is the primary architecture-realism stage.

## Full-model execution

Use the accepted Qwen2.5-7B AWQ deployment.

Input:
- accepted S2_TEXT 2048-token prefix.

Then perform exactly 4 deterministic greedy decode steps.

Freeze:
- decode token IDs;
- target module input SHA per occurrence;
- target module output SHA per occurrence.

Repeat the entire natural run in a fresh process and require the same token IDs and target SHA sequence before profiling.

## Target modules

Primary:
- layer0 `mlp.up_proj`

Held-out:
- layer14 `mlp.up_proj`

Additional semantic control:
- layer0 `mlp.down_proj`

For every decode occurrence assign a unique range name, e.g.:

- `C16_E1_NAT_L0_UP_D0`
- `C16_E1_NAT_L0_UP_D1`
- ...
- `C16_E1_NAT_L14_UP_D3`
- `C16_E1_NAT_L0_DOWN_D0`

Prefill is not part of the M1 target analysis.

## Native timing

Run 7 complete full-model executions.

Use CUDA events around each target module invocation without synchronizing inside the model loop; resolve event times only after the full run.

Report per occurrence:
- median/min/max/CV;
- target input/output SHA;
- token ID / decode index.

Also record full decode-step duration.

## Natural semantic NCU

Use application replay + cache-control none.

Profile:

### layer0 up_proj
- D0
- D1
- D3

### layer14 up_proj
- D0
- D3

### layer0 down_proj
- D0
- D3

Total:
`7 natural full-model profiles`

Collect:
- l1tex__t_bytes.sum
- lts__t_bytes.sum
- dram__bytes.sum

The whole model executes naturally outside the selected target range and therefore establishes the actual between-use interference state.

## Natural-vs-isolated classification

For each natural target occurrence, compare target DRAM/timing to accepted isolated references:

- isolated WARM;
- isolated DENSE_MEMORY_PRESSURE.

Define descriptive proximity:

`warm_fraction = |natural - warm| / |dense - warm|`

for DRAM and timing where denominator is nonzero.

Interpret:
- near 0: warm-like;
- near 1: dense-like;
- outside [0,1]: report as outside bracket; do not clamp.

No categorical threshold is required.

---

# 6. Optional RAW full-model natural control

Attempt only if the accepted RAW Qwen2.5-7B deployment can run the same 4-step full-model sequence on RTX4080 without:
- package changes;
- offload;
- changing dtype/backend;
- OOM repair tricks that alter execution.

If it runs naturally:
- native timing only for layer0 up_proj D0/D3;
- one NCU D0 profile is optional.

If it does not fit cleanly:
`RAW_FULL_MODEL_NATURAL_CONTROL_NOT_RUN_RESOURCE_BOUND`

Do not spend the Goal engineering around this optional control.

---

# 7. Part D — integrated interpretation

The stage should distinguish these possibilities.

### Case A — isolated refill + natural warm-like
The compressed target is repopulated quickly and remains resident across realistic decode reuse.

Implication:
current hardware already captures much of the residency benefit.

### Case B — isolated refill + natural dense-like
Immediate reuse repopulates the target, but natural inter-module interference evicts it before the next token occurrence.

Implication:
there may be architecture opportunity for selective/protected residency, but no mechanism is authorized yet.

### Case C — no clear refill dynamics
The intervention effect is not explained by simple target-state refill.

Implication:
do not proceed to residency mechanism.

### Case D — role-dependent
q/down/up differ materially even after accounting for size.

Implication:
kernel/access policy matters in addition to nominal capacity.

---

# 8. Cross-stage evidence requirements

The producer must preserve raw evidence for:
- every timing sample;
- every NCU BASE/SESSION/PROFILE artifact;
- every natural decode token;
- per-occurrence input/output SHA;
- exact kernel inventory;
- profiler commands.

No producer summary is accepted as independent-consumer authority.

---

# 9. 109 deliverables

Review pack:

`docs/vm_tlb/review_packs/C16_E1_NATURAL_REUSE_RESIDENCY_109_V1/`

At minimum:

- `UPSTREAM_AUTHORITY.json`
- `REFILL_SEQUENCE_CONTRACT.json`
- `REFILL_NATIVE_TIMING.tsv`
- `REFILL_NCU_INDEX.tsv`
- `REFILL_ANALYSIS.json`
- `CAPACITY_KNEE_CONTRACT.json`
- `CAPACITY_KNEE_TIMING.tsv`
- `CAPACITY_KNEE_NCU.tsv`
- `CAPACITY_KNEE_ANALYSIS.json`
- `NATURAL_FULL_MODEL_CONTRACT.json`
- `NATURAL_DECODE_TOKENS.json`
- `NATURAL_OCCURRENCE_BINDINGS.tsv`
- `NATURAL_NATIVE_TIMING.tsv`
- `NATURAL_NCU_INDEX.tsv`
- `NATURAL_VS_ISOLATED.json`
- `RAW_OPTIONAL_CONTROL.json`
- `INTEGRATED_INTERPRETATION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Update the living scientific log.

---

# 10. 174-new role

In parallel:

- audit this contract;
- independently implement refill-sequence analysis;
- implement capacity-knee analysis;
- implement natural occurrence/token identity consumer;
- extend raw NCU consumer for call-index and decode-occurrence identity;
- prepare isolated-reference comparison;
- synthetic tests;
- fetch producer once;
- if ready, consume raw evidence directly;
- otherwise stop at:
  `READY_FOR_E1_NATURAL_REUSE_RESIDENCY_109`

No GPU work.

---

# 11. Final boundary

No automatic:
- NVBit;
- full address trace;
- cache/TLB mechanism;
- mechanism simulation.

Only after producer + independent consumer closure may the project decide whether a residency mechanism is scientifically justified.
