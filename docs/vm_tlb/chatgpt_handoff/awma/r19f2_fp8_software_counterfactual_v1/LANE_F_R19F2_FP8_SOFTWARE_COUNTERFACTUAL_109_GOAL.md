# Codex Goal — Lane F / node109
## AWMA R19F2 FP8 readiness strong-software counterfactual V1

Date: 2026-10-01

Execution branch:
`hrl/awma-r19f2-fp8-software-counterfactual-109-v1`

Scientific parent:
`7375abd8e86c1523c1873913e8fffccf0b4e3a96`

This is one continuous solve-and-continue Goal.

The order is fixed:

1. **Stage A — share one exact FP8 representation across Qwen gate_proj and up_proj.**
2. **Only if a material residual remains after Stage A, Stage B — one bounded fused current-scaling quantizer counterfactual.**
3. STOP with a software-closure or architecture-review classification.

Do not jump directly to Stage B.

---

# 0. Scientific question

R19F1 proved that online current-scaling representation readiness adds a material operator-boundary cost before one FP8 Linear.

R19F2 asks:

> In a natural Qwen MLP where `gate_proj` and `up_proj` consume the exact same hidden tensor, how much of that readiness cost is removed by simply producing the FP8 representation once and reusing it across both consumers? If a residual remains, can a single fused software quantization path remove it without changing FP8 bits/scales or GEMM math?

This is a strong-software/dataflow test, not a hardware-mechanism Goal.

---

# 1. Fixed source, model and input

Reuse exact R19F1 environment and source:

- NVIDIA Transformer Engine v2.19.0
- source commit `5e52befd5262c06289106338c308079d6adb391f`
- RTX4080 / SM89
- `Float8CurrentScaling(E4M3, use_power_2_scales=False)`
- Qwen/Qwen2.5-0.5B-Instruct revision
  `7ae557604adf67be50417f59c2c2f167def9a775`
- accepted R101 256-token real input
- layer 0 MLP hidden input:
  shape `[1,256,896]`

Reuse the parent frozen hidden input exactly.

Bind and freeze both real sibling weights:
- `model.layers.0.mlp.gate_proj.weight`
- `model.layers.0.mlp.up_proj.weight`

Both must be the natural Qwen layer0 weights from the same accepted model revision.

Record:
- tensor SHA256
- shape/dtype
- cached FP8 representation bits/scales
- device pointers after steady-state cache establishment.

No new prompt, model, layer or shape.

---

# 2. Numerical/identity admission before timing

## 2.1 Shared input representation

Use TE's public `Float8CurrentScalingQuantizer` with the exact same source-backed configuration as R19F1.

For the frozen hidden tensor X:

- capture each normal online Linear's quantized X representation;
- prove gate and up normal paths produce the exact same FP8 data bits and inverse scale;
- construct one public shared FP8 X representation;
- prove its bits/scale exactly match both normal online representations.

If normal gate and up paths do not produce the same represented X:
`R19F2_SHARED_REP_IDENTITY_NOT_QUALIFIED`
STOP.

## 2.2 Consumer identity

For gate and up separately prove:
- normal arm and shared-ready arm use the same cached FP8 weight representation;
- same native SM89 E4M3 GEMM function/shape;
- same output dtype;
- output is bitwise identical between normal and shared-representation arms.

A bounded source/runtime identity check is enough if R19F1's kernel witness plus unchanged shape/source makes identity unambiguous; otherwise use one combined NSYS witness later.

Do not infer from tensor metadata alone if backend identity changes.

---

# 3. Stage A — natural shared-representation software baseline

All CUDA under the shared GPU lock.

Three arms use the same hidden X and two real sibling weights.

## B0_DUPLICATE

Natural independent current-scaling path:

```
X BF16
  -> online current scaling
  -> gate_proj FP8 GEMM

X BF16
  -> online current scaling
  -> up_proj FP8 GEMM
```

Each Linear uses:
- steady-state cached FP8 weight;
- `is_first_microbatch=False` or equivalent accepted steady-state path.

No first-call/JIT in primary timing.

## S1_SHARED

Natural software/dataflow counterfactual:

