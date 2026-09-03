# M5 Graphics Reproduction Plan

Status: **ACTIVE UNDER M5 v3 — RESEARCH NOW, INTEGRATE AFTER COMPUTE FREEZE**

Scheduling authority:

- `M5_V3_PARALLEL_TRACKS_APPROVAL.md`
- `M5_GRAPHICS_INDEPENDENT_WINDOW_HANDOFF.md`
- `M5_GRAPHICS_HANDOFF_CONTRACT.md`

The existing `UNAVAILABLE_WITH_CURRENT_INFRA` audit is evidence that the ready-made current Accel-Sim/GPGPU-Sim path cannot directly execute/replay the thesis glmark2 workloads. It is not permission to fabricate a proxy and it is not the end of source/artifact recovery.

## 1. Stage structure

### Research phase — may run now in a separate Framework-only window

`M5.7 Graphics Provenance -> M5.8 Graphics Path Recovery`

Research branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

No Core modifications are allowed in this phase.

### Integration/formal phase — only after M5.COMPUTE_FREEZE

If a source-backed path is established:

`M5.9 Graphics Infrastructure -> M5.10 Graphics Fidelity Pilot -> M5.11 Five-Scene Formal Graphics -> M5.12 Full Synthesis`

If exhaustive M5.8 recovery proves source-backed graphics unavailable, skip M5.9-M5.11 and enter M5.12 negative-evidence synthesis after compute freeze.

## 2. Compute freeze prerequisite for graphics Core changes

Graphics Core integration waits for the v3 join barrier:

- Paper-10 M5.6 PASS;
- Extended-20 M5.E3 PASS;
- no unresolved correctness/fidelity issue;
- active compute Core/Framework pushed/clean.

The compute handoff records:

- `COMPUTE_FREEZE_CORE_SHA`
- `COMPUTE_FREEZE_FRAMEWORK_SHA`

Fresh graphics integration branches are then created exactly from those SHAs:

- Core `hrl/decoupled-l1-m5-graphics-v0`
- Framework `hrl/decoupled-l1-exp-m5-graphics-v0`

Graphics research evidence is carried forward intentionally; do not merge stale pre-freeze compute source state from the research branch.

## 3. M5.7 — Graphics provenance closure

For `jellyfish`, `cat-tex`, `cube-tex`, `2D-tex`, `horse`:

1. resolve thesis reference/version to exact or closest source-backed glmark2 version/tag/commit;
2. map each paper name to scene/test invocation;
3. recover shader sources, model assets, textures, draw parameters, resolution, vertices, texture dimensions and scene options;
4. search thesis/project artifacts, archived repositories, author/group releases and glmark2 history;
5. record source/asset hashes;
6. classify exact vs reconstructed/inferred properties.

Mapping classes:

- `EXACT_GRAPHICS_MATCH`
- `SOURCE_EQUIVALENT_GRAPHICS_MATCH`
- `PARTIAL_PROVENANCE_ONLY`
- `UNRESOLVED_AFTER_EXHAUSTIVE_AUDIT`

No visually similar scene is silently substituted.

Handoff:

`docs/dtc_l1/m5/handoffs/M5_7_GRAPHICS_PROVENANCE.md`

PASS -> M5.8.

## 4. M5.8 — Source-backed execution-path recovery

Search routes in order:

1. original thesis/project simulator, RTL/testbench, request/shader traces and scripts;
2. author/group historical artifacts;
3. historical graphics-enabled GPGPU-Sim/Accel-Sim forks or companion artifacts;
4. actual direct graphics frontend integration;
5. source-backed shader/request trace capture/replay;
6. calibrated memory proxy only as clearly supplemental non-formal work.

Any DIRECT/TRACE candidate must document:

- vertex/fragment shader identity;
- source-backed thread/warp/grouping semantics;
- memory addresses/request sizes;
- global vs texture distinction and texture-path interaction;
- memory ordering and shader completion ordering;
- draw/frame boundaries;
- framebuffer/fixed-function traffic scope;
- whether writes/atomics/fixed-function memory enter DTC scope;
- cycle/performance metric definition;
- why Base/IO/OO use the same driver/timing boundary.

If graphics is trace-driven while compute is execution-driven, `GM-ALL-PAPER` remains forbidden until a source-backed cross-path comparability contract is proven.

M5.8 valid research-phase closeouts:

### Path found

`M5_GRAPHICS_RESEARCH_READY_FOR_COMPUTE_FREEZE`

Provide M5.9 integration and directed-test plan, then wait for compute freeze. Do not modify Core yet.

### Exhaustive path unavailable

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

