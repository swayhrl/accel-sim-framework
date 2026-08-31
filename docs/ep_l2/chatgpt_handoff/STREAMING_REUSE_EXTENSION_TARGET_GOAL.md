# EP-L2 Streaming / Temporal-Reuse Extension — Autonomous Target Goal

Status: **AUTHORIZED TARGET MODE**

## Terminal objective

Starting from the frozen Motivation source pair, autonomously build and validate a separate sector-aware temporal-reuse characterization extension, screen the existing runnable trace pool, select 2–3 additional formal streaming/far-reuse workloads, generate the formal original-10+new Figure-1-v2 dataset, publish Figure 1 v2 plus supporting evidence, and stop only at:

```text
STREAMING_REUSE_FIG1V2_REVIEW_READY
```

Do not stop after ordinary intermediate success.

---

## Immutable prior state

Treat the following as read-only historical/formal evidence:

```text
Core Motivation final:
2a6a31591bc42023e5997cca969e4b672efe0405

Framework Motivation final:
02f36816f60afcff55e910cdef2b60937e691cdc

Branch:
hrl/ep-l2-motivation-v0

Results:
/workspace/results/ep_l2_motivation/

Review pack:
docs/ep_l2/review_packs/MOTIVATION_FIGURES_r1/
```

Never overwrite, rewrite, regenerate in place, amend, rebase, force-push or delete these artifacts.

---

## Isolated execution state

Create/use only:

```text
Framework worktree:
/workspace/worktrees/accel-sim-ep-l2-streaming-reuse/

Core worktree:
/workspace/worktrees/gpgpu-sim-ep-l2-streaming-reuse/

Branch:
hrl/ep-l2-streaming-reuse-v0

Results:
/workspace/results/ep_l2_streaming_reuse/
```

Final evidence:

```text
docs/ep_l2/codex_handoff/LANE_STREAMING_REUSE_LATEST.md

docs/ep_l2/review_packs/STREAMING_REUSE_CHARACTERIZATION_r1/
```

---

## Mandatory governing documents

Read and obey in order:

```text
docs/ep_l2/chatgpt_handoff/STREAMING_REUSE_EXTENSION_HANDOFF.md
docs/ep_l2/chatgpt_handoff/STREAMING_REUSE_EXTENSION_ACCEPTANCE_CRITERIA.md
```

Also preserve the scientific semantics of:

```text
docs/ep_l2/project_spec/MOTIVATION_FIGURES_PLAN.md
docs/ep_l2/project_spec/decisions/ADR-009-motivation-wbuf-shadow-definition.md
```

The extension acceptance criteria are the mandatory self-gating contract.

---

## Autonomous execution sequence

### Stage 0 — preservation / branch isolation

- capture immutable prior branch/SHA/pack/result checksums;
- create fresh worktrees/branch/result root;
- prove no old artifact is modified.

Gate:

```text
STREAMING_REUSE_PRESERVATION_PASS
```

### Stage 1 — sector-aware telemetry implementation

Implement a new default-OFF, observation-only sector-reuse family without changing `EPL2MOTV1` semantics.

Primary semantic correction:

```text
same 128B line + different 32B sector first touch
!= temporal reuse

same exact 32B sector referenced again
== temporal sector reuse
```

Implement exact bounded sector temporal-reuse distance through 4096 distinct sector identities and all required coverage/classification counters.

### Stage 2 — correctness / neutrality preflight

Complete:

- source map;
- deterministic spatial-vs-temporal fixtures;
- distance boundary fixtures through 4097;
- multi-sector request fixtures;
- epoch/slice/read/write/writeback fixtures;
- Release build;
- parser/aggregator regressions;
- timing-neutrality controls on vectorAdd/convolution/sad;
- host wall/RSS checks;
- old `EPL2MOTV1` compatibility checks.

Do not continue until:

```text
STREAMING_REUSE_PREFLIGHT_PASS
```

### Stage 3 — existing-trace screening

