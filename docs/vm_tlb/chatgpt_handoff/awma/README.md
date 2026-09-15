# AI Workload Memory Analysis — ChatGPT → Codex Handoff

Official project name: **AI Workload Memory Analysis** (`AWMA`).

Chinese description: **AI负载访存分析与体系结构模拟**.

`C16` is retained as a historical campaign/namespace identifier. Existing Git paths, run IDs, receipts, manifests, node164 paths, and review packs that contain `C16` are not renamed merely for cosmetics.

## Read order

1. `PROJECT_CHARTER.md`
2. `CURRENT_STATE.md`
3. `PROCESS_AND_EXECUTION_RULES.md`
4. `UNIFIED_ANALYSIS_ARCHITECTURE.md`
5. `IDENTITY_AND_EVIDENCE_CONTRACT.md`
6. `STORAGE_AND_CATALOG_CONTRACT.md`
7. `CODEX_NEXT_STAGE_174NEW_AWMA_UNIFIED_FOUNDATION.md`
8. `NEXT_WAVE_PLAN.md`

## Simulation Analysis mainline

The dedicated Simulation Analysis plan is under:

```text
simulation_analysis/
```

Start with:

```text
simulation_analysis/README.md
simulation_analysis/CURRENT_STATE.md
simulation_analysis/EXECUTION_ROADMAP.md
```

The prepared executable specification is:

```text
simulation_analysis/CODEX_NEXT_STAGE_174NEW_SIMULATION_FOUNDATION.md
```

It is currently **planned, not active** while the existing Qwen Decode/analysis Goal is running on 174-new. Do not interrupt that Goal merely to start Simulation Analysis. Once activated, Simulation Analysis should advance mainly on 174-new/node164 without consuming 109 GPU time until simulator-compatible capture qualification is actually needed, allowing Native Characterization to continue independently.

## Ownership

The files in this directory are ChatGPT-owned coordination specifications. Codex should not silently redefine them. If implementation discovers a mismatch, preserve evidence, document the mismatch in the Codex report/review pack, and use the narrowest safe adaptation consistent with these contracts.

Codex owns execution reports under `docs/vm_tlb/codex_handoff/awma/` and review evidence under `docs/vm_tlb/review_packs/`.

## Purpose of this stage

This handoff starts the transition from the historical `C16` campaign namespace to a long-lived AWMA architecture without destructive renaming. The immediate objective is to establish one shared identity/catalog foundation for two evidence planes:

- **Native Evidence**: real-GPU NSYS/NCU/NVBit/C16WARP1 observations.
- **Simulation Evidence**: simulator-compatible trace + Accel-Sim/GPGPU-Sim results.

A third **Cross-view** layer joins the two only when identity/provenance is sufficient.

This stage is intentionally CPU/filesystem-only. It must not start new GPU capture or a production simulator campaign.