# Codex new-window bootstrap — Qwen3-30B-A3B asset archive V2

## Goal mode

This is a self-contained execution task for a fresh Codex window. Do not rely on prior Codex chat context.

## Fetch

```text
branch:
hrl/c16-qwen3-30b-asset-archive-v1

expected handoff HEAD at task creation:
a7ec21f16e14a023a536df52bcfd347f842da49a
```

If the branch has advanced only because of subsequent ChatGPT handoff edits, consume the latest branch tip and report the actual starting SHA.

## Read in order

```text
1. docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
   CURRENT_STATE_BEFORE_Q30_ARCHIVE.md

2. docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
   QWEN3_30B_A3B_ASSET_ARCHIVE_GOAL_V2.md

3. For background only, if useful:
   docs/vm_tlb/chatgpt_handoff/c16/qwen3_30b/
   QWEN3_30B_A3B_4080_TRACE_PLAN_V1.md
```

The V2 archive Goal is authoritative for this execution round. The 4080 trace plan is future context and must not be executed now.

## Worktree isolation

Create a fresh execution branch/worktree.

Suggested branch:

```text
hrl/c16-qwen3-30b-asset-archive-exec-v2
```

Suggested worktree location:

```text
/root/workspace/accel-sim-framework-qwen3-30b-archive-v2
```

Do not modify closed historical worktrees or any active node109 experiment worktree.

## Primary source

Treat this entire root as the source discovery scope:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/
```

Known model-specific subtree:

```text
/root/share/huangrulin/c16_qwen3_30b_a3b/metadata/
Qwen__Qwen3-30B-A3B__ad44e777bcd18fa416d9da3bd8f70d33ebb85d39
```

Do not assume the subtree layout before inventorying the whole root.

## Destination

Canonical model:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/assets/models/
qwen3-30b-a3b/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/
```

Historical download provenance:

```text
/root/share/mnt164/huangrulin/c16_ai_workload/provenance/historical_snapshots/
qwen3_30b_a3b_download_v1/
```

## Execution behavior

Work autonomously through operational problems such as resumable copy, transient SSHFS I/O, stale-but-unambiguous `.partial` state, or large-file hashing. Diagnose and repair those without stopping for approval.

Do not weaken identity/integrity requirements. Required shard/index/config/tokenizer inconsistency is a real fail-closed condition.

Do not delete the source in this round.

Do not run the model or start any GPU profiling.

Do not provision the 61GB working copy to node109 in this round.

## Important quality checks

Do not stop at “all 16 files exist”. The review evidence must prove:

```text
source stability
+ whole-file SHA closure
+ receipt reconciliation
+ safetensors header readability
+ model.safetensors.index.json shard closure
+ tensor-key-to-shard header closure
+ exact config/tokenizer identity
+ source/destination independent rehash
+ complete accounting of every source regular file
```

Generated archive manifests/receipts must not contaminate the source-derived payload equality inventory.

## Required outcome

Expected successful final status:

```text
QWEN3_30B_A3B_CANONICAL_ARCHIVE_PASS
```

Required review pack:

```text
docs/vm_tlb/review_packs/
C16_QWEN3_30B_A3B_ASSET_ARCHIVE_V2/
```

Commit, push, report final branch/SHA/review-pack entry point, and STOP.

Do not continue into input binding or layer-streaming/replay work.
