# AI Workload Memory Analysis — ChatGPT → Codex Handoff

Official project name: **AI Workload Memory Analysis** (`AWMA`).

Chinese description: **AI负载访存分析与体系结构模拟**.

`C16` remains a historical campaign/namespace identifier. Existing run IDs, receipts, manifests, node164 paths and review packs are not renamed merely for cosmetics.

## Ownership

```text
chatgpt_handoff/  = ChatGPT-owned research coordination and execution specification
codex_handoff/    = Codex-owned execution reports
review_packs/     = Codex-generated review evidence
```

Codex must not silently redefine files in `chatgpt_handoff/`. If execution discovers a mismatch, preserve evidence, document it in the Codex report/review pack, and make only the narrowest safe adaptation consistent with the written scientific contract.

## Current canonical read order

For the active stage, Codex should read:

```text
1. CURRENT_STATE.md
2. DISCUSSION_REFERENCE.md
3. CODEX_NEXT_STAGE.md
4. the node-specific CODEX_NEXT_STAGE file selected by CODEX_NEXT_STAGE.md
```

Long-lived project contracts remain authoritative where applicable:

```text
PROJECT_CHARTER.md
PROCESS_AND_EXECUTION_RULES.md
IDENTITY_AND_EVIDENCE_CONTRACT.md
STORAGE_AND_CATALOG_CONTRACT.md
UNIFIED_ANALYSIS_ARCHITECTURE.md
```

Older `CODEX_NEXT_STAGE_*` files and `NEXT_WAVE_PLAN.md` are historical stage specifications unless the current `CODEX_NEXT_STAGE.md` explicitly reactivates them.

## Active stage

Current stage:

```text
AWMA_Q05_REPRESENTATIVENESS_AND_TRANSLATION_BEHAVIOR_V1
```

It has two parallel tracks:

```text
174-new:
CODEX_NEXT_STAGE_174NEW_Q05_FULL_TRANSLATION_BEHAVIOR_V1.md

109 / RTX4080:
CODEX_NEXT_STAGE_109_QWEN25_S2_KERNEL_CENSUS_V1.md
```

The stage is **pre-mechanism characterization**. Its purpose is to clarify the complete Q05 translation behavior and Q05's representativeness within the frozen Qwen2.5 workload before any new TLB/PTW mechanism experiment is authorized.

## Evidence planes

AWMA keeps two primary evidence planes distinct:

- **Native Evidence**: real-GPU NSYS/NCU/NVBit/C16WARP1 observations.
- **Simulation Evidence**: simulator-compatible trace plus Accel-Sim/GPGPU-Sim results.

A Cross-view conclusion is allowed only when identity and provenance are sufficient. Native C16WARP1/MREF evidence must not be silently converted into a simulator-compatible trace claim.

## Codex completion rule

Every active track must:

```text
execute only its allowed scope
produce a stage-specific report
produce an independently reviewable review pack
record raw-data indexes/hashes instead of committing large raw logs
commit
push
verify remote state
finish with a clean worktree
STOP at the written boundary
```

ChatGPT reviews the Codex reports and review packs before issuing the next scientific stage.
