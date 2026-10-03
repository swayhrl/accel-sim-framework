# START HERE — AWMA R27R2 / Lane G / node109

Date: 2026-10-03 (Asia/Shanghai)

Stage:
`AWMA_R27R2_TIED_WEIGHT_VARIED_BATCH_CAPACITY_STABILITY_109_V1`

Handoff branch:
`hrl/awma-r27r2-varied-batch-capacity-seeded-continuation-handoff-v1`

Fresh execution branch:
`hrl/awma-r27r2-varied-batch-capacity-109-v1`

Start from the **exact published handoff HEAD/tree in the launch message** and create a fresh isolated execution worktree.

This handoff is based on closed R27R1 execution:
`254d66f69ec81bf932add705f721f36255feef2c`
(tree `ebefec69e9ba153adfaf5d1f7860a956964d09cb`).

R27 and R27R1 remain COMPLETE / STOP. Do not resume or amend them.

Read in order:

1. `ACCEPTED_R27R1_REVIEW.md`
2. `SOURCE_SEED_AUTHORITY.json`
3. `LANE_G_R27R2_VARIED_BATCH_CAPACITY_109_GOAL.md`
4. `R27R2_EXPERIMENT_CONTRACT.json`
5. repository `AGENTS.md`

This is intentionally one merged Goal to reduce iteration overhead.

Execution flow:

`external exact seed validation + node164 admission`
→ `token bank construction + node164 bank authority`
→ `B1 B0/C1/S2 numerical/checkpoint/switch qualification`
→ `IMPLEMENTATION_FREEZE`
→ `bounded natural C1/S2 capacity search + 3/3 endpoints`
→ only if positive: `common-B + witness-B 32-step/resume/switch`
→ only if positive and genuinely needed: `one bounded allocator diagnostic pair`
→ publication/closure/STOP.

Important:

- Do **not** retry Hugging Face/network downloads. The seed is external to this Goal.
- Preferred seed path:
  `/data/c16/awma/r27_input_seed/train-00000-of-00001.parquet`
- Required exact seed:
  - 6,357,543 bytes
  - SHA256 `e83889baabc497075506f91975be5fac0d45c5290b6b20582c8cd1e853d0c9f7`.
- No tokenization until raw seed node164 admission/readback PASS.
- No CUDA/JIT until input/bank prerequisites PASS.
- All CUDA/JIT requires real `flock` on:
  `/data/c16/locks/c16_gpu_campaign.lock`.
- Passing gates continue automatically; do not return for routine approval.
- Ordinary pre-freeze engineering problems: solve-and-continue in this Goal and rerun only affected dependencies.
- Scientific identity/source/numerical/resource failure: STOP.
- After freeze, scientific behavior/data/classifier/tolerance changes: STOP/review.
- No formal timing campaign, profiler, 174/Accel-Sim, second corpus/model, hardware/PPA, all-parameter training or deployment.
- One final review pack / execution commit / node164 publication / final report, then STOP.
