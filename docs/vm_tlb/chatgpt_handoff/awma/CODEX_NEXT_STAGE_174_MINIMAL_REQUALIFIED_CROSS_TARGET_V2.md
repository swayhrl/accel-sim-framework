# CODEX NEXT STAGE — 174 Minimal Requalified Cross-Target Hit-Path Validity V2

Date: 2026-09-20

Mode:

`GOAL MODE / solve-and-continue / SCIENTIFIC REQUALIFICATION AUTHORIZED`

Node:

`174-new`

Stage:

`AWMA_174_MINIMAL_REQUALIFIED_CROSS_TARGET_HITPATH_V2`

Coordination branch:

`hrl/awma-mainline-reset-crossview-v2`

Read first:

1. `CURRENT_STATE.md`
2. `REVIEW_174_V4_INCOMPLETE_MATRIX_DECISION_2026-09-20.md`
3. `CROSSVIEW_JOIN_CONTRACT_V1.md`
4. `174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`
5. this Goal

Suggested execution branch:

`hrl/awma-174-minimal-requalified-cross-target-hitpath-v2`

## 0. Scientific reset

The historical V4 six-point lookup matrix is:

`PARTIAL_NOT_ADMITTED / SUPERSEDED`

Do not reconstruct it.

Do not rerun:

- 5/80
- 2/80
- 10/40
- 10/0

unless a later ChatGPT review explicitly requests them.

The V4 runtime-load forensic qualification remains valid.

## 1. Frozen repaired authority

Accepted repaired source/contract:

`a7110f789a2bc6761d8885a2ca5628b4acf50f69`

Accepted repaired runtime-load forensic anchor:

`c8657cf637c5b54a0f40135248ff1eabcfd66696`

Use the already-qualified target-only lookup-latency diagnostic semantics.

No new VM/TLB/cache functional semantics.

Before science, prove the actually loaded repaired core/runtime using the accepted V4 load-path procedure:

- ldd/readelf/build-id/SHA;
- repair marker;
- target-override marker/authority.

If an engineering rebuild is needed, rebuild only from the already-qualified repaired + lookup-override source authority.

## 2. Frozen target set

### T0 — Attention

`Q05_PREFILL_ATTN_FLASH`

Use isolated Q05 trace/input corresponding to the accepted repaired isolated authority.

Accepted external references:

```text
R0 isolated repaired = 1,654,548 cycles
I0 isolated repaired =   674,179 cycles
coverage              = 3,090,304/3,090,304 translated
```

### T1 — Prefill GEMM

`PREFILL_GEMM_PRIMARY_OCC0`

Producer authority:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Durable bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_prefill_awma-route-b-nvbit1771-sim-native_prefill-gemm-primary-occ0_20260918T052739Z_01540d931e17`

### T2 — Decode GEMV

`DECODE_GEMV_PRIMARY_STEP16`

Same producer authority.

Durable bundle:

`/root/share/mnt164/huangrulin/c16_ai_workload/raw/C16R_qwen-qwen2-5-0-5b-instruct_s2-text_decode_awma-route-b-nvbit1771-sim-native_decode-gemv-primary-step16_20260918T074437Z_b0dfb1af1ae1`

No target substitution.

## 3. T0 runtime-control gate

Run fresh:

`T0_ISOLATED_10_80_CONTROL`

Use natural repaired config:

`L1=10, L2=80`

Require:

- complete target terminal marker;
- exact accepted target identity;
- full target instruction/CTA completion;
- per-access coverage marker;
- all downstream admissions translated;
- untranslated=0;
- unobserved=0;
- post-ready violation=0 if available.

Expected deterministic cycle authority:

`1,654,548`

If the fresh control does not exactly reproduce the accepted isolated repaired R0 scientific metrics, STOP:

`STOP_SCIENTIFIC_T0_REPAIRED_RUNTIME_REPRODUCTION_MISMATCH`

Do not continue to 0/80 or T1/T2.

## 4. T0 minimal latency requalification

After T0 control PASS, run target-only:

### T0_ISOLATED_0_80
`L1=0, L2=80`

### T0_ISOLATED_0_0
`L1=0, L2=0`

Each point must satisfy the same terminal/coverage invariants as T0 control.

The accepted isolated I0:

`674,179 cycles`

is a reference only and does not need rerun.

Compute:

```text
T0_L1_ZERO_DELTA = cycles(10/80) - cycles(0/80)
T0_ZERO_ZERO_DELTA = cycles(10/80) - cycles(0/0)

