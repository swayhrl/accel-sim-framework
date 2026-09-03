# M5 Graphics Independent-Window Handoff

Status: **AUTHORIZED NOW — M5.7/M5.8 RESEARCH ONLY; M5.9+ WAITS FOR COMPUTE FREEZE**

Purpose: allow a second Codex window to advance graphics provenance and source-backed execution-path recovery in parallel with the active compute Goal without causing branch/worktree conflicts or invalidating compute evidence.

## 1. Research-window scope

The independent graphics window is authorized to execute:

- M5.7 — five-scene provenance closure;
- M5.8 — deep source-backed graphics path recovery.

It is not authorized to implement M5.9 graphics simulator/Core integration before `M5.COMPUTE_FREEZE`.

Existing `UNAVAILABLE_WITH_CURRENT_INFRA` evidence remains valid for the ready-made simulator, but M5.8 must search deeper before declaring graphics scientifically unavailable.

## 2. Dedicated branch/worktree

Use a Framework-only research branch/worktree:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

This branch is for source/artifact research, manifests, scripts that do not alter the active compute simulator, and handoff evidence.

Do not modify:

- active Framework compute branch/worktree `hrl/decoupled-l1-exp-m5-v0`;
- active Core branch/worktree `hrl/decoupled-l1-m5-v0`;
- Extended-20 selection branch;
- current compute raw jobs/processes/output directories.

No graphics-research Core branch is created at this stage.

## 3. Mandatory research order

### M5.7 — provenance

For `jellyfish`, `cat-tex`, `cube-tex`, `2D-tex`, and `horse`:

1. resolve thesis reference/version provenance;
2. map thesis names to exact/closest source-backed glmark2 scene/test invocations;
3. recover shader/model/texture/assets/options/resolution/vertex counts;
4. hash recovered source/assets;
5. distinguish exact from reconstructed/inferred properties;
6. do not silently substitute a visually similar scene.

Handoff:

`docs/dtc_l1/m5/handoffs/M5_7_GRAPHICS_PROVENANCE.md`

### M5.8 — execution-path recovery

Search in order and preserve evidence for each route:

1. original thesis/project simulator/artifacts/traces/scripts;
2. author/group historical repositories/releases;
3. historical graphics-enabled GPGPU-Sim/Accel-Sim forks or companion artifacts;
4. actual direct graphics frontend integration possibilities;
5. source-backed shader/request trace capture/replay with timing/order semantics;
6. calibrated memory proxy only as supplemental non-formal fallback.

Any proposed DIRECT/TRACE path must document at least:

- shader-stage identity;
- thread/warp/grouping semantics;
- memory addresses/sizes;
- global vs texture behavior;
- ordering/completion semantics;
- draw/frame boundaries;
- framebuffer/fixed-function scope;
- timing/performance metric definition;
- why Base/IO/OO would exercise the same DTC model fairly.

Handoff:

`docs/dtc_l1/m5/handoffs/M5_8_GRAPHICS_PATH.md`

## 4. Research-window terminal states

### Path found

If a source-backed path is established, end the research-only window at:

`M5_GRAPHICS_RESEARCH_READY_FOR_COMPUTE_FREEZE`

The handoff must include an implementation plan and directed-test plan for M5.9, but **do not modify Core yet**.

### Path unavailable

If original artifacts, historical simulator paths, direct integration, and source-backed trace/replay are exhaustively ruled out, end at:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

with complete negative evidence. Do not create a proxy and call it paper reproduction.

This unavailable result is later consumed by M5.12 after compute freeze.

## 5. After compute freeze

When the compute window produces `M5.COMPUTE_FREEZE`:

1. create fresh integration branches from exact freeze SHAs:
   - Core `hrl/decoupled-l1-m5-graphics-v0`
   - Framework `hrl/decoupled-l1-exp-m5-graphics-v0`
2. carry forward reviewed graphics-research evidence/commits without importing stale pre-freeze compute source state;
3. execute M5.9 -> M5.10 -> M5.11 if a source-backed path exists;
4. otherwise proceed to M5.12 negative-evidence synthesis.

## 6. Resource coordination

M5.7/M5.8 should primarily use source/artifact inspection and lightweight builds. It must not consume long simulator slots reserved for current Paper/Extended compute work.

Before any expensive compilation/capture/reconstruction, inspect current host CPU/RAM load and obey `M5_PARALLEL_BATCH_POLICY.md`.

## 7. Mutable-report ownership

The graphics research branch must not modify the active compute `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`.

Instead maintain:

`docs/dtc_l1/codex_handoff/LATEST_GRAPHICS_RESEARCH_REPORT.md`

on the graphics-research branch.

This avoids write conflicts between Codex windows.

## 8. Stop policy

Do not stop merely for a missing dependency, missing asset that can still be recovered, build failure, source-search dead end on one route, or trace parser problem. Continue through the ordered recovery routes.

Pause only if a proposed formal path would require changing frozen DTC semantics, using an approximation as formal graphics reproduction, or choosing between irreducible scientifically different timing/execution meanings.
