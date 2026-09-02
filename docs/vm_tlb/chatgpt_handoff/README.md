# ChatGPT → Codex Handoff

Ownership: **ChatGPT**.

Codex must read, in order:

1. `CURRENT_STATE.md`
2. `DISCUSSION_REFERENCE.md`
3. `CODEX_NEXT_STAGE.md`
4. the stage specifications referenced by `CODEX_NEXT_STAGE.md`
5. repository-root `AGENTS.md`

Codex must not modify files under `chatgpt_handoff/` unless the current executable specification explicitly authorizes that exact modification.

## Current authorization

The bootstrap has been reviewed. `CODEX_NEXT_STAGE.md` now authorizes two macro tracks:

- Track A: M1 → M2 → M3 single-GPU VM/TLB/PTW baseline.
- Track B: M4A LLM trace/metadata/paper-input preparation.

Detailed stage specifications live under:

`docs/vm_tlb/chatgpt_handoff/stage_specs/`

The target-paper extraction used by M4A lives under:

`docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md`

A chat message is not a replacement for these committed specifications. If the repository handoff and a chat instruction appear to conflict, stop and report the conflict before changing research semantics.
