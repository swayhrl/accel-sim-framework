# START — C16 Full-Authority Recovery V3 V9 Goal

Use Goal mode. This v9 start supersedes v8 for the current task.

## Read-only handoff branch

```text
hrl/vm-c16-g-retry570-chatgpt-handoff-v9
```

## First action before normal R0-R9

Read and apply:

```text
docs/vm_tlb/codex_handoff/c16/retry570/C16_RECOVERY_V3_PRELAUNCH_ASSET_CONSOLIDATION_DELTA.md
docs/vm_tlb/specs/C16_FULL_AUTHORITY_RECOVERY_V3_MATRIX_V2.json
```

Perform one bounded asset consolidation pass for all in-scope models. Existing exact assets should be migrated/hash-closed under `/root/share/c16_recovery_v3` instead of redownloaded. Do not destructively move the only copy before destination closure. Keep the already-running Qwen2.5-0.5B exact fetch under `/root/share` running.

## Current user scope override

`Qwen3-30B-A3B` is **excluded from this task**. It is being downloaded separately under `/root/share/huangrulin`.

Do not:

- wait for that download;
- move or alter it;
- validate/package it;
- execute/profile/trace it;
- include it in completion denominators.

Record only:

```text
QWEN3_30B_A3B_STATUS=EXCLUDED_BY_USER_CURRENT_CAMPAIGN
```

Then continue all remaining in-scope Recovery V3 work through R9 without asking for stage-by-stage confirmation.

## In-scope roster

```text
Llama-3.2-1B                (S0 inherited; continue S1-S4)
Qwen2.5-0.5B-Instruct       (all required scenarios)
Qwen2.5-7B-Instruct raw     (all required scenarios)
Qwen2.5-7B-Instruct-AWQ     (all required scenarios)
Qwen3-8B                    (all required scenarios)
DeepSeek-V2-Lite            (S1/S2 required; optional only if stable)
GLM historical extension    (recover exact identity, then required scenarios)
```

## Continue to use the complete v8/v9 handoff set

After the delta and matrix-v2, read the inherited v8 files from this v9 branch:

```text
C16_FULL_AUTHORITY_RECOVERY_V3_MASTER_HANDOFF.md
C16_FULL_AUTHORITY_RECOVERY_V3_STAGE_ACCEPTANCE.md
C16_RECOVERY_V3_LOCAL_STORAGE_LAYOUT.md
C16_RECOVERY_V3_ASSET_TRANSFER_HANDOFF.md
C16_RECOVERY_V3_NATIVE_CENSUS_TARGET_PLAN_HANDOFF.md
C16_RECOVERY_V3_CAPTURE_COPYBACK_HANDOFF.md
C16_RECOVERY_V3_FINAL_DATASET_CLOSEOUT_HANDOFF.md
```

Where the old matrix or roster mentions Qwen3-30B-A3B, matrix-v2 and this v9 start override it for the current task.

## Problem-solving contract

Do not stop for ordinary engineering problems. Resolve network/download/cache/path/build/runtime/target/copyback issues with bounded evidence-preserving fixes and continue. Existing exact local assets must be preferred over redownloads.

All successful/partial raw and large payloads must end under `/root/share/c16_recovery_v3`, SHA closed, with `REMOTE_ONLY_REQUIRED_ARTIFACT_COUNT=0` at final closeout.

Preferred terminal status remains:

```text
C16_FULL_AUTHORITY_RECOVERY_V3_DATASET_COMPLETE
```

with Qwen3-30B-A3B reported as a user-authorized scope exclusion, not an exception or blocker.
