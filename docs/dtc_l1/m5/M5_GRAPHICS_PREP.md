# M5 Graphics Preparation Track

Status: **ACTIVE PARALLEL PREPARATION — MUST NOT BLOCK COMPUTE M5**

Authority: `M5_V1_APPROVAL.md` + `M5_EXPERIMENT_MATRIX.md`.

The thesis uses five glmark2 graphics workloads in Table 4.1. Current M1-M4 infrastructure has not established a source-backed end-to-end graphics fixed-function pipeline, so graphics preparation is a separate track. Its job is to make graphics ready to attach immediately after the ten-compute study, not to force a proxy into paper GM-ALL.

Thesis workload identities/settings:

| Workload | Vertices | Texture | Resolution |
| --- | ---: | --- | --- |
| jellyfish | 13200 | 2 x 256 x 256 | 800 x 600 |
| cat-tex | 43044 | 512 x 512 | 800 x 600 |
| cube-tex | 36 | 512 x 512 | 800 x 600 |
| 2D-tex | 4 | 128 x 128 | 256 x 256 |
| horse | 21516 | none | 800 x 600 |

---

## G0 — Thesis/glmark2 provenance audit

### Work

1. Resolve thesis reference [78] to the glmark2 source/version or closest source-backed version available.
2. Identify the exact scene/test names corresponding to `jellyfish`, `cat-tex`, `cube-tex`, `2D-tex`, and `horse`.
3. Recover model/texture assets and command-line parameters matching the thesis vertex/texture/resolution settings where available.
4. Record source commit/version, asset hashes, shader sources, and invocation.
5. Do not silently substitute a visually similar scene.

### Acceptance

- Each thesis graphics name has a source-backed mapping or a documented unresolved reason.
- Settings/assets are recorded exactly where recoverable.
- No simulator claim is made yet.

### Handoff

`handoffs/M5_G0_GRAPHICS_PROVENANCE.md`.

---

## G1 — Simulator-path feasibility audit

### Work

Audit whether the current Accel-Sim/GPGPU-Sim path can execute or faithfully replay the relevant shader/memory behavior.

Check:

- graphics API/fixed-function pipeline availability;
- ability to obtain PTX/SASS/shader traces for vertex/fragment stages;
- texture path support;
- ordering constraints relevant to IO-vs-OO retirement;
- framebuffer/output/completion semantics;
- whether existing trace infrastructure can represent the memory request stream without inventing graphics ordering.

Classify each candidate path:

- `DIRECT_SOURCE_BACKED`: source and simulator can execute the needed graphics path;
- `TRACE_SOURCE_BACKED`: source-backed shader/request trace can be replayed with preserved memory/order semantics;
- `CALIBRATED_MEMORY_PROXY`: only a memory-traffic proxy is possible; useful supplement but not paper graphics reproduction;
- `UNAVAILABLE_WITH_CURRENT_INFRA`.

### Acceptance

- Feasibility classification is based on source/tool evidence.
- Missing fixed-function support is not papered over with a compute kernel.
- If TRACE_SOURCE_BACKED is proposed, ordering and memory-operation fidelity are explicitly audited.

### Handoff

`handoffs/M5_G1_GRAPHICS_FEASIBILITY.md` plus `implementation/M5_GRAPHICS_PATH_AUDIT.md`.

---

## G2 — Preparation for execution

Only if `DIRECT_SOURCE_BACKED` or `TRACE_SOURCE_BACKED` is established:

1. create build/capture/replay scripts;
2. lock asset/trace/config hashes;
3. run a single-scene LEGACY/Base/IO/OO correctness smoke;
4. verify source-domain operation counts and memory lifecycle accounting;
5. package a resumable five-scene run manifest.

This may happen while compute sweeps run, but it must not consume or alter the compute FORMAL behavior anchor without the normal invalidation/regression process.

### Handoff

`handoffs/M5_G2_GRAPHICS_READY.md` with status `READY_FOR_GRAPHICS_FORMAL` or a source-backed non-direct classification.

---

## G3 — Attach graphics to paper figures after compute review

If source-backed graphics is ready, extend:

- Figure 4.2 stall breakdown;
- Figure 4.5 performance;
- Figure 4.7 concurrent misses;
- Figure 4.8 logical sensitivity;
- Figure 4.10 PIB sensitivity.

Figure 4.9 remains compute-only, matching the thesis discussion.

Only after all five graphics workloads are source-backed and correctness-clean may the aggregate label `GM-ALL-PAPER` be emitted.

If only a calibrated proxy is possible, keep graphics in a separate supplemental section and do not compare proxy results numerically to thesis FPS/performance bars as if they were direct reproduction.

Compute Goal may continue through M5.6 regardless of G0-G2 outcome. A graphics feasibility limitation is recorded and carried to compute review; it is not a compute-stop condition.
