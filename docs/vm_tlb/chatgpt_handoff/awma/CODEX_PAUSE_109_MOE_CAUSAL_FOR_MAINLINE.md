# CODEX PAUSE — 109 MoE Causal-Closure for AWMA Mainline Preemption

Date: 2026-09-20

Mode:

`SAFE PAUSE / PRESERVE EVIDENCE / RELEASE GPU`

Applies to the currently running:

`AWMA_109_MOE_CAUSAL_CLOSURE_AND_SCALE_PHASE_DIAGRAM_20H_V1`

Reason:

`AWMA_MAINLINE_PREEMPTION`

The campaign is a candidate side lane, not the active AWMA mainline.

## 1. Current known runtime state

User reports:

- C2 randomized interleaved schedule is frozen;
- 10 blocks;
- 22 conditions per block;
- background serial execution;
- each condition uses the same exact harness under the normal GPU lock;
- CPU-side source/component preparation may be running concurrently.

Do not discard already completed conditions/blocks.

## 2. Stop at the smallest safe checkpoint

Preferred:

- if the scheduler supports a checkpoint/pause marker per condition, request pause now and let the current condition finish;
- do not launch the next condition.

Fallback:

- if the scheduler cannot safely stop between conditions but checkpoints per block, let the current block finish;
- do not launch the next block.

Do NOT:

- kill a CUDA call mid-execution;
- corrupt a result file;
- delete a partially written artifact;
- continue merely to consume the original 20h budget.

## 3. Freeze partial state

Record:

- original campaign START/DEADLINE;
- pause-request UTC;
- actual stop UTC;
- last fully completed block;
- last fully completed condition;
- number of admitted condition measurements;
- frozen schedule SHA;
- degree-realization authority SHA(s) already materialized;
- GPU/runtime/model/harness authority;
- list of completed candidate artifacts;
- list of not-started/unfinished tasks.

Create:

`PAUSED_STATE.json`

Status:

`PAUSED_FOR_AWMA_MAINLINE`

This is not FAILURE and not COMPLETE.

## 4. Evidence admission

Completed measurements may be retained only if:

- the condition finished normally;
- receipt/output is complete;
- exact condition identity is known.

Anything interrupted or partially written:

`PARTIAL_NOT_ADMITTED`

Do not infer missing blocks.

## 5. CPU-side work

After GPU pause is requested:

- finish only the smallest CPU operation needed to make current evidence self-consistent;
- do not continue broad causal-closure analysis or prepare new GPU experiment families.

## 6. Durable closure

Store partial raw/results under the existing campaign durable root.

Create/update a compact review pack containing:

- PAUSED_STATE.json
- frozen schedule/seed authority
- admitted completed result index
- PARTIAL_NOT_ADMITTED entries
- raw-data paths/hashes
- SHA256SUMS

Do not relabel partial campaign results as final scientific conclusions.

## 7. Git publication

Publish the paused state remotely.

Preferred branch:

`hrl/awma-109-moe-causal-closure-scale-20h-v1`

If the local execution branch already has that name, push it.

If the branch name differs, publish the exact accepted pause commit under a stable ref and report it.

Required:

- local HEAD;
- remote HEAD;
- exact equality;
- remote tree contains pause state;
- worktree clean.

## 8. GPU handoff

After durable/Git closure:

- release `/data/c16/locks/c16_gpu_campaign.lock`;
- verify GPU returns to normal idle baseline;
- do not start another side-lane GPU task.

Final marker:

`AWMA_109_MOE_CAUSAL_CLOSURE_PAUSED_FOR_MAINLINE`

STOP and wait for the mainline 109 Goal.