```
X BF16
  -> current scaling ONCE
  -> same exact FP8 X
       -> gate_proj same FP8 GEMM
       -> up_proj same FP8 GEMM
```

The shared FP8 X must exactly equal each B0 normal representation.

Do not change either GEMM or weight representation.

## D0_READY_PAIR

Diagnostic ideal boundary:

```
same exact FP8 X already ready
  -> gate_proj same FP8 GEMM
  -> up_proj same FP8 GEMM
```

D0 begins after input representation preparation and is not a deployable-policy claim.

---

# 4. Stage A measured regions

Measure two nested regions.

## Region P — sibling projection region

Boundary:
`X BF16 ready at arm boundary -> gate and up outputs committed`

B0 contains two online quantizations.
S1 contains one online quantization.
D0 contains zero online quantization.

## Region M — natural MLP region

Extend the exact same arm through:

```
gate = gate_proj(...)
up   = up_proj(...)
h    = silu(gate) * up
out  = down_proj(h)
```

Use the same natural layer0 down_proj and the same TE/BF16 organization in every arm.

Important:
- R19F2 intervention changes only representation preparation of the shared X consumed by gate/up.
- The `silu * multiply` and `down_proj` path must be identical across B0/S1/D0.
- Do not optimize or prequantize down_proj input in this Goal.

Region M determines whether the local readiness effect remains material at a natural MLP boundary.

All three arms must produce bitwise-identical gate/up outputs and therefore bitwise-identical Region-M outputs, or STOP as mixed.

---

# 5. Stage A formal timing

For B0_DUPLICATE, S1_SHARED, D0_READY_PAIR:

- 3 paired groups
- 2 warmups per arm/group
- 5 formal samples per arm/group
- rotate/alternate arm order across groups
- save every wall and CUDA-event sample
- unprofiled formal timing.

Report median/MAD for Region P and Region M.

Also record:
- input quantizer launch count per arm;
- cached weight reuse;
- allocation deltas;
- representation bytes/scales;
- first-call/JIT separately.

## Stage A decision

Define:
- `H_ideal_M = B0_M - D0_M`
- `H_shared_M = B0_M - S1_M`
- `R_remaining_M = S1_M - D0_M`

### A — shared software closes the architecture-sized issue

Use:
`R19F2_SHARED_REP_SOFTWARE_SUFFICIENT`

if either:
- S1 vs D0 Region-M median residual is <5% of S1 Region-M time, OR
- S1 recovers >=70% of B0->D0 Region-M ideal headroom,

and timing direction is stable.

STOP. Do not run Stage B.

### B — residual remains after natural sharing

Proceed to Stage B only if all:
- B0/S1/D0 numerical and identity contracts pass;
- S1 beats B0 in the expected direction;
- S1 vs D0 Region-M residual remains >=5% of S1 Region-M time;
- all three paired-group median S1-D0 gaps have the same positive sign;
- combined gap >3x larger-arm MAD.

If the sibling Region-P residual remains large but Region-M residual is <5%, STOP:
`R19F2_LOCAL_FP8_READINESS_NOT_MATERIAL_AT_MLP_BOUNDARY`

Do not proceed to Stage B merely because a local percentage looks large.

If unstable:
`R19F2_RESULT_MIXED_NEEDS_REVIEW`
STOP.

---

# 6. Stage B — fused current-scaling software counterfactual

Run only if Stage A authorizes it.

## 6.1 First search for an existing direct software path

Audit pinned TE v2.19 and current TE source for:
- standalone or reusable fused current-scaling quantization;
- fused amax + scale + FP8 cast;
- activation/current-scaling fusion that can legally reproduce the exact frozen X representation.

Current-main code may be read for capability/design only. Do not silently change the consumer runtime from v2.19 during formal comparison.

If a source-supported path can produce exactly the same FP8 bits and scale on SM89, use it.

## 6.2 If no source-supported standalone path exists

Exactly one minimal opt-in software diagnostic is allowed:

A single-launch current-scaling quantizer for this exact per-tensor E4M3 contract, implemented as the smallest reasonable CUDA/extension diagnostic.

