# START HERE — AWMA R27 / Lane G / node109

Date: 2026-10-03 (Asia/Shanghai)

Stage: `AWMA_R27_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`

Handoff branch: `hrl/awma-r27-varied-batch-capacity-handoff-v1`

Create isolated execution branch/worktree:
`hrl/awma-r27-varied-batch-capacity-109-v1`

Start from the **exact published handoff HEAD and tree in the launch message**. The Git parent of this handoff is R26 execution
`1a2485011b300cddd5137bbccb91dd6d30cfc22f`
(tree `cce37bbbd368b545bea92c7b86cb429d8da4f48b`).
The accepted R26 review is `097c2b6ed7905480ed72679f0cc79865087ae3c9`.
Do not branch from either parent directly after the handoff is published.

Read completely in order:

1. `ACCEPTED_R26_REVIEW.md` — exact accepted scientific review snapshot.
2. `PARENT_AUTHORITY.json` — R26 raw archive, common state, source/model and new dataset hashes.
3. `LANE_G_R27_VARIED_BATCH_CAPACITY_109_GOAL.md` — authoritative bounded Goal and STOP rules.
4. `R27_EXPERIMENT_CONTRACT.json` — machine-readable constants, gates and outcomes.
5. `AGENTS.md` — repository ownership, Git/worktree and review-pack requirements.

The task-specific Goal/contract supersede historical M4 root handoff text for this stage. Preserve those old files. The user authorized this **one** gated Lane G/node109 Goal. Gate A is CPU-only readback of R26 raw endpoint evidence. When it passes, continue in the same execution branch to fixed WikiText-2 train input preparation, component qualification, natural capacity search, and positive-only 32-step/resume. Do not ask for a new approval between gates that pass. Ordinary pre-freeze implementation fixes remain in this Goal; scientific identity, numerical, raw-authority or resource failure is STOP.

Only Lane G may use node109 CUDA under `/data/c16/locks/c16_gpu_campaign.lock`. No GPU task has been started by publishing this handoff. R26/R25/R24/R23G are COMPLETE/STOP; Lane F and E remain STOP; R20 CLOSED. No node174/Accel-Sim, profiler, hardware/PPA, new model, training-quality, all-parameter or deployment authorization.

The only new network input allowed by this Goal is the exact 6,357,543-byte pinned WikiText-2 *train* parquet in `PARENT_AUTHORITY.json`. Its SHA must match before tokenization. Do not download or replace model weights/tokenizer, choose another corpus, or use validation/test. The exact R26 CPU common checkpoint is now available on node164; use it rather than another B0 derivation.

Deliver one execution commit/review pack, node164 raw/checkpoint manifest with readback, lock/process cleanup and final report at
`docs/vm_tlb/codex_handoff/awma/r27_varied_batch_capacity_v1/LANE_G_FINAL_REPORT.md`.
Then STOP for scientific review. No next stage starts automatically.
