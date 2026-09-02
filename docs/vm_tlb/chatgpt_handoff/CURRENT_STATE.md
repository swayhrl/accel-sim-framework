# Current state

Stage: `S1_B0_BOOTSTRAP_REVIEWED`

## Source anchors

- Core baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- Framework baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- Framework branch: `swayhrl/accel-sim-framework@hrl/vm-core-v0`
- Core project repository: `swayhrl/gpgpu-sim`
- Core project branch: `hrl/vm-core-v0`

## Bootstrap review

S1-B0 is accepted as `CONDITIONAL_PASS` on its original evidence: the clean baseline builds and both QV100 and unchanged RTX3070 trace smoke runs pass; no simulator behavior was changed.

The original blocker was the lack of a verified writable Core remote in the local Core worktree. During ChatGPT review, GitHub access verified that `swayhrl/gpgpu-sim` exists, is writable by the project account, contains the frozen Core baseline commit, and now has remote branch `hrl/vm-core-v0` created from exactly that baseline.

Therefore the repository-level provenance blocker is resolved. Before the first Core source modification, Codex must configure/verify the local Core worktree remote against `swayhrl/gpgpu-sim` and confirm that pushes target the project fork rather than the official upstream.

## Baseline VERIFIED_RUN

- Standard clean build: PASS.
- Rodinia LUD-64/QV100 trace smoke: PASS.
- Same trace with unchanged SM86/RTX3070 config: PASS.

See `docs/vm_tlb/review_packs/S1_B0_BOOTSTRAP/` for original commands and provenance.

## Agent guardrails

Project guardrails are now committed in root `AGENTS.md` in both Framework and Core research branches. These guardrails are authoritative for future Codex target-mode work together with the current ChatGPT handoff.

## Frozen direction

1. M1: VM-Core Foundation.
2. M2: Functional single-GPU TLB/MSHR/PTW pipeline.
3. M3: timing-realistic PTE/L2/DRAM translation baseline.
4. M4 may prepare LLM trace/metadata/paper evidence in parallel, but must not modify or destabilize M1–M3 semantics without explicit authorization.
5. Segmentation reproduction follows only after the required baseline pieces and LLM inputs are validated.

## Current authorization

No M1–M4 implementation is authorized by this file alone. `CODEX_NEXT_STAGE.md` remains the executable authorization boundary.
