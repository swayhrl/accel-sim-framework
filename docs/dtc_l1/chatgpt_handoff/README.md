# ChatGPT → Codex Handoff

Ownership: **ChatGPT**.

Codex must read, in order:

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. `CODEX_NEXT_STAGE.md`

Then read the core architecture specification:

`swayhrl/gpgpu-sim@hrl/decoupled-l1-v0:docs/dtc_l1/DTC_L1_SPEC.md`

Codex must not modify files in this directory unless the current stage explicitly authorizes it.

- `CURRENT_STATE.md`: authoritative coordination state and frozen decisions.
- `DISCUSSION_REFERENCE.md`: research rationale, interpretations, and rejected alternatives.
- `CODEX_NEXT_STAGE.md`: the only executable stage specification.

If there is a conflict, report it and STOP rather than choosing silently.
