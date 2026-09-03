# M5 Graphics Handoff Contract

Status: **ACTIVE — M5.7/M5.8 MAY RUN NOW; M5.9+ REQUIRES M5.COMPUTE_FREEZE**

Scheduling authority:

- `M5_V3_PARALLEL_TRACKS_APPROVAL.md`
- `M5_GRAPHICS_INDEPENDENT_WINDOW_HANDOFF.md`
- `M5_GRAPHICS_POST_COMPUTE_PLAN.md` for integration/formal details

## 1. Two-phase graphics workflow

Graphics is split deliberately:

### Phase A — independent research now

Framework-only graphics-research branch executes:

`M5.7 -> M5.8`

No Core modifications and no active-compute branch writes.

### Phase B — integration after compute freeze

Only after `M5.COMPUTE_FREEZE`:

`M5.9 -> M5.10 -> M5.11 -> M5.12`

on fresh graphics branches created from exact compute-freeze SHAs.

## 2. M5.7 provenance handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_7_GRAPHICS_PROVENANCE.md`

Branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

Must contain one row per thesis graphics workload:

`paper name | glmark2 scene/test | source version | shader source | model/texture asset hashes | resolution | vertices | exact/reconstructed options | mapping class | unresolved gaps`

Acceptance:

- all five have explicit mapping classes;
- no silent scene substitution;
- exact and inferred/reconstructed settings are separated;
- provenance/source/asset hashes are recorded.

PASS -> M5.8 in the same research window.

## 3. M5.8 path-recovery handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_8_GRAPHICS_PATH.md`

Must report evidence for all candidate routes:

1. original thesis/project artifacts/traces/simulator/scripts;
2. historical graphics-enabled simulator/fork artifacts;
3. direct graphics frontend integration;
4. source-backed trace/replay;
5. proxy only as non-formal supplemental fallback.

For any DIRECT/TRACE candidate include:

- shader-stage identity;
- thread/warp grouping semantics;
- memory addresses/sizes;
- global vs texture behavior;
- ordering/completion semantics;
- draw/frame boundaries;
- fixed-function/framebuffer scope;
- cycle/performance metric definition;
- comparability plan across Base/IO/OO.

Valid M5.8 closeouts:

### Source-backed path found

`M5_GRAPHICS_RESEARCH_READY_FOR_COMPUTE_FREEZE`

Include M5.9 implementation/test plan, but do not modify Core yet.

### Exhaustive source-backed path unavailable

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

Preserve negative evidence; no formal proxy. Wait for compute freeze, then M5.12 consumes the unavailable result.

## 4. Compute-to-graphics integration handoff

Before M5.9, the compute window must create:

`docs/dtc_l1/m5/handoffs/M5_COMPUTE_FREEZE.md`

with:

- `COMPUTE_FREEZE_CORE_SHA`;
- `COMPUTE_FREEZE_FRAMEWORK_SHA`;
- Paper-10 M5.6 PASS evidence;
- Extended-20 M5.E3 PASS evidence;
- no unresolved correctness/fidelity issues;
- clean/pushed compute branches.

Then create:

- Core `hrl/decoupled-l1-m5-graphics-v0` from `COMPUTE_FREEZE_CORE_SHA`;
- Framework `hrl/decoupled-l1-exp-m5-graphics-v0` from `COMPUTE_FREEZE_FRAMEWORK_SHA`.

Carry forward reviewed M5.7/M5.8 research evidence intentionally; do not merge stale pre-freeze compute source state from the research branch.

## 5. Standard M5.9-M5.12 handoff fields

Every integration/formal graphics handoff records:

1. status;
2. graphics Core/Framework SHAs and compute-freeze SHAs;
3. previous graphics-research handoff;
4. graphics provenance version/source/asset/shader hashes;
5. execution-path class;
6. semantic-fidelity checklist;
7. config/parser identities;
8. completed experiment IDs;
9. acceptance checklist;
10. issue/resolution IDs;
11. obsolete graphics results;
12. compact results/raw-log index;
13. mechanism finding;
14. compute/graphics metric-comparability state;
15. next scope;
16. do-not-redo list.

## 6. M5.9 infrastructure handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_9_GRAPHICS_INFRA.md`

Must include:

- graphics source modifications and branch SHAs;
- shader-memory routing tests;
- texture semantics tests;
- draw/frame completion exactly-once evidence;
- Base/IO/OO request identity/comparability;
- IO/OO ordering constraints;
- lower/request lifecycle drain;
- fixed-function/framebuffer traffic separation;
- DTC CTests and compute-sentinel regressions on graphics Core;
- proof no scene identity is special-cased inside DTC.

PASS -> M5.10.

## 7. M5.10 fidelity-lock handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_10_GRAPHICS_FIDELITY.md`

Pilots:

- jellyfish;
- one texture-heavy scene (`cat-tex` or `cube-tex`);
- horse.

For Base/IO/OO record source/asset/trace identity, dynamic request counts, performance metric, output/frame or trace completion, structural pressure, live misses, accounting drain and causal classification.

PASS freezes `M5_GRAPHICS_FORMAL_BEHAVIOR_ANCHOR` -> M5.11.

## 8. M5.11 formal graphics handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_11_GRAPHICS_FORMAL.md`

Review pack:

`docs/dtc_l1/review_packs/M5_11_GRAPHICS_FORMAL/`

Cover all five source-backed graphics workloads for Figure 4.2, 4.5, 4.7, 4.8 and 4.10. Figure 4.9 remains compute-only.

Before `GM-ALL-PAPER`, create `COMPUTE_GRAPHICS_COMPARABILITY.md` proving metric aggregation is meaningful.

PASS -> M5.12.

## 9. M5.12 full synthesis handoff

Path:

`docs/dtc_l1/m5/handoffs/M5_12_FULL_SYNTHESIS.md`

Final review pack:

`docs/dtc_l1/review_packs/M5_FULL_REPRO/`

M5.12 requires the v3 join conditions:

- Paper-10 M5.6 PASS;
- Extended-20 M5.E3 PASS;
- `M5.COMPUTE_FREEZE`;
- graphics M5.11 PASS **or** exhaustive M5.8 `GRAPHICS_SOURCE_BACKED_UNAVAILABLE`;
- no unresolved correctness/fidelity issue.

Final synthesis must report separately:

- `GM-PAPER10` / `GM-GP`;
- `GM-EXTENDED20`;
- `GM-ALL-COMPUTE30` as supplemental generalization;
- `GM-GRAPHICS` if source-backed;
- `GM-ALL-PAPER` only for original 10 compute + 5 graphics and only if comparability is proven.

Extended-20 is never part of `GM-ALL-PAPER`.

Final statuses:

- `M5_FULL_REPRO_READY_FOR_REVIEW`; or
- `M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`.

## 10. Mutable-report ownership

During M5.7/M5.8 research use only the graphics-research branch's:

`docs/dtc_l1/codex_handoff/LATEST_GRAPHICS_RESEARCH_REPORT.md`

Do not edit active compute `LATEST_REPORT.md` from the graphics window.

After compute freeze and migration to graphics integration branches, the graphics integration window may establish its own final mutable report according to the compute-freeze handoff.

## 11. Transition/stop rules

Ordinary missing dependencies/assets, build failures, parser/integration bugs, timeouts with progress, weak speedup and individual path failures are resolve-in-track issues.

Pause only for a genuine research decision, a proposal to use approximation/proxy as formal graphics, a required frozen-DTC semantic change, irreducible timing/comparability ambiguity, or final M5 review state.
