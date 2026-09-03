# M5 Graphics Handoff Contract

Status: **ACTIVE AFTER M5.6 COMPUTE CLOSEOUT**

Authority: `M5_GRAPHICS_POST_COMPUTE_PLAN.md`.

Graphics stages are independently reviewable quality gates, but PASS handoffs are not human-approval pauses. After M5.6 compute freeze, Codex continues automatically through the graphics plan unless a genuine researcher-decision boundary is reached.

## 1. Compute-to-graphics transition handoff

Before M5.7, create:

`docs/dtc_l1/m5/handoffs/M5_6_TO_GRAPHICS.md`

Required fields:

- compute final status `M5_COMPUTE_READY_FOR_GRAPHICS_CONTINUATION`;
- `COMPUTE_FREEZE_CORE_SHA`;
- `COMPUTE_FREEZE_FRAMEWORK_SHA`;
- compute review-pack path;
- compute formal behavior/config/parser anchors;
- list of reusable compute results;
- list of graphics-preparation evidence already completed (G0/G1/G2);
- exact graphics branch names and creation SHAs;
- explicit statement that later graphics changes do not rewrite compute FORMAL data.

After this handoff, create/use isolated graphics branches:

- Core `hrl/decoupled-l1-m5-graphics-v0`;
- Framework `hrl/decoupled-l1-exp-m5-graphics-v0`.

## 2. Standard graphics-stage handoff fields

Every `M5.7-M5.12` handoff must include:

1. **Status**: PASS / RESOLVING_ISSUE / RESEARCHER_DECISION_REQUIRED / GRAPHICS_SOURCE_BACKED_UNAVAILABLE.
2. **Input anchors**: graphics Core SHA, graphics Framework SHA, compute-freeze SHAs.
3. **Previous handoff SHA/path**.
4. **Graphics provenance version**: source/tag/asset/shader hashes.
5. **Execution-path class**: DIRECT_SOURCE_BACKED / TRACE_SOURCE_BACKED / PROXY_SUPPLEMENTAL / unavailable.
6. **Semantic-fidelity checklist status**.
7. **Config and parser/schema identities**.
8. **Completed experiment IDs**.
9. **Acceptance checklist with evidence paths**.
10. **Issue IDs and resolution state**.
11. **Invalidated/obsolete graphics result IDs**.
12. **Result artifacts and raw-log index**.
13. **Mechanism finding** without claiming numeric thesis matching.
14. **Cross-path comparability state** for compute/graphics performance metrics.
15. **Next executable scope**.
16. **Do-not-redo list**.

## 3. M5.7 provenance handoff

Path:

`m5/handoffs/M5_7_GRAPHICS_PROVENANCE.md`

Must contain one row per thesis graphics workload:

`paper name | glmark2 scene/test | source version | shader source | model/texture asset hashes | resolution | vertices | exact/reconstructed options | mapping class | unresolved gaps`

Acceptance:

- all five have explicit mapping classes;
- no silent scene substitution;
- exact versus inferred settings are separated.

PASS -> M5.8.

## 4. M5.8 path-recovery handoff

Path:

`m5/handoffs/M5_8_GRAPHICS_PATH.md`

Must report evidence for each attempted path:

- original thesis/project artifacts;
- historical graphics-enabled simulator artifacts;
- direct OpenGL/frontend integration;
- source-backed trace/replay;
- proxy only as non-formal fallback.

For any selected DIRECT/TRACE path, include the complete semantic-fidelity checklist and cycle/performance definition.

Valid closeouts:

- `GRAPHICS_PATH_SOURCE_BACKED` -> M5.9;
- `GRAPHICS_SOURCE_BACKED_UNAVAILABLE` -> M5.12 negative-evidence closure.

Do not stop merely because the first candidate path fails.

## 5. M5.9 infrastructure handoff

Path:

`m5/handoffs/M5_9_GRAPHICS_INFRA.md`

Must include:

- graphics source modifications and branch SHAs;
- directed tests for shader-memory routing, texture semantics, completion, ordering, lower lifecycle, and request identity;
- DTC CTest and compute-sentinel regressions on graphics Core;
- explicit separation of fixed-function/framebuffer traffic outside DTC scope;
- source proof that no graphics benchmark identity is special-cased inside DTC.

PASS -> M5.10.

## 6. M5.10 fidelity-lock handoff

Path:

`m5/handoffs/M5_10_GRAPHICS_FIDELITY.md`

Required pilots:

- jellyfish;
- one texture-heavy scene (`cat-tex` or `cube-tex`);
- horse.

For Base/IO/OO record:

- source/asset/trace identity;
- dynamic shader/request counts;
- cycles/performance metric;
- output/frame checksum or trace-completion proof;
- Base structural pressure;
- common live misses;
- lower/accounting drain;
- weak/negative-result causal classification.

PASS freezes `M5_GRAPHICS_FORMAL_BEHAVIOR_ANCHOR` and continues M5.11.

## 7. M5.11 formal graphics handoff

Path:

`m5/handoffs/M5_11_GRAPHICS_FORMAL.md`

Review pack:

`review_packs/M5_11_GRAPHICS_FORMAL/`

Minimum contents:

- README.md
- SOURCE_ANCHORS.md
- GRAPHICS_PROVENANCE.md
- GRAPHICS_PATH_FIDELITY.md
- FORMAL_ANCHOR.md
- CONFIG_MANIFEST.md
- PARSER_SCHEMA.md
- COUNTER_SANITY.md
- VALIDATION_SUMMARY.md
- RESULT_MANIFEST.tsv
- RAW_LOG_INDEX.tsv
- OPEN_ISSUES.md
- generated/ compact CSV/JSON

Must cover all five graphics workloads for Figure 4.2, 4.5, 4.7, 4.8 and 4.10 as authorized by the plan. Figure 4.9 remains compute-only.

Before emitting `GM-ALL-PAPER`, include a dedicated `COMPUTE_GRAPHICS_COMPARABILITY.md` proving the performance metric can be aggregated across the compute and graphics execution paths.

PASS -> M5.12.

## 8. M5.12 full synthesis handoff

Path:

`m5/handoffs/M5_12_FULL_SYNTHESIS.md`

Final review pack:

`review_packs/M5_FULL_REPRO/`

If graphics succeeds, required final status:

`M5_FULL_REPRO_READY_FOR_REVIEW`

If exhaustive path recovery proves graphics unavailable, required final status:

`M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

In the unavailable case, the review pack must preserve:

- compute-complete evidence;
- exhaustive graphics path audit;
- exact reasons formal graphics cannot be claimed;
- any proxy/supplemental artifacts clearly segregated and excluded from paper figures;
- no `GM-ALL-PAPER`.

## 9. Transition rules

At every graphics-stage PASS:

1. finish correctness/fidelity acceptance;
2. run parser/counter sanity;
3. commit compact evidence with explicit path staging;
4. push graphics branches;
5. update `codex_handoff/LATEST_REPORT.md`;
6. begin the next graphics stage automatically.

Ordinary recoverable problems remain in the active stage and follow `M5_PROBLEM_RESOLUTION_POLICY.md` plus the graphics-specific rules in `M5_GRAPHICS_POST_COMPUTE_PLAN.md`.

Pause only for a real researcher decision or final terminal review state.
