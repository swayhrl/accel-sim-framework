# M5 Graphics Research Closeout Approval

Status: **ACCEPTED — GRAPHICS_SOURCE_BACKED_UNAVAILABLE; NO M5.9-M5.11 FORMAL GRAPHICS EXECUTION**

Review date: 2026-09-04.

Reviewed graphics-research branch:

- Framework: `hrl/decoupled-l1-exp-m5-graphics-research-v0`
- reviewed closeout commit: `ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`
- research terminal state: `GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

This document is the researcher/ChatGPT review acceptance of the independent M5.7/M5.8 graphics-research result. It does not alter the frozen DTC architecture or the Paper/Extended compute experiment definitions.

## 1. Review verdict

The graphics-research closeout is accepted.

M5.7 established source-equivalent official glmark2 scene/asset lineages for four thesis labels while correctly refusing to overclaim exact identity:

- `jellyfish` -> source-equivalent `jellyfish` scene only;
- `cat-tex` -> source-equivalent `texture:model=cat:texture=crate-base` scene only;
- `cube-tex` -> source-equivalent `texture:model=cube:texture=crate-base` scene only;
- `horse` -> source-equivalent `build:model=horse` scene only;
- `2D-tex` remains `UNRESOLVED_NO_SUBSTITUTE` because the source-backed `effect2d` near-match uses an 800x600 texture rather than the thesis 128x128 asset.

The provenance evidence also preserves material mismatches instead of silently normalizing them. In particular, the recovered jellyfish source loads a main 256x256 texture plus a caustic sequence rather than simply matching the thesis table's two-256x256-texture description. This prevents an unjustified `EXACT_GRAPHICS_MATCH` claim.

M5.8 then audited the authorized path classes in order and found no source-backed route that satisfies the minimum semantic contract needed for a formal DTC graphics reproduction:

1. no original thesis/project graphics simulator, request trace, shader trace, run script, or missing 2D asset was recovered;
2. official glmark2 history supplies source/asset provenance but not the simulator/replay bridge;
3. surviving GPGPU-Sim `OPENGL_SUPPORT` is CUDA--OpenGL buffer interoperability, not an OpenGL shader/draw/frame frontend;
4. current Accel-Sim trace replay is CUDA SASS/NVBit oriented, not a five-scene glmark2 graphics capture/replay path;
5. no recovered candidate supplies shader-stage identity, graphics grouping, dynamic request identity, texture semantics, ordering/completion, draw/frame boundaries, framebuffer/fixed-function scope, and a comparable Base/IO/OO cycle definition together;
6. a memory proxy would therefore be supplemental only and cannot be promoted to paper graphics reproduction.

The result is appropriately bounded: it does **not** claim that an unknown future private/original artifact can never exist. A newly recovered artifact may reopen M5.8 only if it satisfies the explicit admission contract in `M5_8_GRAPHICS_PATH.md`.

## 2. Consequence for the active M5 roadmap

The graphics branch is now a completed evidence branch and should be treated as read-only unless genuinely new source material appears.

The current M5 path is therefore:

```text
Paper Compute:    M5.0B -> ... -> M5.6
Extended Compute: M5.E1 -> M5.E2 -> M5.E3
                     \       /
                      M5.COMPUTE_FREEZE
                              |
                              v
                 M5.12 negative-evidence synthesis
```

The following stages are skipped under the accepted negative closure:

- M5.9 Graphics Infrastructure;
- M5.10 Graphics Fidelity Pilot;
- M5.11 Formal Five-Scene Graphics.

Do not create graphics integration Core/Framework branches after compute freeze solely to restate this unavailable result.

## 3. Final reporting restrictions

Because no source-backed formal graphics execution/replay path exists:

- no formal graphics performance bars are emitted for Figures 4.2/4.5/4.7/4.8/4.10;
- no `GM-GRAPHICS` is emitted;
- no `GM-ALL-PAPER` is emitted;
- the four source-equivalent scene mappings and unresolved `2D-tex` are retained as provenance/negative-evidence documentation only;
- a calibrated proxy, if ever explored, must be labeled supplemental and must remain outside paper-reproduction aggregates.

The final compute-side reporting groups remain valid:

- `GM-PAPER10` / `GM-GP`;
- `GM-EXTENDED20`;
- `GM-ALL-COMPUTE30` supplemental generalization view.

## 4. M5.12 dependency after this closeout

M5.12 now requires only:

1. Paper-10 M5.6 PASS;
2. Extended-20 M5.E3 PASS;
3. `M5.COMPUTE_FREEZE` recorded with exact Core/Framework SHAs;
4. this accepted graphics closeout commit `ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d` referenced in the final review pack;
5. no unresolved compute correctness/fidelity issue.

After those conditions, M5.12 performs the final Chapter-4 compute/mechanism synthesis plus the explicit graphics-unavailability appendix and closes at:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

## 5. Reopening rule

Reopen graphics only if genuinely new original/source-backed evidence appears. Before any M5.9 authorization, the new artifact must satisfy the M5.8 reopening/admission contract, including immutable source/asset/trace hashes, shader-stage identity, grouping semantics, dynamic memory requests and spaces, ordering/completion, draw/frame boundaries, framebuffer/fixed-function scope, replay mapping, and a fair Base/IO/OO timing metric.

Absent such evidence, do not spend additional M5 simulation time attempting to force current CUDA-only infrastructure to stand in for the thesis graphics path.