Requirements:
- no custom GEMM;
- no approximation;
- no changed scale rule;
- exact FP8 input bytes equal TE v2.19 representation;
- exact inverse scale equal;
- same shared FP8 X is then consumed by the same gate/up GEMMs.

A cooperative-grid or equivalent single-launch implementation is allowed only if bounded and exact on SM89.

Do not generalize it into a new library or architecture mechanism.

If exact one-launch representation cannot be qualified without broad redesign:
`R19F2_FUSED_COUNTERFACTUAL_NOT_QUALIFIED`
STOP.

---

# 7. Stage B arms

Keep Stage-A B0 and D0 receipts.

Add:

## S2_FUSED_SHARED

```
X BF16
 -> exact single-launch fused current-scaling representation
 -> same FP8 X bits/scale
      -> gate same GEMM
      -> up same GEMM
 -> same silu/multiply/down_proj path
```

S2 must be bitwise identical to S1/D0 at:
- FP8 input bits/scale;
- gate output;
- up output;
- Region-M final output.

If not, S2 is not qualified.

Formal timing:
- S1_SHARED vs S2_FUSED_SHARED vs D0_READY_PAIR
- same 3 groups / 2 warmups / 5 formal schedule
- Region P and Region M
- unprofiled.

At most one combined NSYS capture after formal timing if needed.
At most one NCU exact target only if NSYS cannot distinguish the remaining quantizer work.

---

# 8. Stage B final decisions

### Software fusion sufficient

`R19F2_FUSED_SOFTWARE_SUFFICIENT`

if S2:
- closes Region-M residual to <5% of S2 time, OR
- recovers >=70% of S1->D0 remaining Region-M headroom,

with stable paired timing.

This closes the current hardware line.

### Residual survives strong software

`R19F2_READINESS_RESIDUAL_SURVIVES_STRONG_SOFTWARE`

requires all:
- exact same FP8 representation;
- exact same gate/up consumers;
- exact same natural MLP downstream;
- shared representation already applied;
- exact fused quantizer applied;
- S2 Region-M still >=5% slower than D0;
- all paired groups same direction;
- gap >3x larger-arm MAD;
- no first-call/JIT/backend change.

This label means:
`READY_FOR_ARCHITECTURE_REVIEW`

It does **not** authorize a hardware mechanism or 174.

### Mixed

`R19F2_RESULT_MIXED_NEEDS_REVIEW`

for unstable or ambiguous evidence.

---

# 9. Interpretation constraints

Do not claim:
- BF16->FP8 speedup;
- model-level quality equivalence;
- whole-model latency improvement;
- Blackwell FP4/TMEM behavior;
- quantization arithmetic alone explains all R19F1 residual;
- a new hardware unit is justified merely because S2-D0 >0.

The project question is whether a material representation-readiness residual survives realistic strong software/dataflow organization.

---

# 10. Profiling limits

Across the entire Goal:
- at most one new NSYS capture;
- at most one NCU target;
- no NVBit/SASS;
- no Accel-Sim;
- no node174 execution.

The R19F1 NSYS identity may be reused where scientifically sufficient.

---

# 11. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R19F2_FP8_SOFTWARE_COUNTERFACTUAL_109_V1/`

At minimum:
- README.md
- PARENT_AUTHORITY.json
- REAL_MLP_INPUT_WEIGHT_RECEIPT.json
- SHARED_REP_IDENTITY.json
- NUMERICAL_IDENTITY.tsv
- STAGE_A_CONTRACT.md
- STAGE_A_TIMING_P.tsv
- STAGE_A_TIMING_M.tsv
- STAGE_A_DECISION.md
- SOFTWARE_CAPABILITY_AUDIT.md
- STAGE_B_CONTRACT.md if triggered
- FUSED_REP_IDENTITY.json if triggered
- STAGE_B_TIMING_P.tsv if triggered
- STAGE_B_TIMING_M.tsv if triggered
- PROFILE_SUMMARY.tsv if triggered
- FINAL_DECISION.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Large raw stays on node164.

---

# 12. Closure

Release GPU lock after each bounded campaign and final closure.
Commit/push/fetch-back exact branch SHA/tree.
Clean worktree.
STOP.

Do not auto-start architecture design, simulator work or a second shape after closure.
