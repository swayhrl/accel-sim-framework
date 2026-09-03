# CODEX_GRAPHICS_RESEARCH

Status: **ACTIVE — INDEPENDENT M5.7/M5.8 GRAPHICS RESEARCH WINDOW**

## Branch/worktree

Work only on:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

Use a dedicated worktree. Do not enter or modify the active compute worktrees.

## Goal

Advance the thesis graphics reproduction as far as scientifically possible **without touching Core before compute freeze**.

Execute:

`M5.7 -> M5.8`

and stop this research window only at one of:

- `M5_GRAPHICS_RESEARCH_READY_FOR_COMPUTE_FREEZE`; or
- `GRAPHICS_SOURCE_BACKED_UNAVAILABLE`; or
- a genuine `RESEARCHER_DECISION_REQUIRED` semantic boundary.

## M5.7

Resolve the exact/source-equivalent identity of:

- jellyfish
- cat-tex
- cube-tex
- 2D-tex
- horse

Recover/reference:

- glmark2 version/tag/commit;
- exact scene/test invocation;
- shader sources;
- model/texture assets;
- resolution;
- vertex counts;
- texture dimensions;
- command/scene options;
- hashes/provenance.

Classify exact vs reconstructed properties. No silent scene substitution.

## M5.8

Do not simply repeat the prior `UNAVAILABLE_WITH_CURRENT_INFRA` conclusion.

Search in this order:

1. original thesis/project simulator, RTL/testbench, request/shader traces and scripts;
2. author/group historical repositories/releases/artifacts;
3. historical graphics-enabled GPGPU-Sim/Accel-Sim forks and published artifacts;
4. direct graphics frontend integration with real vertex/fragment/texture/frame semantics;
5. source-backed shader/request trace capture/replay preserving ordering/timing semantics;
6. proxy only as clearly supplemental non-formal work after formal routes fail.

For a candidate DIRECT/TRACE path prove or explicitly resolve:

- shader identity/stage;
- grouping/warp semantics;
- addresses/request sizes;
- global vs texture accesses;
- ordering/completion;
- draw/frame boundaries;
- framebuffer/fixed-function traffic scope;
- cycle/performance definition;
- how the same Base/IO/OO DTC model would be exercised.

## Forbidden

Do not:

- modify GPGPU-Sim Core;
- modify active compute Framework/Core branches;
- edit active compute `LATEST_REPORT.md`;
- kill/modify compute processes;
- start M5.9 integration;
- claim proxy graphics as paper reproduction;
- invent missing graphics semantics.

## Required outputs

Maintain:

- `docs/dtc_l1/m5/handoffs/M5_7_GRAPHICS_PROVENANCE.md`
- `docs/dtc_l1/m5/handoffs/M5_8_GRAPHICS_PATH.md`
- compact source/path evidence docs
- `docs/dtc_l1/codex_handoff/LATEST_GRAPHICS_RESEARCH_REPORT.md`

Commit/push compact evidence at meaningful checkpoints and continue automatically from M5.7 to M5.8.

Do not wait for compute M5.6 merely to do provenance/path research.
