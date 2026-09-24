# C16 E1 Residency Cost/Benefit Closure Design V1

## 1. Purpose

The operator-family stage shows that broad qweight persistence is not system-positive:
- only up_proj has repeatable local benefit;
- gate/down do not;
- pairwise/all-FFN expansion does not improve whole decode;
- a large negative accounting residual remains outside the measured FFN projection timings.

This stage performs one bounded real-hardware closure before deciding whether the residency mechanism line should continue.

Questions:

1. Can a smaller **global** persisting-L2 budget preserve enough up_proj benefit while reducing the offset elsewhere?
2. Which top-level model components account for the negative residual?
3. Does the residual look like self-attention, MLP-internal overhead, norms/final stages, or an unresolved timing/overlap effect?
4. Is there any budget point with >=2% whole-decode benefit?

No simulator is run.

---

## 2. Frozen model/runtime authority

Model:
`Qwen/Qwen2.5-7B-Instruct`

Deployment:
accepted AWQ full-model path.

Input:
accepted S2_TEXT 2048-token prefix.

Decode:
exactly four deterministic greedy steps.

Expected tokens:
`[23578, 11, 323, 3950]`

GPU:
RTX4080.

Protected object family:
all 28 `up_proj.qweight` regions only.

Gate/down are not protected in this stage.

---

## 3. Budget sweep

Test global requested persisting-L2 budgets:

- 8 MiB
- 16 MiB
- 24 MiB
- full-qweight request = 33,947,648 B

For each requested budget B:

- query and record runtime actual set-aside;
- require actual <= runtime max;
- preserve the exact query-back value in every fresh run of that budget.

Do not infer a universal alignment law from the returned values.

### Policy hint

There are 28 selected up_proj windows.

For each budget B define:

`hitRatio = min(1.0, B / (28 * qweight_bytes))`

where qweight_bytes is the exact accepted up_proj qweight size.

This keeps the aggregate persistence intent scaled with the tested global budget.

CUDA hitRatio is a policy hint only.
It is not an exact fraction of retained lines or bytes.

---

## 4. Matched condition matrix

For every budget B:

### CONTROL_UP28_B
- same requested set-aside B;
- same exact 28 up_proj update locations;
- same hitRatio;
- exact full qweight window;
- NORMAL/NORMAL;
- non-persisting.

### FAIR_UP28_B
- same requested set-aside B;
- same update locations;
- same hitRatio;
- exact full qweight window;
- PERSISTING/STREAMING.

Total:
8 native conditions.

Every condition:
- 7 fresh processes;
- reset before/after condition;
- no in-run persistence reset;
- exact model/token/backend identity.

No post-data budget selection.

---

## 5. Top-level residual decomposition

The previous operator-family stage timed all 84 FFN projections but not the rest of the layer.

This stage adds non-overlapping top-level semantic timing.

### Per-layer top-level modules

Runtime-discover and verify the actual Qwen layer structure.

Expected semantic categories to attempt:

- input_layernorm
- self_attn
- post_attention_layernorm
- mlp

Do not silently assume names if runtime differs.

For every layer 0..27 and D0-D3:

- time each discovered top-level category with CUDA events;
- do not inner-loop synchronize;
- resolve after the normal step/run completes.

### Final model stages

Also attempt to time, if directly hookable without changing execution:

- final model norm
- lm_head / output projection

If one stage cannot be isolated cleanly, mark it uninstrumented rather than guessing.

### Nested timing rule

MLP top-level timing contains gate/up/down and internal activation/multiply work.

Therefore:
- top-level categories are used for whole-step decomposition;
- gate/up/down child timings are used only for MLP-internal decomposition;
- never add MLP top-level timing to its child projection timings.

---

## 6. Keep all FFN child timing

In every budget condition continue timing all 84 FFN projections:

- gate_proj
- up_proj
- down_proj

For every occurrence preserve:
- layer
- role
- D0-D3 index
- input/output SHA
- module/backend identity
- timing.

This directly measures:
- protected up_proj saving;
- gate/down changes;
- MLP-internal residual.

---

## 7. Run-aligned accounting

For every budget and stable D1-D3, compute within each matched run:

### DIRECT_UP_SAVING
`sum(CONTROL up_proj - FAIR up_proj)`

### GATE_SAVING
`sum(CONTROL gate_proj - FAIR gate_proj)`

### DOWN_SAVING
`sum(CONTROL down_proj - FAIR down_proj)`

### TOTAL_FFN_PROJECTION_SAVING
sum of the three above.

### MLP_TOP_SAVING
`sum(CONTROL mlp_top - FAIR mlp_top)`

### MLP_INTERNAL_RESIDUAL
`MLP_TOP_SAVING - TOTAL_FFN_PROJECTION_SAVING`

### SELF_ATTN_SAVING
`sum(CONTROL self_attn - FAIR self_attn)`

### NORM_SAVING
sum directly measured layer norms.

### FINAL_STAGE_SAVING
final norm + lm_head/output when instrumented.

### OBSERVED_DECODE_SAVING
`CONTROL decode - FAIR decode`

### ACCOUNTED_TOPLEVEL_SAVING
sum of non-overlapping measured top-level categories:
- self_attn
- mlp_top
- norms
- final stages

