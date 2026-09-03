# M5 Post-Compute Graphics Reproduction Plan

Status: **RESEARCHER-AUTHORIZED — EXECUTE AFTER M5.6 COMPUTE CLOSEOUT**

Authority: this plan extends `M5_V1_APPROVAL.md` after the ten-compute study. It does not weaken or replace the compute acceptance criteria. Compute remains the immediate priority through M5.6.

## 0. Research scope and terminal states

The top-level reproduction remains M5. M0-M4 established and validated simulator mechanism infrastructure; M5 is the paper experiment/reproduction stage.

The ten-compute portion ends at M5.6. After M5.6 passes, Codex must **checkpoint/freeze compute evidence and continue into the graphics track rather than stop for ordinary approval**.

Graphics continuation stages:

`M5.7 -> M5.8 -> M5.9 -> M5.10 -> M5.11 -> M5.12`

Successful full performance/mechanism terminal state:

`M5_FULL_REPRO_READY_FOR_REVIEW`

If exhaustive source/artifact recovery proves that no scientifically source-backed graphics execution/replay path can be established without inventing graphics semantics, the allowed terminal state is:

`M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

That state is not a DTC mechanism failure. It must include complete negative evidence and must not fabricate a proxy as paper reproduction.

Figure 4.6 area/synthesis is outside this M5 performance track. If a fresh RTL/synthesis area reproduction is later required, handle it as a separate M6 track.

## 1. Compute freeze before graphics modifications

After M5.6 PASS:

1. finish the compute review pack and all compute handoffs;
2. record immutable `COMPUTE_FREEZE_CORE_SHA` and `COMPUTE_FREEZE_FRAMEWORK_SHA`;
3. verify both compute worktrees are clean and pushed;
4. retain all compute FORMAL result identities and raw-log indexes;
5. create isolated graphics branches from the exact compute-freeze heads:
   - Core: `hrl/decoupled-l1-m5-graphics-v0`
   - Framework: `hrl/decoupled-l1-exp-m5-graphics-v0`
6. graphics frontend/replay/integration changes go only on those graphics branches unless a documentation-only fix explicitly belongs on the frozen compute branch.

Graphics work must not invalidate or rewrite completed compute FORMAL evidence.

## 2. Existing graphics evidence

The current G1 audit classifies the existing infrastructure as `UNAVAILABLE_WITH_CURRENT_INFRA` for direct glmark2 execution and source-faithful replay. That classification is a starting point for post-compute recovery, not permission to create a compute proxy and call it graphics reproduction.

Existing evidence shows the active simulator lacks a production glmark2/OpenGL scene frontend and lacks an already-established source-backed graphics shader/request replay path. `OPENGL_SUPPORT` CUDA interoperability is not by itself proof of a complete graphics execution path.

## M5.7 — Graphics provenance closure

### Goal

Close the source identity of the five thesis graphics workloads before changing simulator infrastructure.

### Work

For `jellyfish`, `cat-tex`, `cube-tex`, `2D-tex`, and `horse`:

1. resolve thesis reference [78] to exact or closest source-backed glmark2 version/tag/commit;
2. map each thesis name to exact glmark2 scene/test invocation;
3. recover shader sources, model assets, textures, draw parameters, resolution, vertex counts, texture dimensions, and any scene options;
4. search thesis/project artifacts, archived repositories, author/group releases, glmark2 history, and local recovered assets before declaring a mapping unavailable;
5. record hashes and provenance for all recovered material;
6. distinguish exact identity from nearest-version reconstruction.

### Mapping classes

- `EXACT_GRAPHICS_MATCH`
- `SOURCE_EQUIVALENT_GRAPHICS_MATCH`
- `PARTIAL_PROVENANCE_ONLY`
- `UNRESOLVED_AFTER_EXHAUSTIVE_AUDIT`

### Acceptance

`FIDELITY_HARD`:

- every thesis graphics workload has an explicit mapping classification;
- no visually similar scene is silently substituted;
- exact recovered settings are separated from inferred/reconstructed settings;
- all provenance sources/hashes are recorded.

### Handoff

`m5/handoffs/M5_7_GRAPHICS_PROVENANCE.md`

PASS -> M5.8 automatically.

## M5.8 — Source-backed graphics execution-path recovery

### Goal

Try to establish a scientifically defensible path capable of exercising the same DTC L1 mechanism for real graphics shader workloads.

The prior `UNAVAILABLE_WITH_CURRENT_INFRA` result means there is no ready path. Codex must now perform a deeper recovery audit rather than simply repeat that conclusion.

### Candidate path search order

1. **Original thesis/project artifacts**
   - search for the original graphics simulator, RTL testbench, request traces, shader traces, modified GPGPU-Sim code, or scripts used for Chapter 4;
   - prefer artifacts from the thesis authors/group/project when available.
2. **Historical/source-backed simulator path**
   - search historical GPGPU-Sim/Accel-Sim forks, graphics-enabled variants, published companion artifacts, or related simulator code capable of executing the required shader stages;
   - determine whether the path is compatible enough to carry the validated DTC model without changing its frozen semantics.
3. **Direct graphics frontend integration**
   - inspect whether enabling or reconstructing existing OpenGL integration can actually produce shader-stage execution/memory requests, not merely CUDA/OpenGL buffer interop;
   - direct path is valid only if vertex/fragment/texture/framebuffer semantics relevant to the DTC experiment are source-backed.
4. **Source-backed trace/replay path**
   - investigate whether exact graphics shader/request traces can be captured or recovered with sufficient ordering, address, texture, warp/grouping, and completion information;
   - replay is valid only if the resulting simulator timing path still exercises the same L1/DTC model and has a defensible cycle/performance basis.
5. **Proxy path**
   - a calibrated memory proxy may be prepared only as supplemental diagnostic work after formal path recovery fails;
   - proxy data can never be used for thesis graphics bars, Figure 4.x formal extensions, or `GM-ALL-PAPER`.

### Required semantic fidelity checklist

Any proposed DIRECT or TRACE path must document:

- vertex/fragment shader identity;
- warp/thread grouping or a source-backed equivalent;
- memory addresses and request sizes;
- global/texture access distinction;
- texture cache/path interaction relevant to L1 behavior;
- memory ordering and shader completion ordering;
- draw/frame boundaries;
- framebuffer/output-completion semantics sufficient to know when the graphics workload is complete;
- whether writes/atomics/fixed-function memory are inside or outside the DTC L1 scope;
- how `gpu_tot_sim_cycle` or an equivalent performance metric is defined;
- why Base/IO/OO use the same driver and timing boundary.

### Cross-path comparability gate

If graphics uses a trace-driven path while compute uses execution-driven simulation, `GM-ALL-PAPER` is forbidden until Codex proves a source-backed comparability contract for the reported performance metric. It is not sufficient that both outputs contain a field named `cycles`.

### Acceptance

M5.8 may close in one of two ways:

A. `GRAPHICS_PATH_SOURCE_BACKED`
- one DIRECT or TRACE path passes the semantic checklist;
- integration scope and regression plan are explicit;
- proceed to M5.9.

B. `GRAPHICS_SOURCE_BACKED_UNAVAILABLE`
- original-artifact, historical-simulator, direct, and trace routes have all been exhaustively audited;
- evidence explains why each fails scientific fidelity;
- no proxy is relabeled as formal graphics;
- proceed directly to M5.12 negative-evidence closure and terminal review state.

Ordinary build/tool/source-recovery failures are resolve-in-goal and are not pause conditions.

### Handoff

`m5/handoffs/M5_8_GRAPHICS_PATH.md`

## M5.9 — Graphics infrastructure bring-up

Execute only after `GRAPHICS_PATH_SOURCE_BACKED`.

### Goal

Integrate the recovered graphics path on isolated graphics branches while preserving the frozen DTC architecture.

### Required directed validation

At minimum establish source-backed tests for:

1. shader load request reaches the intended L1/DTC path;
2. cacheable hit/miss/pending behavior is visible and drains;
3. texture accesses are routed according to the recovered graphics semantics rather than silently treated as ordinary CUDA global loads;
4. draw/frame completion occurs exactly once;
5. Base/IO/OO dynamic graphics-operation/request identity is comparable;
6. IO retirement ordering and OO behavior do not violate source graphics ordering constraints;
7. no request is lost/duplicated by frontend-to-DTC integration;
8. all lower-request/lifecycle counters drain;
9. any fixed-function/framebuffer traffic outside DTC scope is explicitly separated rather than incorrectly credited to DTC.

### Regression

- release build;
- DTC CTests;
- compute sentinel set on graphics Core to prove DTC mechanism regression cleanliness;
- graphics directed tests;
- git hygiene.

### Acceptance

All correctness/fidelity checks pass. No graphics-special-case behavior is inserted inside DTC merely to improve results.

### Handoff

`m5/handoffs/M5_9_GRAPHICS_INFRA.md`

PASS -> M5.10.

## M5.10 — Graphics pilot/fidelity lock

### Goal

Prove the recovered path on a small but representative graphics set before launching all formal runs.

### Pilot scenes

Use at least:

- `jellyfish` — larger geometry;
- one texture-heavy scene from `cat-tex` or `cube-tex`;
- `horse` — no-texture contrast.

Run Base/IO/OO with the same paper-facing policy as compute unless graphics source evidence requires a documented non-DTC platform difference.

### Required checks

- scene/frame completion or source-backed trace completion;
- output/frame checksum when DIRECT path permits it;
- identical source/asset/trace identity across Base/IO/OO;
- comparable dynamic shader/request counts;
- DTC accounting/lower lifecycle drain;
- no hidden graphics frontend retry/deadlock;
- first mechanism triage: Base pressure, live concurrent misses, IO/OO difference, traffic.

Weak or negative DTC speedup is not a failure; diagnose it using the same causal policy as compute.

### Handoff

`m5/handoffs/M5_10_GRAPHICS_FIDELITY.md`

PASS -> freeze `M5_GRAPHICS_FORMAL_BEHAVIOR_ANCHOR` and continue M5.11.

## M5.11 — Formal five-scene graphics experiments

Use all five source-backed thesis graphics workloads.

### Reproduce/extend these thesis figures

- Figure 4.2: PAPER_BASE structural stalls;
- Figure 4.5: PAPER_BASE / PAPER_IO / PAPER_OO performance;
- Figure 4.7: common live concurrent misses;
- Figure 4.8: logical-cache sensitivity 16/32/64 KiB for IO/OO;
- Figure 4.10: PIB sensitivity 32/64/128/192 for IO/OO.

Figure 4.9 remains compute-only.

### Run reuse and expected unique run envelope

Reuse identical runs across figures whenever config/result identities match.

Maximum core formal run envelope before retries:

- main Base/IO/OO triplets: `5 * 3 = 15`;
- logical sensitivity: `5 * 3 * 2 = 30`;
- PIB sensitivity: `5 * 4 * 2 = 40`;
- total maximum unique graphics formal configurations: `85`.

Figure 4.2 and Figure 4.7 should reuse main runs when instrumentation/config identity is identical.

### Aggregate labels

- `GM-GRAPHICS`: geometric mean over the five graphics workloads;
- `GM-CE`, `GM-GP`: retain compute definitions;
- `GM-ALL-PAPER`: allowed only when all 15 paper workloads are source-backed/correctness-clean and the compute/graphics performance metric comparability gate is satisfied.

### Acceptance

`CORRECTNESS_HARD`:
- scene/output/trace completion valid;
- request/accounting conservation and drain;
- Base/IO/OO source identity consistent.

`FIDELITY_HARD`:
- all five graphics mappings satisfy the accepted provenance class;
- figure-specific knobs are the only intended differences;
- performance metric is comparable across variants and, for GM-ALL, across compute/graphics paths.

`MECHANISM_EXPECTATION`:
- characterize, but do not force, DTC concurrency/performance trends and graphics IO-vs-OO behavior.

### Handoff / review pack

- `m5/handoffs/M5_11_GRAPHICS_FORMAL.md`
- `review_packs/M5_11_GRAPHICS_FORMAL/`

PASS -> M5.12.

## M5.12 — Full Chapter-4 performance/mechanism synthesis

### Goal

Combine the validated ten-compute and five-graphics evidence without rewriting either frozen result set.

### Required outputs

1. complete workload/provenance table for all 15 workloads;
2. Figure 4.2 compute + graphics structural-stall reproduction;
3. Figure 4.5 Base/IO/OO performance with valid group labels;
4. Figure 4.7 common live-miss comparison;
5. Figure 4.8 logical sensitivity;
6. Figure 4.9 compute-only physical sensitivity;
7. Figure 4.10 PIB sensitivity;
8. GM-CE, GM-GP, GM-GRAPHICS, and only if eligible `GM-ALL-PAPER`;
9. causal classification of weak/negative/outlier workloads;
10. explicit numerical differences from thesis separated from mechanism/trend conclusions;
11. explicit graphics-path limitations and comparability assumptions;
12. list of excluded work: Figure 4.6 area, sector extension, proxy graphics, other M5.13+ supplements.

### Terminal states

If source-backed graphics formal reproduction succeeds:

`M5_FULL_REPRO_READY_FOR_REVIEW`

If M5.8 exhaustively proves graphics unavailable:

`M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

No M6 area/synthesis work starts automatically.

## 3. Problem/stop policy for graphics continuation

Do not pause merely for:

- missing glmark2 build dependency;
- missing asset that can still be source-recovered;
- compiler/shader conversion failure;
- graphics frontend crash;
- trace parser/integration bug;
- counter/instrumentation gap;
- timeout with diagnosable progress;
- poor/negative DTC performance;
- a repairable graphics integration bug.

Resolve -> regress -> continue.

Pause for researcher decision only if:

- the proposed path would change frozen DTC architecture semantics;
- a proxy/approximation would be required to claim formal graphics reproduction;
- multiple scientifically distinct graphics timing/execution interpretations remain after source audit;
- compute/graphics metrics cannot be made comparable but a combined GM-ALL claim is being considered;
- or the plan reaches one of its terminal review states.
