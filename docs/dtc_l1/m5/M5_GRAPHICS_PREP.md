# M5 Graphics Preparation Track

Status: **ACTIVE PARALLEL PREPARATION; POST-COMPUTE EXECUTION AUTHORIZED**

Authority:

- `M5_V1_APPROVAL.md` + `M5_EXPERIMENT_MATRIX.md` for compute-era G0-G2 preparation;
- `M5_V2_GRAPHICS_CONTINUATION_APPROVAL.md` + `M5_GRAPHICS_POST_COMPUTE_PLAN.md` for post-M5.6 graphics recovery/execution.

The thesis uses five glmark2 graphics workloads in Table 4.1. Current M1-M4/M5 compute infrastructure has not established a source-backed end-to-end graphics path. Graphics work therefore has two phases:

1. nonblocking preparation while compute M5 runs;
2. a deeper post-compute recovery/execution track after M5.6 freezes compute results.

Thesis workload identities/settings:

| Workload | Vertices | Texture | Resolution |
| --- | ---: | --- | --- |
| jellyfish | 13200 | 2 x 256 x 256 | 800 x 600 |
| cat-tex | 43044 | 512 x 512 | 800 x 600 |
| cube-tex | 36 | 512 x 512 | 800 x 600 |
| 2D-tex | 4 | 128 x 128 | 256 x 256 |
| horse | 21516 | none | 800 x 600 |

## G0 — Thesis/glmark2 provenance preparation

Resolve thesis reference [78], scene/test names, source version, assets, shader sources, invocation, vertex/texture/resolution settings, and hashes. Do not silently substitute visually similar scenes.

Handoff:

`handoffs/M5_G0_GRAPHICS_PROVENANCE.md`

## G1 — Current-infrastructure feasibility audit

Audit direct graphics frontend, CUDA/OpenGL integration, shader/texture/fixed-function execution, trace capture/replay, ordering, framebuffer/completion semantics, and whether existing traces can faithfully represent graphics DTC traffic.

Classification vocabulary:

- `DIRECT_SOURCE_BACKED`
- `TRACE_SOURCE_BACKED`
- `CALIBRATED_MEMORY_PROXY`
- `UNAVAILABLE_WITH_CURRENT_INFRA`

Current evidence has closed G1 as `UNAVAILABLE_WITH_CURRENT_INFRA`: the ready-made active simulator does not provide direct glmark2 execution or a source-faithful graphics request replay path.

This is **not** the post-compute terminal conclusion. After M5.6, M5.8 is authorized to search more deeply for original thesis/project artifacts, historical graphics-enabled simulator support, defensible direct integration, or source-backed trace/replay infrastructure.

Handoff:

`handoffs/M5_G1_GRAPHICS_FEASIBILITY.md` plus `implementation/M5_GRAPHICS_PATH_AUDIT.md`.

## G2 — Opportunistic preparation while compute runs

If a source-backed path or useful provenance material is discovered before compute closeout, prepare build/capture/replay scripts, source/asset hashes, and candidate manifests without modifying the compute FORMAL behavior anchor.

Do not force a proxy into paper results.

## Post-compute continuation

After M5.6, follow:

`M5_GRAPHICS_POST_COMPUTE_PLAN.md`

Sequence:

`M5.7 provenance closure -> M5.8 deeper path recovery -> M5.9 infrastructure -> M5.10 pilot -> M5.11 formal five-scene runs -> M5.12 synthesis`

Use:

`M5_GRAPHICS_HANDOFF_CONTRACT.md`

Figure 4.9 remains compute-only.

Only after all five graphics workloads are source-backed/correctness-clean and the compute/graphics performance metric comparability gate passes may `GM-ALL-PAPER` be emitted.

If exhaustive post-compute recovery still proves source-backed graphics unavailable, preserve negative evidence and finish at `M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`. A memory proxy remains supplemental only.