### UNEXPLAINED_RESIDUAL
`OBSERVED_DECODE_SAVING - ACCOUNTED_TOPLEVEL_SAVING`

Do not clamp any ratio.

Do not call negative values cache slowdown unless the affected semantic category is directly measured.

---

## 8. Decomposition qualification

The top-level decomposition is considered qualified if:

- semantic module call identities are stable across all fresh runs;
- no top-level timing ranges overlap other top-level ranges within the same layer/step;
- every timed category has exact one-occurrence-per-layer/step identity where expected;
- the absolute median UNEXPLAINED_RESIDUAL is <=0.10 ms per stable decode step.

If the final residual is >0.10 ms, report:
`TOPLEVEL_DECOMPOSITION_INCOMPLETE`

and preserve the unexplained amount.

The 0.10 ms threshold is a measurement-closure criterion, not a hardware claim.

---

## 9. Local and system effects

For up_proj D3:

`MATERIAL_LOCAL_UP`
if:
- >=5% timing benefit;
- benefit > combined dispersion.

For stable D1-D3 whole decode:

`MATERIAL_SYSTEM`
if:
- >=2% benefit;
- benefit > combined dispersion.

Also report any positive-beyond-dispersion point below 2%.

---

## 10. Representative NCU

Re-query installed NCU metrics/version.

Profile two budgets:

- 16 MiB
- full-qweight request

For each budget:

### L0 up_proj D3
- CONTROL
- FAIR

### L0 self_attn D3
- CONTROL
- FAIR

Total:
8 primary profiles.

If self_attn range contains multiple kernels:
- preserve per-kernel metrics;
- sum only additive metrics.

Required base metrics:
- L1/TEX bytes
- L2 bytes
- DRAM bytes

Critical-path categories when available:
- kernel duration
- L2 read hit sectors
- L2 read miss sectors
- DRAM read bytes
- long-scoreboard stall
- LSU utilization
- active warps

Application replay + cache-control none.

Purpose:
test whether up_proj persistence benefit coincides with measurable self-attention degradation at representative budgets.

---

## 11. Stage outcomes

### RESIDENCY_COST_AWARE_SYSTEM_RELEVANT
At least one budget:
- whole-decode benefit >=2%;
- benefit > combined dispersion.

### RESIDENCY_COST_AWARE_POSITIVE_SUBTHRESHOLD
No system-relevant point, but at least one budget:
- positive whole-decode benefit > combined dispersion.

### RESIDENCY_OFFSET_LOCALIZED
No positive whole-decode point beyond dispersion, but:
- top-level decomposition qualified;
- >=80% of the negative offset relative to DIRECT_UP_SAVING is assigned to directly measured non-up categories.

This label does not by itself authorize a mechanism.
It means the failure mode is localized.

### RESIDENCY_SYSTEM_CASE_WEAK
No positive whole-decode point beyond dispersion and no stronger label.

### RESIDENCY_COST_DIAGNOSTIC_UNQUALIFIED
Policy or semantic decomposition cannot be qualified.

Precedence:
1. RESIDENCY_COST_DIAGNOSTIC_UNQUALIFIED
2. RESIDENCY_COST_AWARE_SYSTEM_RELEVANT
3. RESIDENCY_COST_AWARE_POSITIVE_SUBTHRESHOLD
4. RESIDENCY_OFFSET_LOCALIZED
5. RESIDENCY_SYSTEM_CASE_WEAK

No simulator work is auto-authorized.

---

## 12. 109 review pack

Create:

`docs/vm_tlb/review_packs/C16_E1_RESIDENCY_COST_BENEFIT_CLOSURE_109_V1/`

At minimum:

- `UPSTREAM_AUTHORITY.json`
- `BUDGET_MATRIX_CONTRACT.json`
- `TOPLEVEL_MODULE_AUTHORITY.json`
- `TOPLEVEL_NATIVE_TIMING.tsv`
- `FFN_CHILD_NATIVE_TIMING.tsv`
- `DECODE_STEP_TIMING.tsv`
- `POLICY_OVERHEAD.tsv`
- `RUN_ALIGNED_DECOMPOSITION.tsv`
- `BUDGET_EFFECT_ANALYSIS.json`
- `RESIDUAL_LOCALIZATION.json`
- `REPRESENTATIVE_NCU_INDEX.tsv`
- `REPRESENTATIVE_CRITICAL_PATH.json`
- `STAGE_DECISION.json`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Preserve all raw evidence.

Update scientific log.

---

## 13. 174-new parallel role

174-new should:

1. independently close the operator-family producer first;
2. freeze this cost/benefit consumer before new producer data;
3. implement budget/policy/top-level/FFN/decomposition/NCU consumers;
4. preserve operator-family producer label separately;
5. fetch the new producer once after prep and consume if ready;
6. otherwise stop READY.

No simulator run.

---

## 14. Next-step review

After independent closure, ChatGPT will choose among:

- authorize bounded trace + first simulator mechanism;
- revise the mechanism around measured interference/cost;
- stop the current residency mechanism line;
- review required.

No producer or consumer auto-authorizes simulator mutation.