Original-artifact, historical-simulator, direct and trace routes must all be audited. Preserve exact reasons each route fails. A proxy is not formal graphics reproduction.

## 5. M5.9 — Graphics infrastructure bring-up

Execute only after both:

- source-backed path exists;
- `M5.COMPUTE_FREEZE` exists.

Required validation includes:

1. shader load reaches intended L1/DTC path;
2. cacheable hit/miss/pending behavior drains;
3. texture accesses preserve recovered source semantics;
4. draw/frame completion exactly once;
5. Base/IO/OO dynamic request identity is comparable;
6. IO/OO retirement does not violate graphics ordering constraints;
7. no request loss/duplication;
8. lower/request lifecycle drains;
9. fixed-function/framebuffer traffic outside DTC scope is separated.

Regression:

- Release build;
- DTC CTests;
- compute sentinels on graphics Core;
- graphics directed tests;
- git hygiene.

No scene-specific behavior may be inserted inside DTC.

Handoff:

`docs/dtc_l1/m5/handoffs/M5_9_GRAPHICS_INFRA.md`

PASS -> M5.10.

## 6. M5.10 — Graphics fidelity pilot

Pilot at least:

- jellyfish;
- one texture-heavy scene from cat-tex/cube-tex;
- horse.

For Base/IO/OO require:

- same source/asset/trace identity;
- valid scene/frame or trace completion;
- output/frame checksum when available;
- comparable dynamic request counts;
- DTC/lower accounting drain;
- Base pressure/live misses/IO-vs-OO/traffic triage.

Weak/negative DTC performance is not failure; classify causally.

PASS freezes `M5_GRAPHICS_FORMAL_BEHAVIOR_ANCHOR`.

## 7. M5.11 — Five-scene formal graphics

Run all five source-backed thesis graphics workloads for:

- Figure 4.2 Base structural stalls;
- Figure 4.5 Base/IO/OO performance;
- Figure 4.7 common live misses;
- Figure 4.8 logical-cache 16/32/64 KiB IO/OO sensitivity;
- Figure 4.10 PIB 32/64/128/192 IO/OO sensitivity.

Figure 4.9 remains compute-only.

Reuse identical runs across figures whenever identities match.

Maximum primary graphics formal envelope before retries:

- main triplets: 15;
- logical sensitivity: 30;
- PIB sensitivity: 40;
- total maximum: 85 unique configurations.

Use `M5_PARALLEL_BATCH_POLICY.md` for independent long runs on the graphics integration host/window.

Review pack:

`docs/dtc_l1/review_packs/M5_11_GRAPHICS_FORMAL/`

## 8. M5.12 — Full synthesis

M5.12 requires:

1. Paper-10 M5.6 PASS;
2. Extended-20 M5.E3 PASS;
3. `M5.COMPUTE_FREEZE`;
4. graphics M5.11 PASS **or** exhaustive M5.8 `GRAPHICS_SOURCE_BACKED_UNAVAILABLE`;
5. no unresolved correctness/fidelity issue.

Required outputs include:

- Paper-10 workload/provenance and Chapter-4 compute results;
- Extended-20 generalization results;
- graphics source-backed results or exhaustive limitation evidence;
- Figure 4.2, 4.5, 4.7, 4.8, 4.9 compute-only physical sensitivity, 4.10;
- per-workload causal classifications;
- numerical differences from thesis separated from mechanism/trend conclusions;
- graphics-path limitations/comparability assumptions.

Aggregate labels:

- `GM-PAPER10` / `GM-GP`;
- `GM-EXTENDED20`;
- `GM-ALL-COMPUTE30` supplemental;
- `GM-GRAPHICS` if source-backed;
- `GM-ALL-PAPER` only original 10 compute + 5 graphics and only if cross-path metric comparability is proven.

Extended-20 is never included in `GM-ALL-PAPER`.

Final states:

- `M5_FULL_REPRO_READY_FOR_REVIEW`; or
- `M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`.

Figure 4.6 fresh RTL/synthesis area work remains outside M5 and requires M6 authorization.

## 9. Problem/stop policy

Ordinary missing dependency/asset, compiler/shader conversion failure, frontend crash, trace parser/integration bug, counter gap, timeout with progress, poor speedup and repairable integration bug are resolve-in-track issues.

Pause only when:

- proposed formal path changes frozen DTC semantics;
- proxy/approximation would be required for a formal graphics claim;
- multiple scientifically distinct timing/execution interpretations remain irreducible;
- cross-path metrics cannot be made comparable but a combined `GM-ALL-PAPER` claim is being considered;
- final M5 review state is reached.
