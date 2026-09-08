# Window B — SPECULATIVE EXPERIMENT FARM current handoff

Status: `SPECULATIVE_DIAGNOSTIC`. B7/B8 analysis-only and B9 execution preflight are complete. Window A C3 is now formally terminal.

## authoritative identity

- Framework branch: `hrl/vm-spec-farm-v0`
- B9 evidence SHA: `b9119d4dfe0f8c04f432caa2b7974c3ccfc38152`
- Core branch baseline: `0d92e6aa8fd8bc885ffdf081a559bc616aaa85fd`
- simulator SHA-256: `2d6f825faf71e4aa9acc8d62e98186c9d7c1a92ecd2c41cbfd108e918de44915`
- scratch: `/workspace/vm-spec-farm/`

## Window A terminal evidence

A terminal publication checkpoint:

`14edbe200859f6ddf42bc3d459334f184a920a82`

It records `C3_FINAL_STATUS = TERMINAL_PASS`, 8/8 terminal arms, and no active C3 simulator. Shared attestation first line is `A_TERMINAL_CONFIRMED`.

The old `B10_CONCURRENT_E01_CANARY` was a pre-terminal safeguard and is now superseded. Do not execute it.

## Current authorized Goal

`B11_POST_TERMINAL_E01_E10_EXECUTION_GOAL`

Read and execute:

- `docs/vm_tlb/codex_handoff/spec_farm/B11_POST_TERMINAL_E01_E10_EXECUTION_GOAL.md`
- `docs/vm_tlb/codex_handoff/spec_farm/B11_ACCEPTANCE_MATRIX.md`
- the complete B9 execution pack

B11 runs the frozen E01–E10 set and synthesizes the results. It is Goal mode: transient resource pressure is a wait/retry condition, not a final stop.

Resource admission uses bounded PSI percentages rather than requiring exact-zero PSI deltas. New B/C heavy steps cooperate through:

`/workspace/vm_tlb_post_terminal_heavy_slot.lock`

Effective B heavy concurrency remains 1. Do not manipulate Window A/C processes to obtain resources.

Engineering failures must be actively diagnosed and repaired when possible without changing frozen experiment semantics. Only provenance/semantic/evidence hard blockers may terminate the Goal.

Final B11 status is either:

- `B11_E01_E10_COMPLETE_READY_FOR_REVIEW`
- `B11_HARD_BLOCKER_WITH_EVIDENCE`

Do not execute E11–E18 in B11.