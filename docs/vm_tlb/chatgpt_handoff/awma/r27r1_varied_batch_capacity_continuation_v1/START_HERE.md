# START HERE — AWMA R27R1 / Lane G / node109

Date: 2026-10-03 (Asia/Shanghai)

Stage:
`AWMA_R27R1_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`

Handoff branch:
`hrl/awma-r27r1-varied-batch-capacity-continuation-handoff-v1`

Execution branch to create:
`hrl/awma-r27r1-varied-batch-capacity-109-v1`

Start from the **exact published handoff HEAD/tree in the launch message**, not from the old R27 execution branch directly.

The handoff branch was based on the accepted, closed R27 execution:
`4dca1cd713df8315b9e04f702d7f3b990c8f4b88`
(tree `03debf7395f51062c133ad4d534791f2b5fc1770`).

R27 itself remains COMPLETE / STOP with:
`R27_INPUT_OR_SOURCE_NOT_QUALIFIED`.

This is a new reviewed continuation because public source metadata still identifies the intended exact payload, but the previous execution environment could not acquire its bytes. The continuation must first obtain and durably admit the exact payload by byte size/SHA before tokenization or GPU use.

Read in order:

1. `ACCEPTED_R27_REVIEW.md`
2. `SOURCE_AUTHORITY.json`
3. `LANE_G_R27R1_VARIED_BATCH_CAPACITY_109_GOAL.md`
4. `R27R1_EXPERIMENT_CONTRACT.json`
5. repository `AGENTS.md`

Key control rules:

- Do not reopen or amend the old R27 execution branch.
- Gate A reuses accepted R27 parent-raw qualification after a bounded identity recheck; do not redo the entire 207-item audit unless a mismatch is discovered.
- Gate B0 exact-input acquisition/admission is CPU-only.
- No tokenization until the exact 6,357,543-byte parquet has SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7` and node164 readback passes.
- No CUDA/JIT before B0 admission and the Goal's prerequisites.
- Once GPU work is reached, all CUDA/JIT holds `/data/c16/locks/c16_gpu_campaign.lock`.
- Passing gates continue automatically in this single execution Goal.
- Scientific/source/identity/numerical/resource failure STOPs this Goal.
- Ordinary pre-freeze engineering defects may be solved and affected pre-freeze gates rerun.
- No alternate scientific payload, second corpus/model, profiler, node174/Accel-Sim, hardware/PPA, formal timing campaign or deployment.
- Publish one execution commit/review pack/final report and STOP for ChatGPT review.
