# C16 174-new Dual Restart V6

This handoff replaces the two problematic 174-new Codex windows with two **fresh, independent windows/worktrees**.

Do not resume or reuse the old Codex windows. Do not reuse their partially modified worktrees or branches unless only reading evidence from an accepted pushed commit.

## Window A — Mainline scientific analysis

Purpose: consume node109 V5 LDGSTS formal bundles and integrate them with the accepted Qwen0 direct-GLOBAL-MREF baseline.

Read and execute:

`CODEX_174NEW_MAINLINE_LDGSTS_ANALYSIS_DETAILED.md`

Suggested implementation branch:

`hrl/c16-ldgsts-analysis-174new-v6-r1`

Suggested worktree:

`/root/workspace/accel-sim-framework-c16-ldgsts-analysis-174new-v6-r1`

Base accepted 174-new analysis commit:

`1447bf9bb19bd249c116f53287a1f768170848c7`

Producer authority:

`ea43fa6331dcb2d7d6553f6a48000bdd004458e0`

## Window B — CPU-only asset/readiness preparation

Purpose: prepare canonical assets and Qwen2.5-7B raw semantically exact layer-replay metadata without starting any new model execution.

Read and execute:

`CODEX_174NEW_ASSET_READINESS_DETAILED.md`

Suggested implementation branch:

`hrl/c16-asset-readiness-174new-v6-r1`

Suggested worktree:

`/root/workspace/accel-sim-framework-c16-asset-readiness-174new-v6-r1`

Base accepted 174-new analysis commit:

`1447bf9bb19bd249c116f53287a1f768170848c7`

## Hard separation between the two windows

The two windows may run concurrently but must not share a worktree or implementation branch.

Both are CPU-only. Neither may run CUDA/model inference.

Window A may read accepted formal raw bundles and write derived analysis outputs/review evidence.

Window B may read canonical model/input/source receipts and lightweight checkpoint metadata, and may write compact readiness metadata/review evidence. It must not mutate formal raw, live catalog entries, or canonical model payloads.

No window may move/delete/rename node164 formal data or canonical model assets.

## Shared node164 root

Long-term root:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Important: existing admitted runs remain governed by their catalog entry and run manifest even if their current path uses the older `<root>/raw/<RUN_ID>` layout. Do not silently reinterpret them as `<root>/captures/raw/<RUN_ID>`.

## STOP discipline

Each window must produce its own hash-closed review pack, commit/push its own implementation branch, report branch/HEAD/final decision, and STOP independently.
