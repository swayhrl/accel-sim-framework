# CODEX NEXT STAGE — 109 Exact-Target Native Cross-view V1

Date: 2026-09-20

Mode:

`GOAL MODE / solve-and-continue`

Node:

`109 / RTX4080`

Stage:

`AWMA_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `CURRENT_STATE.md`
2. `EXECUTION_PRIORITY_POLICY_V2.md`
3. `CANDIDATE_SIDE_LANES.md`
4. `CROSSVIEW_JOIN_CONTRACT_V1.md`
5. this Goal

Suggested execution branch:

`hrl/awma-109-exact-target-native-crossview-v1`

## 0. Hard prerequisite: side-lane pause

Before taking the GPU for mainline:

- the active MoE causal-closure campaign must reach a safe pause;
- admitted partial candidate evidence must be durable;
- its paused state must be published remotely;
- `/data/c16/locks/c16_gpu_campaign.lock` must be released.

Expected pause marker:

`AWMA_109_MOE_CAUSAL_CLOSURE_PAUSED_FOR_MAINLINE`

Do not delete or overwrite partial MoE data.

## 1. Scientific objective

Provide bounded Native Evidence for the same exact kernel targets used by 174 cross-target simulation.

This is not a new workload-discovery campaign.

Question:

> What native workload/memory/resource regimes correspond to the exact targets whose repaired simulator hit-path sensitivity is being tested?

## 2. Frozen workload

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
```

No model/input/backend substitution.

## 3. Frozen target set

### T0
`Q05_PREFILL_ATTN_FLASH`

Exact accepted Q05 occurrence 0.

Reuse existing Q05 native producer/census evidence first.

### T1
`PREFILL_GEMM_PRIMARY_OCC0`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17`

Frozen producer facts:

```text
raw records                = 12,043,648
memory instruction records = 2,298,240
effective lane addresses   = 70,352,896
4 KiB pages                = 7,906
64 KiB pages               = 495
```

### T2
`DECODE_GEMV_PRIMARY_STEP16`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1`

Frozen producer facts:

```text
raw records                = 1,515,136
memory instruction records = 318,592
effective lane addresses   = 9,022,720
4 KiB pages                = 2,132
64 KiB pages               = 135
```

No target substitution after results.

## 4. Evidence-reuse first

Before any GPU run, inventory existing accepted evidence for T0/T1/T2:

- NSYS/kernel census;
- CUDA timing;
- Route-B producer receipt;
- page footprints;
- kernel launch/grid/block identity;
- prior NCU reports.

Create:

`EXISTING_NATIVE_EVIDENCE_INDEX.tsv`

Do not rerun a metric that already has adequate exact-target authority.

## 5. Exact native timing

Preferred authority order:

1. accepted existing exact-target native timing;
2. accepted exact NSYS kernel duration from the frozen full scenario;
3. one new lightweight frozen-scenario timing/census run only if required.

Do not replace real scenario timing with random/synthetic isolated inputs.

For any new timing:

- preserve exact workload;
- no NVBit detailed trace;
- retain raw samples/receipt;
- distinguish instrumentation timing from native timing.

Output:

`NATIVE_TARGET_TIMING.tsv`

## 6. Native footprint and dynamic-shape evidence

Reuse producer bundles.

For each target report:

- raw dynamic records;
- memory instruction records;
- effective lane addresses;
- CTA count;
- warp/CTA relationship;
- 4 KiB pages;
- 64 KiB pages;
- opcode/kernel-family fingerprint.

No recapture unless an accepted receipt is corrupt or missing.

## 7. Bounded NCU resource evidence

Purpose:

classify each target's native resource/traffic regime, not infer TLB latency.

First query installed NCU metrics.

Prefer available metrics covering:

- L1/TEX requested bytes/traffic;
- L2 requested bytes/traffic;
- DRAM bytes/traffic;
- achieved occupancy;
- SM activity;
- tensor/math activity;
- memory throughput;
- instruction/activity descriptors useful to distinguish Attention/GEMM/GEMV.

Use exact target selector/range canary.

Prefer application replay of the frozen scenario when practical.

If an exact selector cannot be established for a target after bounded engineering attempts:

`NCU_TARGET_SELECTOR_UNRESOLVED`

Keep its timing/footprint evidence and continue other targets.

Do not treat zero selected kernels as zero hardware traffic.

## 8. NCU protocol

Record:

- NCU version;
- selector identity;
- replay mode;
- cache-control setting;
- metric set;
- number of passes.

NCU timing is not native timing authority.

Cache control is not TLB flush.

## 9. Native target matrix

Create:

`NATIVE_EXACT_TARGET_MATRIX.tsv`

Rows:

- T0 Q05 Attention
- T1 Prefill GEMM
- T2 Decode GEMV

Required identity columns follow `CROSSVIEW_JOIN_CONTRACT_V1.md`.

Report explicit NA/UNAVAILABLE where needed.

## 10. Cross-view export

Create:

`CROSSVIEW_NATIVE_EXPORT.tsv`

Only include compact columns intended for later joining with 174.

Every row relation:

`EXACT_WORKLOAD_TARGET`

Do not add simulator results on 109.

## 11. Scope boundaries

Forbidden:

- new model download;
- MoE continuation;
- AWQ continuation;
- new broad NVBit capture;
- detailed SASS trace;
- new simulator-native recapture;
- architecture mechanism;
- interpreting NCU cache controls as translation controls.

## 12. Solve-and-continue

Routine engineering issues:

- selector;
- NSYS export;
- NCU metric names;
- parser;
- paths;
- receipts;

are solve-and-continue.

Scientific STOP only for target/workload identity change.

## 13. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/EXACT_TARGET_NATIVE_CROSSVIEW_109_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
EXISTING_NATIVE_EVIDENCE_INDEX.tsv
NATIVE_TARGET_TIMING.tsv
NATIVE_TARGET_FOOTPRINT.tsv
NATIVE_TARGET_NCU.tsv
NATIVE_EXACT_TARGET_MATRIX.tsv
CROSSVIEW_NATIVE_EXPORT.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Closeout:

- node164 durable receipt closure;
- commit;
- push;
- remote verify;
- worktree clean;
- release GPU lock.

Success:

`AWMA_109_EXACT_TARGET_NATIVE_CROSSVIEW_V1_COMPLETE_WITH_SCOPE`

STOP and return to ChatGPT.
