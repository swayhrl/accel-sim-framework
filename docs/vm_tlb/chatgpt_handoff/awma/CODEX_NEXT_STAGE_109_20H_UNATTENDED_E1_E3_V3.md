# CODEX NEXT STAGE — 109 20h Unattended E1/E3 Characterization V3

Date: 2026-09-20

Status: ACTIVE AFTER USER LAUNCH

Mode:

`GOAL MODE / 20H UNATTENDED / solve-and-continue`

Node:

`109 / RTX4080`

Stage:

`AWMA_109_20H_UNATTENDED_E1_E3_CHARACTERIZATION_V3`

Coordination branch:

`hrl/awma-109-20h-unattended-e1-e3-handoff-v3`

Read first:

1. `docs/vm_tlb/chatgpt_handoff/awma/REVIEW_109_E1_V2_20H_DECISION_2026-09-20.md`
2. `docs/vm_tlb/chatgpt_handoff/awma/UNATTENDED_POLICY_109_20H_V3.md`
3. `docs/vm_tlb/chatgpt_handoff/awma/UNATTENDED_ACCEPTANCE_109_20H_V3.md`
4. this Goal

Accepted parent execution:

`hrl/awma-e1-shape-oracle-moe-harness-109-v2`

`56096d32bd5cd783286e1b5e5e612b6019f926d0`

Suggested execution branch:

`hrl/awma-109-20h-unattended-e1-e3-v3`

Create from the accepted parent.

Do not rewrite prior review packs.

---

# 0. Fresh 20h campaign clock

At actual Goal launch record:

`START_UTC`

Set:

`DEADLINE_UTC = START_UTC + 20 hours`

Set:

`NO_NEW_GPU_SCIENCE_AFTER = DEADLINE_UTC - 2 hours`

Write:

`CAMPAIGN_TIME_AUTHORITY.json`

Do not inherit any prior 20h/12h/V1/V2 deadline.

If an external launcher/runtime exposes a stricter real deadline:
- record exact value/source;
- use the stricter boundary.

---

# 1. GPU ownership and preflight

Use:

`/data/c16/locks/c16_gpu_campaign.lock`

Before first GPU task and after any long idle interval:
- verify expected RTX4080 UUID/identity;
- inspect legitimate GPU owner;
- acquire lock normally;
- never kill/bypass another workload.

Record:
- driver;
- CUDA;
- torch;
- GPU UUID;
- baseline memory;
- thermal/clock baseline if readily available.

No package upgrade.

---

# 2. Campaign DAG

The scheduler must keep independent work alive.

Scientific DAG:

```text
M0 E1 accepted-evidence synthesis
 |
 +--> M1 threshold-transition diagnostic
 |      |
 |      +--> M2 module-level resource profiling
 |      |
 |      +--> M3 same-quantized-weight decomposition
 |
 +--> M4 E3 exact experts-harness materialization
        |
        +--> M5 E3 N/P/U-active timing

M6 G1 scenario extension              independent after preflight
M7 G4 Llama raw holdout               independent after preflight
M8 G3 profiler-protocol sensitivity   depends on working profiler path
M9 optional detailed capture          depends on M1/M2 selector gate
```

GPU tasks execute serially.

CPU-only analysis/source work/transfer may overlap safely.

A STOP in one branch MUST NOT end the campaign while another READY branch exists.

---

# 3. M0 — E1 accepted-evidence synthesis

No GPU required unless verification is necessary.

Bind the accepted E1 V2 artifacts.

Create:

`E1_ACCEPTED_CORE_ANALYSIS.tsv`

For all 8 accepted points report:
- implementation;
- role;
- M;
- input rank/shape/stride/dtype;
- median;
- sample dispersion;
- output SHA;
- implementation path.

Compute descriptive comparisons only:

### shape scaling inside raw
- q_proj M256/M1
- down_proj M256/M1

### shape scaling inside AWQ
- q_proj M256/M1
- down_proj M256/M1

### deployment-level raw/AWQ ratios
- q_proj M1
- q_proj M256
- down_proj M1
- down_proj M256

Explicitly mark:

`DEPLOYMENT_LEVEL_ONLY`

unless same-input semantics are separately proven.

Do not rerun the core 8 timing points merely to make a cleaner table.

---

# 4. M1 — AWQ threshold-transition diagnostic

Frozen installed dispatch:

`x.shape[0] * x.shape[1] >= 1024`

For preserved shape `[1,M,K]`, transition occurs at M=1024.

Use accepted real M2048 activation input pool.

Roles:

- q_proj
- down_proj

Required AWQ points:

- M1023
- M1024

Preferred raw controls:

- raw q_proj M1023/M1024
- raw down_proj M1023/M1024

