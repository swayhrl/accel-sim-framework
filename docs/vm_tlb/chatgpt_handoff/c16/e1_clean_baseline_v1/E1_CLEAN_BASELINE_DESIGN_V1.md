# C16 E1 Clean Baseline Design V1

## 1. Goal

Build a new durable, reproducible Qwen2.5-7B clean baseline that answers:

> How do semantic operator, M shape, dtype, and deployed AWQ implementation interact at the GPU module level?

The old eight-point matrix is preserved only as historical context because its RAW input authority cannot be fully reproduced.

The clean baseline must not depend on historical RAW activation tensors.

---

# 2. Primary matrix

Run all 18 points under one new canonical input authority:

`{q_proj, down_proj, up_proj} × {M1, M256} × {RAW_BF16, RAW_FP16, AWQ_FP16_INPUT}`

For each role:
- canonical semantic source = live RAW natural S2_TEXT Layer0 M2048 module input;
- M256 = first 256 rows;
- M1 = first row;
- RAW_FP16 and AWQ consume the exact same FP16 activation bytes.

This is the new primary scientific matrix.

---

# 3. Stage A — freeze new canonical activation authority

Use:
- RAW Qwen2.5-7B revision `a09a35458c702b33eeacc393d103063234e8bc28`;
- accepted S2_TEXT token SHA `0ab5bfe82130720edcbeac23c83b44b16cd8d21e4ccd5b4ee41c465c9159b4f9`;
- frozen existing runtime/source; no package upgrades.

Capture exact Layer0 module inputs for:
- q_proj;
- down_proj;
- up_proj.

Freeze M2048/M256/M1 tensors with:
- shape
- stride
- dtype
- byte SHA
- source model/token/runtime identity.

### Reproducibility gate

Regenerate the authority in a fresh process using the same frozen replay.

Require identical M2048 activation SHA for all three roles.

If not deterministic, STOP as a scientific authority problem.

### Direct replay gate

For every role/shape, invoke the exact RAW_BF16 module directly and require repeatable output under a documented exact/tolerance contract. Prefer bitwise equality if observed.

No historical output SHA is used as a gate.

---

# 4. Stage B — dtype bridge

For every role/shape:

Create canonical FP16 activation by casting the new BF16 authority.

Require:
- finite values;
- BF16 -> FP16 -> BF16 bitwise equality.

Create RAW_FP16 dense module state from the exact RAW weights/bias:
- cast weights/bias to FP16 once;
- preserve tensor layout as appropriate;
- record weight/bias SHA;
- require finite values;
- test BF16 -> FP16 -> BF16 equality where possible.

The same FP16 activation tensor must be passed byte-for-byte to:
- RAW_FP16
- AWQ_FP16_INPUT

If AWQ requires a different activation dtype for its actual accepted backend, STOP before changing this contract.

---

# 5. Stage C — 18-point native timing matrix

For each point:
- 2 warmups;
- 7 measured iterations;
- CUDA events around the exact semantic module call;
- preserve all raw samples;
- report min/median/max/CV;
- deterministic rotated ordering across implementations to reduce order drift.

Record:
- semantic role
- M
- implementation
- input/weight/output dtype
- input/output shape/stride
- module class
- lightweight implementation path fingerprint
- output hash
- timing samples

Do not include model load or authority construction in timing.

### Lightweight path fingerprint

Use the least intrusive method available:
- frozen source-path evidence;
- CUDA/PyTorch profiler kernel names;
- exact module class/dispatch branch.

Do not use NCU timing as native timing.

---

# 6. Core analysis

For each role and M report:

### Dtype effect

`R_dtype = T(RAW_FP16) / T(RAW_BF16)`

### Low-bit deployment implementation effect under same FP16 input

`R_awq = T(AWQ_FP16_INPUT) / T(RAW_FP16)`

### Historical deployment comparison

The old RAW/AWQ matrix may be shown only in a separate historical table.

Do not merge historical values into clean-baseline ratios.

### Shape response

Within each implementation:

`R_shape = T(M256) / T(M1)`

### Interaction statistic

For each role:

`I = log(R_awq_M256) - log(R_awq_M1)`

Interpretation:
- I ≈ 0: AWQ-vs-RAW_FP16 effect is shape-stable;
- nonzero I: deployed implementation effect interacts with M shape.

Report exact numeric I; do not create arbitrary causal labels.

### Materiality gate

A difference is considered worth deeper profiling only if:
- absolute median difference >= 5%; and
- larger than the combined ordinary timing dispersion observed for the pair.

No p-value is required from 7 repeats.

---

# 7. Stage D — CODE holdout

Search existing local/node164 Qwen2.5 CODE input authority first.

If a common CODE token authority exists:
1. run the same RAW exact Layer0 replay;
2. capture canonical CODE `down_proj` M2048 input;
3. derive M1 and M256;
4. run only:
   - down_proj M1 RAW_FP16
   - down_proj M1 AWQ_FP16_INPUT
   - down_proj M256 RAW_FP16
   - down_proj M256 AWQ_FP16_INPUT

