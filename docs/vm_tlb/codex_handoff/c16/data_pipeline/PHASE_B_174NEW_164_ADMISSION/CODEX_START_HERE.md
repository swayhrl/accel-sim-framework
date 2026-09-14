# Codex Start Here — Phase B 174-new / 164 Data Root Admission

Work only on:

```text
hrl/c16-174new-164-data-root-admission-v1
```

Read completely before acting:

```text
docs/vm_tlb/codex_handoff/c16/data_pipeline/PHASE_B_174NEW_164_ADMISSION/HANDOFF.md
docs/vm_tlb/chatgpt_handoff/c16/data_pipeline/DATA_ROOT_CONTRACT_V1.md
```

Primary objective:

> Admit `/root/share/mnt164/huangrulin/c16_ai_workload_2239` as the long-term C16 data root using isolated CPU/storage fixtures, create the persistent directory skeleton and header-only catalog, produce a non-secret receipt/review pack, then stop.

Before writing:

1. verify branch/HEAD and clean worktree;
2. inspect candidate root and mount read-only;
3. record capacity/filesystem/mount behavior without committing private endpoint information;
4. if unexpected pre-existing payload exists, preserve it and use a fresh isolated admission namespace or stop if collision is unsafe.

Allowed persistent writes are limited to the contract directory skeleton, a header-only catalog, a small data-root receipt, and admission metadata. Test payloads must be isolated and removed after validation.

Do not import RTX3090, RTX4080 R5, models, Qwen inputs, NCU/NVBit data, or any other scientific payload in Phase B.

Create the required review pack and decision exactly as specified in `HANDOFF.md`. Commit, push, and stop. Do not begin Phase C.