Raw controls are MANDATORY unless a concrete runtime/resource issue blocks them; they are cheap and scientifically useful.

## M1 authority

For every point:
- first M rows of accepted natural activation input;
- preserve `[1,M,K]`;
- preserve dtype;
- shape-specific output oracle;
- exact repeatability before timing.

Do not compare against M2048 output slice.

## M1 timing

- 3 warmups;
- 9 CUDA-event samples;
- retain all samples;
- median;
- MAD or IQR;
- clocks/thermal note if outlier variance is large.

## M1 fingerprint

Record:
- exact path;
- kernel sequence;
- grid/block;
- dequantization occurrence;
- GEMM occurrence;
- temporary allocations if readily visible.

Expected hypothesis from frozen source:
- AWQ M1023 = quantized GEMM;
- AWQ M1024 = dequantize + matmul.

Do not force this expectation; record actual execution.

Output:

- `E1_THRESHOLD_MATRIX.tsv`
- `E1_THRESHOLD_FINGERPRINT.tsv`
- `E1_THRESHOLD_NUMERIC_ORACLE.tsv`

---

# 5. M2 — Reliable module-level resource profiling

Goal:

explain the strongest E1 timing contrast using a profiler path that is first proven to select the correct semantic call.

## M2.1 selector canary

Use isolated module-replay executables/processes from accepted shape authority.

Preferred:
- one semantic module call per process;
- explicit NVTX range if supported by installed NCU;
- installed `ncu --query-metrics` for actual metric availability.

First run a cheap canary.

Canary passes only if expected semantic kernels are actually profiled.

If zero kernel:
`SELECTOR_UNRESOLVED`

Then:
- repair selector/range engineering;
- try bounded alternative exact selection;
- if unresolved after reasonable attempts, freeze NCU for that target and continue the campaign.

Do NOT end the whole Goal.

## M2.2 mandatory contrast set

Profile:

```text
down_proj raw M1
down_proj AWQ M1
down_proj raw M256
down_proj AWQ M256
```

Reason:
the deployment-level direction reverses between M1 and M256.

## M2.3 optional q_proj set

If selector is reliable and time remains:

```text
q_proj raw M1
q_proj AWQ M1
q_proj raw M256
q_proj AWQ M256
```

## M2.4 metrics

Discover from installed NCU.

Prefer supported metrics covering:
- L1/TEX requested bytes;
- L2 requested bytes;
- DRAM bytes;
- SM/math/tensor utilization;
- achieved occupancy;
- warp activity;
- instruction count/classes;
- selected stalls where interpretable.

Do not hard-code unavailable metric names.

Record:
- NCU version;
- replay mode;
- cache-control;
- number of passes;
- exact target/range selector;
- whether profiling perturbs timing.

Native performance claim always uses uninstrumented timing from M0/M1.

Outputs:

- `E1_RESOURCE_PROFILE.tsv`
- `E1_NCU_SELECTOR_RECEIPT.tsv`
- `E1_RESOURCE_INTERPRETATION.md`

---

# 6. M3 — Same-quantized-weight implementation decomposition

Entry gate:

- exact frozen AWQ buffers accepted;
- exact runtime exposes both quantized GEMM and dequantize+matmul primitives;
- no new backend needed.

Default role:

`down_proj`

Use same accepted qweight/qzeros/scales.

Shapes:

- M1
- M256
- M1023
- M1024

For each shape compare:

### A — deployed AWQ path
the frozen `WQLinear_GEMM` behavior.

### B — one-time dequantized weight + matmul
dequantize exact AWQ weight once OUTSIDE timed region;
time matmul only.

### C — per-invocation dequantize + matmul
dequantization INCLUDED inside timed region.

Numerical output must be compared against the deployed AWQ shape-specific oracle.

Do not create a new optimized backend.

Report:
- exact timing boundary;
- output error;
- kernel sequence;
- traffic/resource metrics if profiler selector already works.

This experiment is diagnostic:
it separates quantized-GEMM efficiency from dequantization overhead and matmul efficiency.

Outputs:

- `E1_IMPLEMENTATION_DECOMPOSITION.tsv`
- `E1_IMPLEMENTATION_NUMERIC_VALIDATION.tsv`

---

# 7. M4 — Materialize exact Q30 experts-control harness

This task MUST NOT stop merely because the harness does not pre-exist.

Authority:

`ee67225edc8fc5868de585d38e0391cbeb755d9f`

Use accepted Q30 S2/T2048 Prefill exact layer/state.

Freeze exact local source first:
- transformers/model file path;
- SHA256;
- target layer;
- gate/router implementation;
- inline/exposed expert dispatch implementation;
- expert modules;
- exact weights/backend/residency.

Produce:

`E3_FROZEN_RUNTIME_SOURCE_CONTRACT.md`

