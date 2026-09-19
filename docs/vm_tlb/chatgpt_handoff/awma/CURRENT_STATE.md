# AWMA Current State

Date: 2026-09-19

## Main decision

The VM per-access coverage defect is confirmed and the surgical repair is qualified for requalification.

Accepted repair authority:

`hrl/awma-vm-per-access-coverage-repair-174new-v1`

`3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

Parent:

`be82faf264e93396b4b7d4fd72078c7e4491e3e4`

ChatGPT scientific review:

`PER_ACCESS_VM_COVERAGE_DEFECT_CONFIRMED_REPAIR_QUALIFIED_FOR_REQUALIFICATION`

`MATERIAL_SCIENTIFIC_CHANGE_REQUIRES_MINIMAL_REBASELINE`

The repaired runtime is not yet the final research baseline.

## Direct defect proof

Legacy P34 target-scoped downstream coverage:

- admissions = 3,090,304
- translated = 776,666
- untranslated = 2,313,638
- unobserved = 2,313,638

Repaired P34:

- admissions = 3,090,304
- translated = 3,090,304
- untranslated = 0
- unobserved = 0
- post-ready retranslation = 0

P34 target cycles:

`871,835 -> 1,619,068`

gpu_sim_insn:

`368,696,302 -> 368,696,302`

This is a material change. All old translation-dependent Q05 quantitative results remain historical legacy evidence pending repaired requalification.

## Scope caveat

The core coverage proof is target-kernel gated and accepted.

Some compact impact metrics are not yet proven target-only. The impact matrix reports walk_starts=499, while historical P34 target-only analysis used a different count. The next 174 stage must establish target-boundary deltas before auxiliary telemetry is compared.

Do not state that repaired Q05 has 499 target walks.

## Frozen workload

```text
model      = Qwen/Qwen2.5-0.5B-Instruct
revision   = 7ae557604adf67be50417f59c2c2f167def9a775
scenario   = S2_TEXT
batch      = 1
prefill    = 2048
decode     = 32
dtype      = FP16
backend    = SDPA
target     = Q05_PREFILL_ATTN_FLASH
```

Producer / Q05 identity / contiguous prefix / contextual replay / 109 V2.1 / lookup provenance / global-access determinism remain frozen.

## 109 accepted anchors

Selected producer campaign:

`8f49ba3b9228b5f8a9163e961225ffd415107734`

Contains accepted node164 bundles for Prefill Flash, Prefill GEMM Primary, and Decode GEMV Primary representatives.

V2.1 final:

`8a9d96ceb00e36ebdfa3d56cc277f965fffa649c`

Contains Decode Flash temporal/2D coverage and RTX4080 native TLB reconnaissance.

109 currently has no active AWMA task until the new 20h Goal is launched.

## New coordinated stage

`AWMA_20H_REPAIRED_REQUALIFICATION_AND_NATIVE_WORKLOAD_PIPELINE_V1`

Coordination branch:

`hrl/awma-20h-unattended-pipeline-handoff-v1`

Two solve-and-continue Goal lanes:

### 174-new

1. materialize/freeze repaired runtime and binary SHA;
2. reconcile target-scoped telemetry;
3. minimal repaired Q05 requalification:
   - isolated R0/I0
   - P34 R0/Q05-only I0
   - P8 R0
   - target timeline sanity
4. cross-family existing-evidence analysis;
5. optional one non-Attention repaired R0/I0 isolated screen.

### 109

1. close missing native resource characterization for selected existing families;
2. E1 Qwen2.5-7B raw/AWQ shape x implementation matrix;
3. conditional E3 Q30 natural/P/U-active MoE diagnostic;
4. opportunity queue:
   - long-context/batch extension;
   - same-quantized-weight execution decomposition;
   - profiler protocol sensitivity;
   - Llama raw shape holdout;
5. optional bounded detailed capture if selector trigger passes.

## Time policy

Each lane records actual start and uses a 20-hour deadline.
No new scientific target begins in the final 2 hours.

## Architecture mechanism

`NOT AUTHORIZED`

No TLB/PTW/PWC/cache mechanism, capacity/port/page-size/prefetch/speculation sweep is allowed in this stage.

## Durable storage

node164 remains large-data/model authority.

109 may retain active model replicas.
174-new remains source/simulator/analysis only with bounded local scratch.

## Execution documents

Read:
- REPAIR_REVIEW_DECISION_2026-09-19.md
- PIPELINE_ACCEPTANCE_CONTRACT_20H_V1.md
- PIPELINE_SCHEDULER_POLICY_20H_V1.md
- CODEX_NEXT_STAGE.md
- node-specific Goal file
