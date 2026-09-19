# AWMA 20h Unattended Pipeline Scheduler Policy V1

Date: 2026-09-19

Status: ACTIVE AFTER USER LAUNCH

Coordination branch:
`hrl/awma-20h-unattended-pipeline-handoff-v1`

## 1. Campaign model

Two independent solve-and-continue Goal lanes run concurrently:

- 174-new: repaired-VM requalification + CPU/simulator analysis.
- 109: native characterization + E1/E3 + opportunity queue.

Each lane records its own `START_UTC` and computes:

- `DEADLINE_UTC = START_UTC + 20h`
- `NO_NEW_SCIENTIFIC_TARGET_AFTER = DEADLINE_UTC - 2h`

The final 2 hours are reserved for safe closeout.

Goal success is scoped evidence closure, not 100% queue utilization.

## 2. Queue classes

- MANDATORY: required by the final scientific contract.
- CONDITIONAL: runs only after explicit gates pass.
- OPPORTUNISTIC: high-value work when mandatory work is closed or another resource is idle.
- DEFERRED: forbidden in this campaign.

No task may self-promote from DEFERRED.

## 3. Solve-and-continue

Engineering issues are solve-and-continue:

- build/path/parser/logging;
- bounded tool retry;
- missing derived metadata recoverable from accepted authority;
- transfer resume;
- correctness-neutral scripting fixes;
- exact consumer admission plumbing for an already accepted producer bundle.

Scientific issues are task-local STOP boundaries:

- target identity changes;
- model/input/hidden/route authority changes;
- accepted source semantics change;
- exact paired comparison cannot be preserved;
- result requires a new claim boundary;
- approximation would be needed to continue.

On task-local STOP:
1. freeze that task;
2. preserve evidence;
3. mark STOP_SCIENTIFIC;
4. continue only pre-authorized independent tasks.

Whole-lane STOP is required for shared source corruption, authority inconsistency, unsafe GPU ownership,
or a contract defect affecting all remaining work.

## 4. Resource rules

### GPU109

Exclusive via:
`/data/c16/locks/c16_gpu_campaign.lock`

Before GPU work:
- verify RTX4080 identity/UUID;
- inspect current owner;
- acquire lock normally;
- never kill/bypass a legitimate workload.

### CPU174

Simulator/analysis owner.
Large outputs go to node164.
Local storage remains bounded.

### node164

Durable large-artifact authority.
Accepted paths are immutable.

Publication:
`staging -> ready -> .partial -> size/SHA verify -> no-overwrite admit -> receipt/ACK`

## 5. Pipeline overlap

Allowed:
- transfer to 164 while independent CPU analysis runs;
- 174 analysis while 109 GPU work runs;
- next 109 GPU target after previous target has local closure and transfer pressure/storage are safe.

Forbidden:
- two GPU owners;
- two writers to one accepted 164 path;
- mutating one accepted worktree/source concurrently;
- detailed capture before its selector trigger is frozen.

## 6. Final two-hour reserve

No new GPU or simulator scientific target starts.

Allowed:
- complete safely closable running work;
- transfer/hash/admit/ACK;
- report/review pack;
- commit/push/remote verify;
- clean worktrees;
- release GPU lock.

Unclosable work becomes PARTIAL_NOT_ADMITTED.

## 7. Status vocabulary

Use:
`BLOCKED`
`READY`
`RUNNING`
`TRANSFER`
`ANALYZE`
`ACCEPTED`
`ACCEPTED_WITH_SCOPE`
`PARTIAL_NOT_ADMITTED`
`SKIPPED_GATE`
`SKIPPED_BUDGET`
`COUNTER_UNAVAILABLE`
`STOP_SCIENTIFIC`

## 8. 109 priority

1. 109-M0 existing-family native resource closure.
2. 109-M1 E1 shape x raw/AWQ diagnostics.
3. 109-C1 E3 N/P/U-active only if gates pass.
4. Opportunity queue:
   - G1 long-context then batch extension;
   - G2 same-quantized-weight implementation decomposition;
   - G3 profiler protocol sensitivity;
   - G4 Llama raw shape holdout.
5. Optional detailed capture only if pre-frozen trigger passes.

## 9. 174 priority

1. 174-M0 repair-authority materialization and telemetry-scope reconciliation.
2. 174-M1 minimal repaired Q05 requalification.
3. 174-O1 existing cross-family evidence analysis.
4. 174-C1 one non-Attention repaired R0/I0 screen if all gates pass.

## 10. Forbidden

- no new TLB/PTW/PWC/cache mechanism;
- no capacity/port/page-size/prefetch/speculation sweep;
- no lookup-constant calibration from RTX4080 native recon;
- no broad new model download;
- no DeepSeek/OLMoE bring-up merely to fill time;
- no repeated Decode32 sampling already structurally closed;
- no new pointer-chase/cg sweep without a new isolation method;
- no automatic full historical replay.
