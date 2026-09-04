# Track B current start override — local Llama snapshot resume + Goal mode

This file is the current Track-B authorization and overrides the earlier HF-token-only P5 resume wording and the historical `GOAL_BLOCKED` admission result.

## User-confirmed situation

The user now has a complete local copy of the frozen Llama-3.2-1B model on the main development server and wants to power the retained AutoDL instance back on and continue capture.

Main-server candidate model path:

`/workspace/model/meta-llama__Llama-3.2-1B_main`

Existing local integrity/staging records:

- `/workspace/m4a-rented-host-pilot/pre-shutdown/20260902T140525Z/LOCAL_MODEL_INTEGRITY.md`
- `/workspace/m4a-rented-host-pilot/pre-shutdown/20260902T140525Z/REMOTE_MODEL_STAGING.md`

Previous pilot P1-P4 remain accepted evidence, subject to cheap power-on sanity rechecks. The earlier P5 blocker was only remote gated-model credential availability.

## Active executable specification

Read and execute:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_LOCAL_MODEL_RESUME_GOAL.md`

The local snapshot route replaces the requirement for the rented host to authenticate to Hugging Face, provided Codex independently verifies the staged snapshot against the main-server source and forces local-only loading.

## Goal-mode authorization

The user explicitly authorizes Codex B to run this task in **Goal / 目标 mode**.

After power-on, execute the local-model resume gates continuously:

`R0 retained-host recovery -> R1 verified model staging -> R2 local-loader support -> R3 TP4 no-trace smoke -> R4 diagnostic decode1 pilot/copy-back/parser`.

If those gates close the pilot as:

`PILOT_PASS_READY_FOR_GOAL_CAPTURE`

continue immediately, without waiting for another human approval, into the formal M4A-C Goal:

`formal prefill -> verified copy-back -> formal decode1 -> verified copy-back -> metadata/classification -> parser/simulator compatibility -> closeout`.

Ordinary diagnosable environment/SSH/rsync/wrapper/runtime issues should be repaired autonomously inside the frozen research boundaries. Do not stop merely because the old Goal report says `GOAL_BLOCKED`; this new handoff explicitly authorizes reopening admission after the new local-model provenance gate passes.

Hard semantic/hardware/model/trace-format boundaries in the stage spec remain STOP conditions.

Do not shut down/delete the rented instance at closeout until the user/ChatGPT reviews the copied results.