# Window C — SPECULATIVE M4B DEVELOPMENT current handoff

Status: `SPECULATIVE_CANDIDATE` / `REFERENCE_APPROX_SUBENTRY_16`. C9 architecture is frozen; C10-A/C10-A2 source/static implementation is complete. Window A C3 is formally terminal.

## authoritative identity

Framework branch: `hrl/vm-m4b-speculative-v0`

- pre-Goal Framework checkpoint: `70499d4790a0d3bd2158a23be7ae260af56f92de`
- C10-A2 evidence: `447ad52cf867e35a616fa16ab12e32b8914f50b9`
- C10-A2 Core: `12267bb7ed1dc0257d1d903f6baf7cbdc6ca550e`
- C9 architecture: `04be2899a19b1fe756956dbe5e459494ae1da8df`

## Window A terminal evidence

A publication checkpoint:

`14edbe200859f6ddf42bc3d459334f184a920a82`

records `C3_FINAL_STATUS = TERMINAL_PASS`, 8/8 terminal arms, and no active C3 simulator. Shared attestation begins with `A_TERMINAL_CONFIRMED`.

The old pre-terminal `C10B0_CONCURRENT_FOCUSED_COMPILE_CANARY` is superseded. The prior PSI `RESOURCE_DEFERRED` checkpoint is only a temporary resource observation, not the final C10-B state.

## Current authorized Goal

`C10B_CONTINUOUS_BUILD_RUNTIME_VALIDATION_GOAL`

Read and execute:

- `docs/vm_tlb/codex_handoff/spec_m4b/C10B_CONTINUOUS_GOAL.md`
- `docs/vm_tlb/codex_handoff/spec_m4b/C10B_CONTINUOUS_GOAL_ACCEPTANCE_MATRIX.md`
- existing `C10B_POST_A_TERMINAL_BUILD_AND_RUNTIME_VALIDATION.md`
- C9/C10-A/C10-A2 evidence packs

Goal mode continuously executes C10B-0 through C10B-5 and prepares C5 execution preflight. It does not launch full C5 performance replay.

Transient host pressure is a wait/retry condition, not a final stop. B/C heavy operations cooperate through:

`/workspace/vm_tlb_post_terminal_heavy_slot.lock`

Resource admission uses bounded PSI percentages rather than requiring exact-zero PSI deltas.

Ordinary compile/link/test/runtime/harness problems must be actively root-caused and repaired while preserving C9. Only genuine architecture/provenance/standard-correctness/evidence blockers may terminate the Goal.

Final Goal status:

- `C10B_READY_FOR_C5_RESOURCE_GATED_REPLAY`
- `C10B_HARD_BLOCKER_WITH_EVIDENCE`

Do not use `RESOURCE_DEFERRED` as a final status.