## M4.1 allowed harness implementation

If the runtime has an exact experts function:
wrap/call it directly.

If expert dispatch is inline:
create a TEST-ONLY harness by extracting the exact frozen source operations.

The harness may:
- take hidden_states;
- take selected_experts;
- take routing_weights;
- execute the same grouping;
- call the same expert module objects;
- apply the same routing weights;
- combine identically.

It may NOT:
- change expert math;
- change precision;
- change weight layout;
- change backend;
- change residency policy;
- batch experts differently for performance;
- fuse/unfuse for optimization.

A missing helper is engineering work.

## M4.2 natural canary

Use exact accepted hidden state.

1. execute real gate;
2. capture natural route IDs/weights;
3. capture natural expert-path output at exact boundary;
4. run test harness with same hidden/routes/weights;
5. compare.

If nondeterminism exists:
first establish bounded repeatability independently;
do not create a tolerance directly from harness mismatch.

Only if N canary qualifies:
`E3_HARNESS_NATURAL_PASS`

If exact source semantics cannot be reproduced without changing math/backend:
freeze E3 as `STOP_SCIENTIFIC_HARNESS_SEMANTICS_UNRESOLVED`
and continue M6/M7/M8/M9.

Outputs:

- `E3_HARNESS_SOURCE_AUDIT.md`
- `E3_N_CANARY.tsv`

---

# 8. M5 — E3 N/P/U-active light diagnostic

Only after M4 N canary passes.

## N

Exact natural routing.

Record:
- M=2048;
- top-k;
- active expert IDs;
- expert histogram;
- CV;
- route weights summary;
- kernel sequence;
- expert-region timing.

## P

Freeze deterministic token permutation before timing.

Jointly permute token rows of:
- hidden;
- selected_experts;
- routing_weights.

Run exact harness.

Inverse-permute output.

Require:
- exact expert histogram unchanged;
- output equivalence under qualified N repeatability contract.

If P fails:
freeze P/U interpretation and continue other tasks.

## U-active

Only after P passes.

Use naturally active expert set A only.

Keep:
- M=2048;
- top-k;
- total assignment count;
- same hidden;
- same expert modules/backend;
- same per-token routing-weight values in rank slots.

Construct deterministic balanced routes:
- k distinct IDs/token;
- IDs in A;
- global expert counts differ by <=1 where possible.

Label:
`SYNTHETIC_ROUTING`

No model-quality claim.

## timing

- 3 warmups;
- 9 measured repetitions;
- all samples;
- router timing separately for N;
- expert region includes native grouping/dispatch/expert/weight/combine semantics.

Optional light NCU only after an exact range/selector canary.

Outputs:

- `E3_ROUTING_MATRIX.tsv`
- `E3_NATIVE_TIMING.tsv`
- `E3_P_EQUIVALENCE.tsv`
- `E3_U_ACTIVE_CONSTRUCTION.json`
- `E3_RESOURCE_DIAGNOSIS.tsv` if profiling qualifies.

---

# 9. M6 — Opportunity G1: existing-model scenario extension

Run only with existing accepted Qwen2.5-0.5B asset.

No download.

Priority:

1. B1 / T8192 / D32
2. B4 / T2048 / D32

Use new scenario IDs.

Input policy:
- exact token authority;
- preferably traceable natural/text source;
- do not repeat tokens to create a fake long-context workload and call it natural.

Measure:
- native end-to-end/phase timing;
- lightweight kernel census;
- peak memory;
- representative kernel occurrence mapping.

No detailed trace by default.

Outputs:

- `G1_SCENARIO_MATRIX.tsv`
- `G1_KERNEL_CENSUS.tsv`

If memory/runtime blocks B4:
mark local status and continue.

---

# 10. M7 — Opportunity G4: Llama raw shape holdout

Use existing:

`Llama-3.2-1B @ 4e20de362430cd3b72f300e6b0f18e50e7166e08`

No download.

Freeze at most two linear roles BEFORE timing.

Preferred semantic analogues:
- q_proj
- down_proj

Use a real accepted/frozen activation source from one natural scenario if available.

If no activation authority exists:
Codex is authorized to produce one from the existing model + frozen input, using the same authority discipline learned in E1.

Do not stop because the pool does not pre-exist.

Run:
- M1
- M256

Claim:
`RAW_CROSS_MODEL_SHAPE_HOLDOUT`

No AWQ comparison.

Outputs:

- `G4_LLAMA_SHAPE_HOLDOUT.tsv`
- `G4_LLAMA_AUTHORITY.json`

---

# 11. M8 — Opportunity G3: NCU protocol sensitivity

Entry:
normal module-level NCU path from M2 works.

Use one or two exact existing targets.

