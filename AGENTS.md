# AGENTS.md — DTC-L1 M5 Graphics Research Window

This branch is an **independent Framework-only M5.7/M5.8 research branch**. It must not modify or disturb the active compute Goal.

Branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

Base snapshot:

`e261cd7cfe0d7c5cdddb2624b62a28657aeacd86`

## Mandatory read order

1. `docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`
2. `docs/dtc_l1/m5/M5_BRANCH_OWNERSHIP.md`
3. `docs/dtc_l1/m5/M5_GRAPHICS_INDEPENDENT_WINDOW_HANDOFF.md`
4. `docs/dtc_l1/m5/M5_GRAPHICS_POST_COMPUTE_PLAN.md`
5. `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`
6. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
7. `docs/dtc_l1/implementation/M5_GRAPHICS_PATH_AUDIT.md`
8. `docs/dtc_l1/m5/handoffs/M5_G1_GRAPHICS_FEASIBILITY.md`
9. `docs/dtc_l1/chatgpt_handoff/CODEX_GRAPHICS_RESEARCH.md`
10. `docs/dtc_l1/codex_handoff/LATEST_GRAPHICS_RESEARCH_REPORT.md`

The active compute branch's `CURRENT_STATE.md` may be read as background, but this window must not write active compute branch files.

## Authorized scope now

Execute only:

`M5.7 Graphics Provenance -> M5.8 Graphics Path Recovery`

M5.7:

- resolve five thesis scene identities and glmark2 version/provenance;
- recover shader/model/texture/assets/options/resolution/vertex counts;
- exact vs reconstructed classification;
- hashes and source evidence.

M5.8:

Search source-backed routes in order:

1. original thesis/project simulator/artifacts/traces/scripts;
2. author/group historical releases/repositories;
3. historical graphics-enabled GPGPU-Sim/Accel-Sim forks/artifacts;
4. defensible direct graphics frontend integration;
5. source-backed shader/request trace/replay;
6. proxy only as supplemental non-formal evidence.

Do not stop because the current ready-made simulator is `UNAVAILABLE_WITH_CURRENT_INFRA`; that is only the starting result.

## Strict forbidden scope before compute freeze

Do not:

- modify `swayhrl/gpgpu-sim` Core;
- modify active Framework compute branch/worktree `hrl/decoupled-l1-exp-m5-v0`;
- modify active Core compute branch/worktree `hrl/decoupled-l1-m5-v0`;
- edit active compute `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`;
- kill/alter active Paper/Extended simulation jobs;
- start M5.9 graphics integration;
- run formal graphics Base/IO/OO figures;
- use a proxy as paper reproduction.

## Research-window outputs

Required:

- `docs/dtc_l1/m5/handoffs/M5_7_GRAPHICS_PROVENANCE.md`
- `docs/dtc_l1/m5/handoffs/M5_8_GRAPHICS_PATH.md`
- source/artifact/path evidence under `docs/dtc_l1/implementation/` or `docs/dtc_l1/m5/graphics/`
- `docs/dtc_l1/codex_handoff/LATEST_GRAPHICS_RESEARCH_REPORT.md`

Do not commit large recovered assets/traces/binaries if they are unsuitable for Git; record paths/hashes/provenance instead.

## M5.8 terminal state for this window

If source-backed path exists:

`M5_GRAPHICS_RESEARCH_READY_FOR_COMPUTE_FREEZE`

Provide an M5.9 implementation + directed-test plan, but do not modify Core.

If exhaustive routes fail:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

Preserve complete negative evidence. Do not manufacture a formal proxy.

## Git/worktree discipline

- use a dedicated worktree for this branch;
- never `git add .` or `git add -A`;
- explicit-path staging only;
- no force-push;
- do not merge the active compute branch repeatedly while research is running unless a researcher/ChatGPT handoff explicitly asks for a documentation refresh;
- preserve every source URL/commit/hash used in provenance claims.

## Problem behavior

Missing dependency/asset, source-search dead end on one route, compiler/shader conversion problem, or trace-parser issue is normally resolve-in-research. Continue through the ordered routes.

Pause only if a formal path would require changing frozen DTC semantics, using an approximation as formal graphics reproduction, or choosing between irreducibly different scientific timing/execution meanings.
