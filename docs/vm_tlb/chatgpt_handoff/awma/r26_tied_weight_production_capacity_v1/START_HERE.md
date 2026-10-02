# START HERE — AWMA R26 / Lane G / node109

Date: 2026-10-02 (Asia/Shanghai)

Stage: `AWMA_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_BOUNDARY_109_V1`

Handoff branch: `hrl/awma-r26-tied-weight-production-capacity-handoff-v1`

Create execution branch/worktree: `hrl/awma-r26-tied-weight-production-capacity-109-v1`

Start from the exact published handoff HEAD in the accompanying launch message.
Handoff Git parent is R25 execution:
`2581b6592e79691c4c3e57fe31a339eba9f6b7dd`.
Scientific review/state parent:
`b2ba7f67a46e95ba45073c2a4deb54ee83a5401a`.

## Current authorization

The user accepted the next production-integration + real capacity-boundary step
after R25 review. This handoff authorizes one bounded node109 Goal. It does not
say that node109 has already started running it.

Only Lane G may use the GPU for this AWMA stage. R25/R24/R23G are COMPLETE/STOP,
F/R22F1 and E/R22E remain STOP, and R20 remains CLOSED. No node174/Accel-Sim or
hardware work is authorized.

Read completely, in order:

1. `ACCEPTED_R25_REVIEW.md` — verbatim review snapshot from the scientific parent.
2. `PARENT_AUTHORITY.json` — exact source/data identities and hashes.
3. `LANE_G_R26_TIED_WEIGHT_PRODUCTION_CAPACITY_109_GOAL.md` — complete contract.
4. `R26_EXPERIMENT_CONTRACT.json` — machine-readable frozen constants and outcomes.

The latest R26 Goal is the task-specific entry. Root
`chatgpt_handoff/CURRENT_STATE.md` / `CODEX_NEXT_STAGE.md` contain historical
M4 authorization and do not restart M4 or override this AWMA stage. Preserve
their historical contents. General AGENTS provenance, ownership, worktree,
validation, and closure rules still apply.

## What changes from R25

- Integrate C1 and S2 into one explicitly scoped tied-weight training component.
- C1 is its default memory policy; S2 is an explicit capacity opt-in.
- Use the accepted Llama model and token IDs; context remains 127 shifted positions.
- Increase only physical batch by repeating that exact frozen sequence.
- Qualify 32 consecutive optimizer steps and save/load/resume consistency.
- Freeze implementation before a bounded natural-OOM batch search.
- Compare complete-step feasibility; target allocator deltas alone do not pass.
- Reconfirm a same-batch C1-OOM/S2-PASS witness if one exists.

This is tied-weight-only fine-tuning/integration validation. It is not all-parameter
training, a diverse-data training-quality study, a new holdout, or deployment.

## Solve and continue

Ordinary path/manifest/derived-artifact, API, lifetime, and integration bugs may
be fixed within the authorized scope before implementation freeze. Requalify
after code changes. Do not open a separate repair Goal for a small engineering
issue. True authority, numerical, arm-identity, resource, or scope failure is a
scientific STOP. Natural CUDA OOM during the capacity search is an expected
measurement outcome, not by itself a scientific STOP.

All CUDA/JIT activity holds:
`/data/c16/locks/c16_gpu_campaign.lock`.

Publish code, review pack, immutable node164 raw/receipts, exact result commit,
fetch-back verification and clean-process/lock closure, then STOP.
Do not tune R25 or begin a later stage.