Preferred:
- AWQ down_proj M256
- one existing application-context target such as Q05/Prefill GEMM only if identity is trivial to reuse.

Compare supported installed-NCU protocol settings:
- replay mode;
- cache-control variants.

Same target and metric set.

Claim:
`PROFILER_PROTOCOL_SENSITIVITY`

Never call cache-control a TLB flush.

Output:

`G3_NCU_PROTOCOL_MATRIX.tsv`

---

# 12. M9 — Optional detailed capture

Pre-frozen candidate:

`AWQ down_proj M1023 vs M1024`

This pair is chosen BEFORE new transition results because it straddles the frozen source threshold with nearly identical M.

Entry gates:

- M1 accepted;
- actual path switch confirmed;
- exact module/kernel selector stable;
- M2/M3 indicate detailed memory/instruction behavior would add explanatory value;
- >=3h remain before closeout reserve;
- estimated total new detailed raw <=16 GiB.

If all pass:
capture a bounded paired detailed trace using the accepted producer contract.

Do not switch to another pair because its result looks more interesting unless explicitly labeled exploratory.

Partial:
`PARTIAL_NOT_ADMITTED`

Outputs:
- `DETAILED_CAPTURE_SELECTOR_DECISION.md`
- trace receipts if executed.

---

# 13. Opportunity exhaustion logic

If M4/M5 E3 scientifically stops early, do NOT stop campaign.

Proceed:

M1 -> M2 -> M3 -> M6 -> M7 -> M8 -> M9 where gates pass.

If E1 profiling stops:
continue E3, G1, G4.

If model-specific G1/G4 stops:
continue remaining tasks.

Only when no READY task remains may the campaign close early.

---

# 14. Final two-hour reserve

At `NO_NEW_GPU_SCIENCE_AFTER`:

Do not start new:
- model execution family;
- profiler campaign;
- capture target.

Allowed:
- finish safely closable running task;
- transfer;
- hash;
- analyze;
- produce reports;
- node164 ACK;
- commit/push;
- remote verify;
- clean;
- release lock.

A run that cannot safely close:
`PARTIAL_NOT_ADMITTED`

---

# 15. Forbidden

No:
- new model download;
- model revision substitution;
- package/runtime upgrade;
- fake/random activation replacing natural authority;
- new quantization backend;
- modified expert backend;
- OLMoE/DeepSeek expansion just to fill time;
- TLB/PTW/PWC/cache architecture mechanism;
- broad NVBit/SASS sweep;
- unbounded shape sweep.

---

# 16. Durable output

Large artifacts:

`/root/share/mnt164/huangrulin/awma_109_20h_unattended_e1_e3_v3/`

Report:

`docs/vm_tlb/codex_handoff/awma/UNATTENDED_E1_E3_20H_109_V3_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_109_20H_UNATTENDED_E1_E3_V3/`

Required minimum:

```text
README.md
SOURCE_ANCHORS.md
CAMPAIGN_TIME_AUTHORITY.json
PIPELINE_STATE.json
E1_ACCEPTED_CORE_ANALYSIS.tsv
E1_THRESHOLD_MATRIX.tsv
E1_THRESHOLD_FINGERPRINT.tsv
E1_THRESHOLD_NUMERIC_ORACLE.tsv
E1_NCU_SELECTOR_RECEIPT.tsv
E1_RESOURCE_PROFILE.tsv
E1_RESOURCE_INTERPRETATION.md
E1_IMPLEMENTATION_DECOMPOSITION.tsv
E1_IMPLEMENTATION_NUMERIC_VALIDATION.tsv
E3_FROZEN_RUNTIME_SOURCE_CONTRACT.md
E3_HARNESS_SOURCE_AUDIT.md
E3_N_CANARY.tsv
E3_ROUTING_MATRIX.tsv
E3_NATIVE_TIMING.tsv
E3_P_EQUIVALENCE.tsv
E3_U_ACTIVE_CONSTRUCTION.json
G1_SCENARIO_MATRIX.tsv
G1_KERNEL_CENSUS.tsv
G4_LLAMA_SHAPE_HOLDOUT.tsv
G4_LLAMA_AUTHORITY.json
G3_NCU_PROTOCOL_MATRIX.tsv
DETAILED_CAPTURE_SELECTOR_DECISION.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

For a gated/skipped task, the corresponding file may contain an explicit status receipt instead of fabricated results.

Success marker:

`AWMA_109_20H_UNATTENDED_E1_E3_CHARACTERIZATION_V3_COMPLETE_WITH_SCOPE`

Then:

node164 ACK -> report -> review pack -> hashes -> commit -> push -> remote verify -> clean worktree -> release GPU lock -> confirm idle -> STOP.

Do not automatically enter architecture mechanism design or download another model.