Inventory the local runnable trace pool and select a diverse 12–16-workload screening set when available, minimum 10 if materially constrained.

Include `vectorAdd_4M` as the spatial-streaming control.

Run independent candidates in parallel subject to CPU/RSS stability.

Do not infer archetype labels from benchmark names. Rank from measured sector-aware metrics.

Generate the required screening candidate/ranking/notes files.

### Stage 4 — formal 2–3 workload selection

Choose 2–3 additional workloads beyond the original Motivation 10.

Prefer:

```text
1–2 strong low-temporal-reuse / streaming workloads
+
1 genuine far-reuse workload if supported
```

If no strong far-reuse workload exists, report:

```text
NO_STRONG_FAR_REUSE_FOUND_IN_SCREENED_POOL
```

and select the strongest scientifically useful streaming workloads instead.

Do not fabricate a far-reuse result.

### Stage 5 — formal Figure-1-v2 dataset

On one final frozen extension source/config family, obtain sector-aware formal rows for:

```text
scan
vectorAdd_4M
convolutionSeparable
spmv
FWT_7_21
cfd_097k
dwt2d
sad
btree
gemm
+
selected 2–3 new workloads
```

All must be `COMPLETE_VALID`.

For the original 10, revalidate old `EPL2MOTV1` scientific fields against immutable `MOTIVATION_FIGURES_r1`.

A screening result may be promoted only if its provenance already exactly matches the final frozen source/config/trace and it passes every formal gate.

### Stage 6 — aggregation / Figure 1 v2 / review pack

Generate:

```text
FIG1V2_L2_SECTOR_TEMPORAL_REUSE.png
FIG1V2_L2_SECTOR_TEMPORAL_REUSE.svg

FIG1S_LINE_VS_SECTOR_REUSE.png
FIG1S_LINE_VS_SECTOR_REUSE.svg
```

Figure 1 v2 must visibly separate:

- amount of true temporal reuse;
- spatial continuation;
- one-touch sectors;
- conditional temporal reuse-distance distribution.

Do not allow a workload with very little temporal reuse to look highly reusable merely because its few reuses are short.

Publish the complete review pack and validation evidence required by the acceptance criteria.

### Stage 7 — preservation recheck / terminal handoff

Recheck immutable prior Motivation artifacts.

Push exact new Core/Framework branches and the new review pack.

Publish:

```text
docs/ep_l2/codex_handoff/LANE_STREAMING_REUSE_LATEST.md
```

Terminal state:

```text
STREAMING_REUSE_FIG1V2_REVIEW_READY
```

Then STOP for independent ChatGPT review.

---

## Self-repair rules

When a mandatory gate fails:

1. preserve failing evidence;
2. diagnose root cause rather than patching around the symptom;
3. repair autonomously if the issue is within observation-only telemetry/parser/runner/analysis/plotting scope;
4. rerun all directed/preflight gates affected by the repair;
5. if source/config semantics changed after formal data were produced, freeze a new candidate and invalidate/rerun only affected extension results;
6. never delete or overwrite old results as part of repair.

If a problem requires changing accepted functional EP-L2 architecture semantics, stop and request review rather than crossing that boundary.

---

## Parallelism policy

Use independent parallel runs aggressively when host resources permit.

Do not serialize candidates merely for convenience. Long-running workloads must not block launching unrelated candidates.

However, do not launch the screening fanout before `STREAMING_REUSE_PREFLIGHT_PASS`, and do not promote Figure-1-v2 data before the final source/config provenance is frozen.

---

## Claim boundary

This lane may establish:

- whether old 128-B line reuse is spatial vs true 32-B temporal reuse;
- which workloads are low-temporal-reuse / streaming;
- conditional temporal-sector reuse-distance distributions;
- whether a strong far-reuse archetype exists in the screened pool.

It does not establish:

- performance benefit of a new cache mechanism;
- exact hit rate of a hypothetical victim cache;
- speedup from retaining/evicting sectors differently.

Those require later functional mechanism experiments.
