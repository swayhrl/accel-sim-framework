# CODEX_NEXT_STAGE

Status: **ACTIVE — TRACK C + TRACK E; TRACK D WAITING**

Coordination branch:

`hrl/awma-174-local-storage-audit-handoff-v1`

Read first:

```text
docs/vm_tlb/chatgpt_handoff/awma/CURRENT_STATE.md
docs/vm_tlb/chatgpt_handoff/awma/DISCUSSION_REFERENCE.md
docs/vm_tlb/chatgpt_handoff/awma/STORAGE_GOVERNANCE_POLICY_V1.md
docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE.md
```

Then execute only the active node-specific specification.

## Track A — Q05 translation timeline — COMPLETE

Reported status:

`AWMA_Q05_TRANSLATION_TIMELINE_CLOSURE_V1_COMPLETE_WITH_SCOPE`

Do not restart it in this coordination stage.

## Track B — node109 target selection — COMPLETE / ACCEPTED

Accepted parent:

```text
hrl/awma-kernel-target-selection-109-v1
e90fd76d3704df4a367bb04de09aee42d0cab803
```

Its candidate identities are the only new simulator-native targets authorized for Track C.

## Track C — node109 producer storage governance + GPU side lane — ACTIVE

Continue the existing specification:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_109_STORAGE_GOVERNANCE_AND_GPU_SIDELANE_V1.md`

Strict order remains:

```text
Phase A: storage data-plane qualification
required gate: AWMA_164_DATA_PLANE_QUALIFIED_V1
then only if PASS
Phase B: bounded producer captures
```

Authorized target set only:

```text
PREFILL_GEMM_PRIMARY_1
DECODE_GEMV_PRIMARY_1
DECODE_FLASH_PRIMARY_1
DECODE_FLASH_PRIMARY_2
```

Track C may create producer-qualified durable bundles on node164. It may not create SIM_INPUT IDs or run Accel-Sim.

## Track D — 174-new durable-consumer audit — WAITING

Reported status:

`AWMA_174NEW_STORAGE_CONSUMER_AUDIT_V1_WAITING_FOR_PRODUCER_CANARY`

Its independent existing-data audit is complete. Do not rerun it.

When Track C producer canary receipt/ACK becomes visible, Track D needs only a small delta verification from 174-new:

```text
independent size/SHA read-back
+ receipt/ACK comparison
+ partial/final promotion check
+ catalog path check
```

Until then Track D stays stopped.

## Track E — 174-new local storage audit — ACTIVE

Execute:

`docs/vm_tlb/chatgpt_handoff/awma/CODEX_NEXT_STAGE_174NEW_LOCAL_STORAGE_AUDIT_V1.md`

Purpose:

- inventory actual local/host-backed storage usage from 174-new;
- exclude node164 remote durable storage from local totals;
- identify dominant directories/files/worktrees/builds/caches;
- determine whether local duplicates of accepted node164 data exist;
- classify cleanup candidates and estimate reclaimable bytes;
- perform no deletion or cleanup.

Recommended execution branch:

`hrl/awma-local-storage-audit-174new-v1`

This stage is read-only inventory. It must not alter Track C/D worktrees or any scientific result.

Expected completion:

`AWMA_174NEW_LOCAL_STORAGE_AUDIT_V1_COMPLETE_WITH_SCOPE`

## Storage roles

```text
109 = producer / short-lived local staging
174-new = simulator / analysis / worktree host
164 = durable large-data authority
```

Node164 root:

`/root/share/mnt164/huangrulin/c16_ai_workload/`

Existing accepted durable paths are provenance and must not be reorganized for cleanliness.

## Explicitly forbidden scope

Current tracks may not automatically start:

- new TLB/PTW/cache mechanisms;
- L2-TLB latency/PTW/walker/capacity/page-size/Segment sweeps;
- NCU/C16WARP1/Qwen3/DeepSeek campaigns outside Track C authorization;
- SIM_INPUT admission or Accel-Sim replay of new Track C bundles;
- deletion or reorganization of accepted node164 evidence;
- deletion/move/compression/pruning of 174-new local paths;
- `git clean`, `git gc`, `git prune`, `git worktree remove` or package/cache purge in Track E.

## Execution policy

Routine read-only inventory, parser, path, Git, and reporting problems are solve-and-continue.

Stop for review on:

- provenance contradiction;
- destructive-storage risk;
- local-only accepted scientific authority;
- dirty worktree with significant uncommitted scientific data;
- inability to distinguish node164 remote storage from local/host-backed storage;
- scientific identity conflict.

Each active track independently:

```text
finish scope
-> review pack
-> report
-> hashes
-> commit
-> push
-> remote verify
-> clean worktree
-> STOP
```

Track E must STOP before any actual cleanup. ChatGPT will review the candidate list first.