T0_TOTAL_I0_GAP = 1,654,548 - 674,179
T0_L1_ZERO_FRACTION_OF_I0_GAP
T0_ZERO_ZERO_RESIDUAL_VS_I0 = cycles(0/0) - 674,179
```

Do not interpret these as hardware TLB latency.

## 5. T1/T2 input admission

For T1 and T2 separately:

1. validate producer bundle SHA/manifest;
2. identify accepted simulator-compatible trace member(s);
3. validate parser/terminal grammar;
4. bind target-specific SIM_INPUT identity;
5. no recapture.

If exact simulator input cannot be admitted without semantic changes:

`TARGET_NOT_ADMITTED`

Freeze that target and continue the other.

## 6. Common minimal matrix for T1/T2

For each admitted target run:

### 10/80 natural
`<TARGET>_10_80`

### 0/80
`<TARGET>_0_80`

### 0/0
`<TARGET>_0_0`

Every point requires:

- terminal completion;
- target identity;
- complete instructions/CTA;
- coverage marker;
- translated admissions == downstream admissions;
- untranslated=0;
- unobserved=0.

Do not assume Q05 admission count.

Do not run I0 for T1/T2 in this stage.

## 7. Metrics

Per point collect target-boundary deltas:

- cycles;
- gpu_sim_insn / target instruction completion;
- CTA completion;
- downstream admissions;
- translated/untranslated/unobserved;
- L1 accesses/hits/misses;
- L2 accesses/hits/misses;
- L1/L2 lookup launches/completions/service;
- MSHR alloc/merge/full/HWM;
- walks;
- PWC;
- PTE;
- requester latency;
- requester MSHR wait;
- L2 data accesses/misses.

## 8. Derived cross-target metrics

Per target:

```text
L1_HIT_RATE
L2_HIT_RATE_GIVEN_L1_MISS
WALKS_PER_1K_LOOKUPS
LOOKUPS_PER_MEMORY_INSTRUCTION_RECORD  (where Native descriptor available)
LOOKUPS_PER_1K_LANE_ADDRESSES          (where Native descriptor available)

L1_ZERO_DELTA_CYCLES
L1_ZERO_DELTA_FRAC_R0

ZERO_ZERO_DELTA_CYCLES
ZERO_ZERO_DELTA_FRAC_R0
```

T0 additionally reports I0-gap metrics from section 4.

## 9. Cross-view join

Join with accepted 109 Native export:

`hrl/awma-109-exact-target-native-crossview-v1 @ 2122eccc7aed61d05b114075e1c3126c4308e64b`

Use relation:

`EXACT_WORKLOAD_TARGET`

Do not fill Native UNAVAILABLE fields from simulator-side trace descriptors without explicit evidence-class labeling.

Create:

`CROSS_TARGET_REPAIRED_HITPATH_V2.tsv`

## 10. Scientific classification

At closeout classify only among:

- `HITPATH_SENSITIVITY_SYSTEMATIC_ACROSS_KERNEL_CLASSES`
- `HITPATH_SENSITIVITY_ATTENTION_DOMINANT`
- `HITPATH_SENSITIVITY_TARGET_DEPENDENT`
- `SIMULATOR_HITPATH_MODEL_REQUIRES_SEMANTIC_RECALIBRATION`
- `INSUFFICIENT_CROSS_TARGET_EVIDENCE`

Do not automatically choose mechanism work.

## 11. Historical V4 treatment

Create:

`V4_PARTIAL_MATRIX_SUPERSESSION.md`

It must state:

- runtime-load forensic qualification retained;
- repaired natural qualification retained where complete;
- six incomplete lookup points are PARTIAL_NOT_ADMITTED;
- no full V4 matrix publication claim survives;
- V2 minimal matrix supersedes V4 for mainline hit-path conclusions.

Do not delete old raw artifacts.

## 12. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/MINIMAL_REQUALIFIED_CROSS_TARGET_HITPATH_174NEW_V2_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_174_MINIMAL_REQUALIFIED_CROSS_TARGET_HITPATH_V2/`

Required:

```text
README.md
SOURCE_ANCHORS.md
RUNTIME_AUTHORITY.json
V4_PARTIAL_MATRIX_SUPERSESSION.md
TARGET_INPUT_AUTHORITY.tsv
TARGET_COVERAGE_INVARIANTS.tsv
TARGET_HITPATH_MATRIX.tsv
TARGET_DELTA_METRICS.tsv
CROSS_TARGET_REPAIRED_HITPATH_V2.tsv
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

## 13. Mandatory remote publication

Apply:

`174_MANDATORY_REMOTE_PUBLICATION_CONTRACT.md`

Before COMPLETE:

- node164 durable raw/receipt closure;
- commit;
- push;
- git ls-remote/fetch verification;
- remote HEAD == local HEAD;
- remote commit tree contains report + full review pack;
- SHA256SUMS verified;
- worktree clean.

Success:

`AWMA_174_MINIMAL_REQUALIFIED_CROSS_TARGET_HITPATH_V2_COMPLETE_WITH_SCOPE`

Then STOP.

No architecture mechanism.
