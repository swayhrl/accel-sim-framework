# Track B future start override — M4A-C full Goal mode

## Activation condition

This file is **not active while the current rented-host pilot is still running**.

It becomes the current Track-B authorization only when the pilot report closes with exactly:

`PILOT_PASS_READY_FOR_GOAL_CAPTURE`

If the pilot closes `PILOT_BLOCKED`, do not use this file.

## User authorization

After pilot PASS, the user explicitly authorizes switching Codex B to **Goal / 目标 mode** and running the full formal capture campaign continuously for the next several hours.

The active executable specification is:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_C_GOAL_CAPTURE.md`

This future-start file overrides stale `CODEX_NEXT_STAGE.md`, `M4A_READY_TO_RENT.md`, and the pilot stop-for-review wording **only after the pilot PASS activation condition is satisfied**.

## Goal

`formal prefill -> verified copy-back -> formal decode1 -> verified copy-back -> metadata/kernel validation -> parser/simulator compatibility -> M4A-C closeout -> STOP`

Codex must treat the stage gates as internal Goal checkpoints, not reasons to pause for routine human approval.

Ordinary environment/build/network/SSH/capture-wrapper/runtime problems should be diagnosed, minimally repaired, regression-checked, and execution resumed autonomously within the frozen-contract boundaries of `M4A_C_GOAL_CAPTURE.md`.

Hard semantic/hardware/model/trace-format boundaries remain STOP conditions.

The rented host must remain running and must not be deleted/shut down at Goal closeout until the user/ChatGPT reviews the copied artifacts.
