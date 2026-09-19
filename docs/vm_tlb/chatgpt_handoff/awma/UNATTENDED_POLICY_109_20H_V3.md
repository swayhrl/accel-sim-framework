# AWMA 109 20h Unattended Solve-and-Continue Policy V3

Date: 2026-09-20

Stage:

`AWMA_109_20H_UNATTENDED_E1_E3_CHARACTERIZATION_V3`

## 1. Fresh clock

At actual Goal launch:

- `START_UTC = now`
- `DEADLINE_UTC = START_UTC + 20h`
- `NO_NEW_GPU_SCIENCE_AFTER = DEADLINE_UTC - 2h`

The final two hours are reserved for:
- transfer;
- node164 ACK;
- hashes;
- review pack;
- commit/push;
- remote verify;
- clean worktree;
- GPU lock release.

Do not inherit any older pipeline deadline.

If an external launcher exposes a stricter real deadline, record it explicitly and use the stricter boundary.

## 2. Goal-level stop policy

Do NOT stop the full Goal merely because:
- an E1 profiling selector fails;
- an optional metric is unavailable;
- E3 N/P/U harness qualification fails;
- one model asset path moved;
- a helper script does not exist;
- a prior authority needs materialization;
- one task reaches STOP_SCIENTIFIC.

Instead:
1. freeze that task;
2. preserve evidence;
3. mark its status;
4. continue the highest-priority independent READY task.

Whole-Goal STOP only for:
- wrong/unsafe GPU identity or lock ownership;
- shared repository/model/storage corruption affecting all remaining work;
- exact parent/source identity cannot be established for the stage;
- a newly discovered scientific contradiction invalidates the common experiment contract.

## 3. Engineering problems are solve-and-continue

Codex is explicitly authorized to implement or repair bounded experiment infrastructure when the scientific contract is already frozen, including:

- module replay scripts;
- NVTX ranges;
- profiler selector canaries;
- test-only MoE experts harness;
- data parsers;
- hash/receipt generation;
- node164 staging/transfer;
- runtime path recovery;
- deterministic route-construction scripts.

These are engineering tasks, not scientific STOPs, provided they do not change model/operator/backend semantics.

## 4. Scientific STOP examples

Freeze only the affected task if continuation would require:
- changing model revision;
- changing token/input authority;
- substituting a different semantic operator;
- changing expert math/backend/residency;
- inventing a new numerical tolerance from the result being tested;
- weakening P inverse-equivalence;
- calling synthetic routing natural;
- claiming deployment-level raw/AWQ timing is same-input quantization causality.

## 5. GPU lock

Use:

`/data/c16/locks/c16_gpu_campaign.lock`

Before every new GPU task family:
- verify RTX4080 identity;
- verify legitimate owner state;
- acquire lock normally.

Never kill/bypass another workload.

## 6. Task classes

- MANDATORY
- CONDITIONAL
- OPPORTUNISTIC
- DEFERRED

Task states:

`BLOCKED`
`READY`
`RUNNING`
`TRANSFER`
`ANALYZE`
`ACCEPTED`
`ACCEPTED_WITH_SCOPE`
`STOP_SCIENTIFIC`
`FAILED_ENGINEERING_UNRESOLVED`
`SKIPPED_GATE`
`SKIPPED_BUDGET`
`PARTIAL_NOT_ADMITTED`

## 7. Scheduler priority

1. Mandatory task that unblocks the most downstream work.
2. Mandatory task with short closeout.
3. Conditional task whose gate is already satisfied.
4. Opportunity tasks in predefined order.
5. Optional detailed capture last.

Do not prioritize a task because pilot results look positive.

## 8. Pipeline overlap

GPU tasks are physically serial.

CPU-side work may overlap GPU execution:
- parse previous results;
- prepare deterministic manifests;
- transfer closed artifacts;
- build review tables;
- inspect frozen source.

Do not mutate a runtime/source tree while a GPU task using it is running.

## 9. Artifact lifecycle

For large artifacts:

`staging -> ready -> .partial transfer -> destination size/SHA verify -> no-overwrite admit -> receipt/ACK`

Do not delete accepted prior evidence.

## 10. Early completion

The Goal may end before 20h only when:
- every mandatory/conditional task is accepted or has a justified task-local scientific STOP;
- every authorized opportunity is accepted, gated out, or no longer scientifically useful;
- no READY task remains;
- final closeout is complete.

Do not occupy the GPU solely to consume time.

Conversely, do not terminate after 10–30 minutes merely because one central task stops if independent READY work remains.
