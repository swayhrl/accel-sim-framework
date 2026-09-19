# CODEX NEXT STAGE — 109 20h Native / Workload Characterization Pipeline V1

Date: 2026-09-19

Status: ACTIVE AFTER USER LAUNCH

Mode: GOAL MODE / solve-and-continue

Node: 109 / RTX4080

Coordination:
`hrl/awma-20h-unattended-pipeline-handoff-v1`

Read first:
1. CURRENT_STATE.md
2. DISCUSSION_REFERENCE.md
3. PIPELINE_ACCEPTANCE_CONTRACT_20H_V1.md
4. PIPELINE_SCHEDULER_POLICY_20H_V1.md
5. this file

## 0. Accepted anchors

AWMA 109 V1 selected producer campaign:
`8f49ba3b9228b5f8a9163e961225ffd415107734`

AWMA 109 V2.1:
`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

Do not rewrite accepted packs/data.

Suggested execution branch:
`hrl/awma-109-native-workload-pipeline-20h-v1`

Create from current coordination branch or a clean source parent chosen without rewriting accepted evidence.
Record ancestry explicitly.

## 1. Start/timing/lock

At actual Goal start record START_UTC.
DEADLINE=START+20h.
NO_NEW_TARGET_AFTER=DEADLINE-2h.

Before GPU:
- verify RTX4080 UUID;
- inspect/acquire /data/c16/locks/c16_gpu_campaign.lock normally;
- never kill/bypass owner.

## 2. M0 — Existing-family native resource closure

Targets:
- Q05 Prefill Flash;
- Prefill GEMM Primary;
- Decode GEMV Primary;
- Decode Flash Primary-1.

Reuse accepted NSYS/NCU/native evidence before running anything.

For each required field classify:
`ACCEPTED_REUSE`, `MISSING_NEEDS_RUN`, `COUNTER_UNAVAILABLE`.

Close:
- exact semantic/function/shape/occurrence;
- native timing authority where available;
- kernel/census context;
- compute/tensor-pipeline utilization where supported;
- occupancy/warp activity;
- L2 traffic;
- DRAM traffic;
- selected stall indicators only if interpretable.

Record NCU version, replay mode, cache-control, pass count, target selector.

No dense profiling of Primary-2.

Output:
`EXISTING_FAMILY_NATIVE_RESOURCE_MATRIX.tsv`

## 3. M1 — E1 shape x low-bit implementation

Models:
raw:
`Qwen2.5-7B-Instruct @ a09a35458c702b33eeacc393d103063234e8bc28`

AWQ:
`Qwen2.5-7B-Instruct-AWQ @ b25037543e9394b818fdfca67ab2a00ecc7dd641`

Reuse existing assets/anchors only after receipt verification.

Core:
`{down_proj,q_proj} x {M=1,M=256} x {raw,AWQ}`

N/K from real weights.

M1 is shape diagnostic, not natural Decode.

### 3.1 Semantic/input authority

For each operator:
- exact layer/operator;
- weight or qweight/qzeros/scales hash/identity;
- activation pool source/hash;
- input tensor rank/shape/stride/dtype;
- backend/version;
- timing region;
- actual kernel sequence.

Existing down_proj anchor may be reused after exact verification.
q_proj requires independent closure.

### 3.2 Numeric semantics

Classify every raw/AWQ pair:
- SEMANTIC_PAIR_QUALIFIED
- IMPLEMENTATION_LEVEL_ONLY

If AWQ absorbed scaling/input transform cannot be proven for a clean same-function pair, do not fabricate it.
Continue implementation-level characterization.

### 3.3 Dtype bridge

Inspect actual runtime input/output and available accumulation behavior.

If raw/AWQ differ materially in compared execution dtype, add matching raw-FP16 bridge points for each affected operator at M1/M256.

Do not overwrite BF16 raw identity.

### 3.4 Timing

New points:
- 2 warmups;
- 5 uninstrumented measured samples;
- retain every sample;
- median + dispersion;
- bounded repeat only after clock/temp/background sanity.

Do not pick fastest sample.

### 3.5 Fingerprint

Record all kernels in semantic region, including dequant/copy/postprocess.
Do not report only matmul if actual AWQ operator is multi-kernel.

### 3.6 Resource diagnosis

After timing/fingerprint closure, run bounded NCU only where needed to separate:
A traffic reduction;
B M-dependent utilization/reuse;
C implementation/dequant/layout/kernel-selection effects.

Output:
- E1_CORE_MATRIX.tsv
- E1_IMPLEMENTATION_FINGERPRINT.tsv
- E1_NUMERIC_VALIDATION.tsv
- E1_NATIVE_TIMING.tsv
- E1_RESOURCE_DIAGNOSIS.tsv
- E1_CLAIM_BOUNDARY.md

No positive-effect requirement.

## 4. C1 — Conditional E3 MoE routing

Run only if:
- M1 cleanly closes;
- Qwen3-30B-A3B exact S2 state/replay authority verifies;
- same expert backend and residency/loading policy can be held;
- budget remains.

Q30 model authority:
`Qwen3-30B-A3B @ ad44e777bcd18fa416d9da3bd8f70d33ebb85d39`

Reuse accepted S2 state/replay; do not rerun full 48-layer semantic stream if authority is intact.

If target qualification needed to identify actual execution kernels, perform only bounded qualification needed for this E3 region.
Do not start formal large trace.

Cases:
- N natural
- P histogram-preserving joint permutation + inverse output check
- U-active balance within natural active expert set

Hold M=2048, E/k, total assignments, expert precision/backend/residency, input pool, timing boundary.

Record route histogram/CV, active experts, kernel counts/shapes, dispatch/expert/combine timing, lightweight resource evidence.

P equivalence must pass.
U-active = SYNTHETIC_ROUTING.

## 5. Opportunity O1 — G1 scenario extension

Priority:
1. Qwen2.5-0.5B B1/T8192/D32
2. B4/T2048/D32

Frozen base model:
`7ae557604adf67be50417f59c2c2f167def9a775`

Use new scenario IDs and exact token bindings.
Prefer inputs with traceable relation to existing S2.
Do not create artificial repeated-token long context and call it natural text.

Run native timing + lightweight census.
No default detailed trace.

## 6. Opportunity O2 — G2 same-quantized-weight implementation decomposition

Use already qualified E1 operator only if frozen runtime exposes trustworthy existing reference paths.

Compare as available:
A actual AWQ;
B one-time dequantized weight + FP16 matmul;
C per-invocation dequantization + FP16 matmul.

No new backend implementation.

Report dequant timing boundaries and numeric validation.
Diagnostic only.

## 7. Opportunity O3 — G3 profiler protocol sensitivity

Targets:
- Q05 Prefill Flash
- Prefill GEMM Primary

Compare supported NCU application replay/cache-control variants under installed version.
Reuse matching measurements.

Same target + metric set.
Claim only profiling-protocol sensitivity.
Never label cache-control as TLB flush.

## 8. Opportunity O4 — G4 Llama raw shape holdout

Llama-3.2-1B authority:
`4e20de362430cd3b72f300e6b0f18e50e7166e08`

At most two pre-frozen linear semantic roles x M1/M256.
No new download.
Claim = raw shape trend only, not AWQ validation.

## 9. Optional detailed capture

Not mandatory.

May capture at most one paired scientific contrast unless additional pair remains within same 16 GiB total raw cap.

Entry:
- selector rule frozen before holdout;
- native effect exceeds noise OR uniquely discriminates competing explanations;
- exact semantic/kernel identity;
- enough time for capture+transfer+finalization.

Use accepted producer contracts.
Partial stays partial.

## 10. Data pipeline

node164 durable authority.

As soon as a large artifact closes locally:
staging -> ready -> .partial -> verify -> admit -> ACK.

Transfer may overlap independent work if safe.

Do not delete accepted V1/V2.1 data.

## 11. Solve-and-continue

Engineering issue: solve and continue.

Task-local scientific issue: freeze task, preserve evidence, continue independent queue.

Whole-goal STOP only for shared model/data authority failure or unsafe GPU identity/ownership.

## 12. Forbidden

No:
- new model download;
- DeepSeek/OLMoE bring-up;
- new TLB/PTW/cache mechanism;
- pointer-chase/cg expansion;
- repeated Decode32 structural sampling;
- software-stack upgrade unless required to restore exact already-accepted environment and proven neutral;
- unbounded NCU/NVBit sweep.

## 13. Durable output

Large:
`/root/share/mnt164/huangrulin/awma_109_native_workload_pipeline_20h_v1/`

Report:
`docs/vm_tlb/codex_handoff/awma/NATIVE_WORKLOAD_PIPELINE_20H_109_V1_REPORT.md`

Review pack:
`docs/vm_tlb/review_packs/AWMA_NATIVE_WORKLOAD_PIPELINE_20H_109_V1/`

Required:
- README.md
- SOURCE_ANCHORS.md
- PIPELINE_STATE.json
- EXISTING_FAMILY_NATIVE_RESOURCE_MATRIX.tsv
- all E1 files
- E3 files if executed
- opportunity receipts/results if executed
- detailed-capture selector decision
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Final 2h: no new target.

Then report -> pack -> hashes -> commit -> push -> remote verify -> clean -> release lock -> confirm idle -> STOP.
