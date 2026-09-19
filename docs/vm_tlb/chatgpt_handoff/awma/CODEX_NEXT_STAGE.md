# CODEX_NEXT_STAGE

Status: ACTIVE AFTER USER LAUNCH

Stage:

`AWMA_REPAIRED_HIT_PATH_AND_E1_AUTHORITY_V1`

Coordination branch:

`hrl/awma-hitpath-e1-authority-handoff-v1`

## Scientific state

Accepted repaired requalification:

`hrl/awma-repaired-vm-requalification-20h-174new-v1 @ a7110f789a2bc6761d8885a2ca5628b4acf50f69`

Accepted 109 scoped closure:

`hrl/awma-109-native-workload-pipeline-20h-v1 @ a271a0e57d3cb61ee878e686e6e517082a9f97df`

Mainline decision:

`REPAIRED_VM_PER_ACCESS_BASELINE_ACCEPTED_FOR_MODEL_RELATIVE_CHARACTERIZATION`

Timing provenance:

`NOT_HARDWARE_CALIBRATED`

Architecture mechanism:

`NOT_AUTHORIZED`

## Read in order

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. `POST_PIPELINE_REVIEW_DECISION_2026-09-19.md`
4. `NEXT_STAGE_ACCEPTANCE_CONTRACT_V1.md`
5. this dispatcher
6. exactly one node-specific Goal

## Track A — 174-new

Execute:

`CODEX_NEXT_STAGE_174NEW_REPAIRED_HIT_PATH_MODEL_VALIDITY_V1.md`

Suggested branch:

`hrl/awma-repaired-hitpath-validity-174new-v1`

Goal:

- close missing provenance artifacts without rerunning science where possible;
- run repaired P34 target-only lookup-latency envelope;
- audit hit-path model semantics;
- conditionally screen Prefill GEMM 10/80 vs 0/80.

Completion marker:

`AWMA_REPAIRED_HIT_PATH_MODEL_VALIDITY_174NEW_V1_COMPLETE_WITH_SCOPE`

## Track B — 109 / RTX4080

Execute:

`CODEX_NEXT_STAGE_109_E1_AUTHORITY_AND_MOE_DIAGNOSTICS_V1.md`

Suggested branch:

`hrl/awma-e1-authority-moe-109-v1`

Goal:

- recover exact common raw/AWQ S2 input/model/runtime authority;
- produce live q_proj/down_proj activation authority;
- close fresh module replay equivalence;
- run E1 M1/M256 deployment diagnostics;
- run Q30 E3 N/P/U-active independently of E1;
- use module-replay/NVTX selector canaries for any profiling.

Completion marker:

`AWMA_E1_AUTHORITY_AND_MOE_DIAGNOSTICS_109_V1_COMPLETE_WITH_SCOPE`

## Solve-and-continue policy

Routine engineering problems:
solve locally and continue.

Scientific task-local problem:
freeze that task, preserve evidence, continue independent authorized tasks.

A full lane stops only for shared source/model/authority corruption or unsafe resource ownership.

## GPU scheduling

109 owns one exclusive GPU lock:

`/data/c16/locks/c16_gpu_campaign.lock`

E1 and E3 are scientifically independent but physically serial.

## Storage

node164 remains durable large-data authority.

Use immutable admission with size/hash verification and ACK.

## Explicitly forbidden

No:

- TLB capacity/port redesign;
- PTW/PWC mechanism;
- page-size/segmentation mechanism;
- translation prefetch/speculation;
- cache mechanism;
- new model download/substitution;
- broad detailed trace campaign.

174 lookup-latency variants are model-validity diagnostics only.

## Completion

Each lane independently:

report -> review pack -> hashes -> node164 ACK where needed -> commit -> push -> remote verify -> clean -> release owned lock -> STOP.

Do not automatically enter a mechanism stage.
