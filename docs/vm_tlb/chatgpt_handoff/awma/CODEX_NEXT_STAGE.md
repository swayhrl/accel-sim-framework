# CODEX_NEXT_STAGE

Status: ACTIVE AFTER USER LAUNCH

Stage:

`AWMA_20H_REPAIRED_REQUALIFICATION_AND_NATIVE_WORKLOAD_PIPELINE_V1`

Coordination branch:

`hrl/awma-20h-unattended-pipeline-handoff-v1`

## Scientific decision entering this stage

Repair authority:

`hrl/awma-vm-per-access-coverage-repair-174new-v1 @ 3f7bc0cd3cb3667b38fa0dd803ac034e19b493d6`

Decision:

`PER_ACCESS_VM_COVERAGE_DEFECT_CONFIRMED_REPAIR_QUALIFIED_FOR_REQUALIFICATION`

`MATERIAL_SCIENTIFIC_CHANGE_REQUIRES_MINIMAL_REBASELINE`

The repaired runtime is accepted for requalification only.
It is not yet the final research baseline.

## Read in order

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. `REPAIR_REVIEW_DECISION_2026-09-19.md`
4. `PIPELINE_ACCEPTANCE_CONTRACT_20H_V1.md`
5. `PIPELINE_SCHEDULER_POLICY_20H_V1.md`
6. this dispatcher
7. exactly one node-specific Goal below

## Track A — 174-new

Node:

`174-new / Simulation + analysis`

Execute:

`CODEX_NEXT_STAGE_174NEW_20H_POST_REPAIR_PIPELINE_V1.md`

Suggested execution branch:

`hrl/awma-repaired-vm-requalification-20h-174new-v1`

Primary work:
- rebuild/freeze repaired runtime and binary SHA;
- reconcile target-scoped telemetry;
- isolated/P8/P34 repaired Q05 requalification;
- cross-family existing-evidence analysis;
- conditional one non-Attention repaired R0/I0 screen.

## Track B — 109 / RTX4080

Node:

`109 / native GPU producer`

Execute:

`CODEX_NEXT_STAGE_109_20H_NATIVE_PIPELINE_V1.md`

Suggested execution branch:

`hrl/awma-109-native-workload-pipeline-20h-v1`

Primary work:
- close selected existing-family native resource evidence;
- E1 Qwen2.5-7B raw/AWQ shape x implementation;
- conditional E3 Q30 natural/P/U-active routing;
- bounded opportunity queue;
- optional detailed capture only if selector trigger passes.

## Solve-and-continue

Routine engineering problems are solved locally and execution continues.

A scientific problem freezes only the affected task when independent authorized tasks remain.

Stop a full lane only for a shared scientific/source/authority defect or unsafe resource ownership.

## Time

Each lane records its actual start time and uses:
- deadline = start + 20 hours
- no new scientific target in final 2 hours

Do not extend automatically.

## Storage

node164 remains durable large-data authority.

Use:
`staging -> ready -> .partial -> size/SHA verify -> no-overwrite admit -> receipt/ACK`

## Explicitly forbidden

No:
- new TLB/PTW/PWC/cache architecture mechanism;
- capacity/port/page-size/prefetch/speculation sweep;
- lookup-latency calibration from native pointer chase;
- broad model download/bring-up;
- automatic full historical replay.

## Completion

Each lane independently:

report -> review pack -> hashes -> commit -> push -> remote verify -> clean worktree -> release owned lock -> STOP.

Do not automatically enter a new scientific stage after completion.