Use the exact same clean-baseline contract.

If no durable common CODE authority exists, record:

`CODE_HOLDOUT_NOT_RUN_NO_COMMON_AUTHORITY`

Do not open a new token-generation campaign in this Goal.

---

# 8. Stage E — bounded AWQ path-transition diagnostic

Existing frozen AWQ source reports a threshold around M=1024.

If the clean runtime still proves the same deterministic dispatch condition, run for `down_proj`:

- M1023 AWQ_FP16_INPUT
- M1024 AWQ_FP16_INPUT

using rows from the same canonical M2048 activation.

Also run:
- M1023 RAW_FP16
- M1024 RAW_FP16

if cheap and the RAW dense module supports the same direct boundary.

Purpose:
- determine whether an implementation path switch creates a timing discontinuity.

This is bounded. Do not sweep arbitrary M.

---

# 9. Stage F — conditional bounded NCU, pre-authorized within this Goal

Do not STOP merely to request permission if the following entry gate passes.

## Entry gate

Proceed only if:
1. at least one role has a material AWQ-vs-RAW_FP16 difference at M1 or M256; and
2. the same role shows a materially different ratio across M1 vs M256, or the transition diagnostic shows a clear path discontinuity; and
3. the lightweight path fingerprint shows a plausible implementation/kernel difference.

## Deterministic selection

Select the role with largest:

`abs(log(R_awq_M256) - log(R_awq_M1))`

Profile exactly four clean-baseline points:
- selected role M1 RAW_FP16
- selected role M1 AWQ_FP16_INPUT
- selected role M256 RAW_FP16
- selected role M256 AWQ_FP16_INPUT

If the M1023/M1024 transition is the dominant observed phenomenon, add at most the two AWQ transition points.

## Metrics

Collect only metrics that are available and unit-resolved on the installed NCU:
- L1/TEX requested bytes;
- L2 requested bytes;
- DRAM bytes;
- achieved occupancy / active warps if available;
- tensor/math/SM utilization if available;
- kernel duration only as diagnostic, not replacement for native timing.

Preserve exact metric names and units.

Report:
- raw traffic;
- traffic normalized by output elements;
- kernel list and launch geometry where available.

Do not infer cache/TLB causality from traffic alone.

If selectors cannot uniquely bind the intended semantic module kernels, record `NCU_SELECTOR_UNRESOLVED` and continue to closure without fabricating values.

---

# 10. No automatic full trace

Even if NCU reveals a strong memory-traffic difference:

Do not automatically launch:
- NVBit;
- full address trace;
- TLB/cache mechanism experiment.

Instead record the exact next question for review.

---

# 11. Optional independent raw-only sanity point

If Llama-3.2-1B is already locally available and a direct layer0 linear replay can be executed with no new asset/download work, a small RAW-only shape sanity test may be run:

- one q_proj-like linear
- one down/up-like MLP projection
- M1 vs M256

Purpose:
- check whether large RAW shape response is Qwen-specific.

This is optional and must not block E1.

Do not use it as a low-bit validation because there is no matched AWQ counterpart in this contract.

---

# 12. Required 109 review pack

`docs/vm_tlb/review_packs/C16_E1_CLEAN_BASELINE_109_V1/`

At minimum:

- `UPSTREAM_IDENTITY.json`
- `CANONICAL_ACTIVATION_AUTHORITY.json`
- `CANONICAL_ACTIVATION_INDEX.tsv`
- `AUTHORITY_REGENERATION_CHECK.json`
- `RAW_FP16_WEIGHT_BRIDGE.json`
- `CORE_18_POINT_TIMING.tsv`
- `CORE_18_POINT_PATHS.tsv`
- `CORE_ANALYSIS.json`
- `CODE_HOLDOUT.json`
- `TRANSITION_DIAGNOSTIC.tsv`
- `NCU_ENTRY_GATE.json`
- `NCU_SELECTED_POINTS.tsv`
- `NCU_METRICS.tsv`
- `SCIENTIFIC_INTERPRETATION.md`
- `NEXT_STEP_DECISION.json`
- `SHA256SUMS`

Update:
`docs/vm_tlb/scientific_logs/C16_LOWBIT_SHAPE_EXPLORATION_LOG.md`

The log must explicitly mark the old eight-point RAW input authority as non-reproducible and separate historical evidence from the new clean baseline.

---

# 13. 109 STOP conditions

Routine engineering problems are solve-and-continue.

Do not STOP at foreseeable phase boundaries.

STOP only for:
- canonical RAW activation regeneration is nondeterministic;
- AWQ cannot consume the same canonical FP16 activation without changing its accepted backend;
- RAW_FP16 construction requires semantic changes beyond dtype casting;
- model/token/source identity mismatch;
- GPU/runtime corruption;
- a scientific contract change not covered above.

Otherwise continue through all applicable stages in this one Goal.
