# AWMA status after R27R3 numerical-attribution authorization

Date: 2026-10-13 (Asia/Shanghai)

This supersedes `STATUS_AFTER_R27R2_REVIEW_2026-10-13.md` **for current execution authorization only**. Previous scientific conclusions remain as accepted.

## Authorized, not yet executed

The user authorized a **single merged, gate-driven Lane G / node109 Goal**:

`AWMA_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_V1`

Handoff branch:
`hrl/awma-r27r3-numeric-attribution-capacity-handoff-v1`

Exact published handoff HEAD:
`29ce051f982f3854bd4392a94e4195c59340123b`

Tree:
`2813304af8d4f4c367f3be376a05530e336ccdba`

Expected fresh execution branch:
`hrl/awma-r27r3-numeric-attribution-capacity-109-v1`

Handoff entry:
[`START_HERE.md`](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/chatgpt_handoff/awma/r27r3_numeric_attribution_capacity_v1/START_HERE.md)

Full Goal:
[`LANE_G_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_GOAL.md`](https://github.com/swayhrl/accel-sim-framework/blob/29ce051f982f3854bd4392a94e4195c59340123b/docs/vm_tlb/chatgpt_handoff/awma/r27r3_numeric_attribution_capacity_v1/LANE_G_R27R3_NUMERIC_ATTRIBUTION_CONDITIONAL_CAPACITY_109_GOAL.md)

The handoff is based on the closed R27R2 execution commit `ba73fa0bacf3db09f44d8ad421a0a36f56645898`, tree `6988b03184c909123b6a8dfae082e07202cd808b`. Do not resume/amend R27R2. Publishing this handoff does **not** mean the new execution has started.

## Conditional one-round execution gates

1. **A — read-only evidence**: consume the exact accepted node164 varied-input parquet, `[33,128,128]` bank and R26 common CPU state; no redownload, re-tokenization or historic 95/207-item rerun. Read R27R2 fixed numerical failures/raw index and source.
2. **B — bounded B1 numerical attribution**: first check same-state B0-vs-B0 repeatability in two fresh processes, then fixed B1 step-0 (step-3 only if necessary) split lookup, classifier, merge and optimizer observables, recorded violating tensor locations. Maximum six pre-correction diagnostic GPU processes including the baseline controls.
3. **C — one localized correction if evidence supports it**: no blindly tuned correction family; unchanged math, loss, source/bank, BF16 tied W, FP32 optimizer, C1 default, S2 opt-in and no S2 full V×H GPU gradient/shadow. If root cause is unresolved or remedy requires a different contract, STOP.
4. **D — original fixed B1 four-step qualification**: B0/C1/S2 with original `rtol=atol=1e-2`, complete total gradients/W/m/v/dH/loss/step/cursor/next-loss and fresh checkpoint/switch. All checks must PASS; fail-closed shell status and `pipefail` required.
5. **E — only after D PASS: implementation freeze then bounded natural capacity**: same original B64 bracket, 3/3 adjacent endpoints, same-B C1-OOM/S2-PASS forward witness, valid UNKNOWN and right-censor outcomes.
6. **F — positive-only common-B and witness-B 32-step/resume**: continue automatically only for a stable forward witness.
7. **G — optional bounded allocator diagnostic**: at most one C1/S2 pair if positive and genuinely needed.
8. **Closure**: one publication, SHA/readback, exact Git commit/tree, GPU lock release and STOP.

Ordinary pre-freeze engineering repairs may be done in the same Goal. Do not infer numerical harmlessness from a small mean error or high cosine similarity; do not change tolerance, B0 reference, model, precision, source, optimizer or tile to force PASS.

## Scientific state and boundaries

- R26 accepted narrow capacity result: C1 B70 PASS/B71 OOM vs S2 B71 PASS/B72 OOM under repeated copies of one sequence, tied-W-only, 3/3, one physical batch.
- R27 and R27R1: exact-input availability STOP; no varied-input result.
- R27R2: exact new source/bank accepted, B1 B0-vs-C1/S2 numerical failure on all four varied steps, C1 moment failure at step 4, **no capacity observation**.
- R27R3: authorized **experiment**, not an accepted result; no promotion or conclusion until exact execution/raw is independently reviewed.

Only Lane G/node109 GPU is in the current AWMA scope. Its CUDA/JIT uses real `/data/c16/locks/c16_gpu_campaign.lock` flock. No independent Lane F or 174/Accel-Sim execution, new corpus/model, formal speedup campaign, production, all-parameter training or hardware/PPA is authorized. C16 Stage A and DTC-L1 remain independent projects.

If R27R3 cannot satisfy the unchanged numerical contract, STOP and preserve that finding; do **not** proceed to capacity. If it passes, continue within this same frozen Goal rather than splitting more authorization rounds.
