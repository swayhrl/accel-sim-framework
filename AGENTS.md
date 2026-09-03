# AGENTS.md — Decoupled-Tag L1 M5 Research Workflow

This repository coordinates M5 mechanism/performance reproduction.

## Mandatory read order on `hrl/decoupled-l1-exp-m5-v0`

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
3. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
4. `docs/dtc_l1/m5/M5_V2_GRAPHICS_CONTINUATION_APPROVAL.md`
5. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
6. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
7. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
8. `docs/dtc_l1/m5/M5_GRAPHICS_PREP.md`
9. `docs/dtc_l1/m5/M5_GRAPHICS_POST_COMPUTE_PLAN.md`
10. `docs/dtc_l1/m5/M5_GRAPHICS_HANDOFF_CONTRACT.md`
11. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
12. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
13. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
14. `docs/dtc_l1/implementation/M5_ISSUE_LOG.md`
15. final M4 review pack
16. Core M5 `AGENTS.md`
17. Core `docs/dtc_l1/DTC_L1_SPEC.md`

`M5_V1_APPROVAL.md` activates the compute matrix. `M5_DIRTY_VICTIM_POLICY_RESOLUTION.md` resolves M5-T005. `M5_V2_GRAPHICS_CONTINUATION_APPROVAL.md` extends the persistent Goal beyond M5.6 into post-compute graphics recovery/execution.

## Branch roles

Validated M1-M4 branches are read-only anchors.

Active compute branches:

- Core `hrl/decoupled-l1-m5-v0`
- Framework `hrl/decoupled-l1-exp-m5-v0`

After M5.6 PASS, freeze compute SHAs and create isolated graphics branches:

- Core `hrl/decoupled-l1-m5-graphics-v0`
- Framework `hrl/decoupled-l1-exp-m5-graphics-v0`

Do not rewrite compute FORMAL evidence from graphics branches.

## Current progression

M5.0A is PASS. M5.0B is ACTIVE. Close M5-T005 through the approved R5DV sequence, then resume the existing valid workload-recovery checkpoint.

Compute sequence:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

M5.6 is a compute freeze/checkpoint, not the persistent Goal terminal state.

Post-compute sequence:

`M5.7 -> M5.8 -> M5.9 -> M5.10 -> M5.11 -> M5.12`

Final M5 states:

- `M5_FULL_REPRO_READY_FOR_REVIEW`, or
- `M5_COMPUTE_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW` after exhaustive source-backed graphics recovery fails.

## Scientific objective

M5 targets mechanism/trend fidelity, not fitting thesis speedup numbers.

Expected causal chain:

`Base structural stalls -> limited concurrent misses -> DTC removes structural constraints -> higher live-miss concurrency / latency hiding -> performance effect`.

Weak or negative results must be diagnosed, not tuned away.

## Researcher-frozen compute definitions

### Figure 4.5

PAPER_IO/PAPER_OO: 16 KiB logical Tag/cache + 80 KiB physical Cacheline Array; IO PIB=256, OO PIB=128. PAPER_BASE: conventional 16 KiB L1, PIB=8, MSHR=32.

### Conventional-L1 dirty-victim policy

All paper-facing formal configs use explicit:

`-gpgpu_l1_cache_write_ratio 0`

Preserve write-through, allocation, LRU, MSHR, scoreboard, and DTC semantics. Ratio 25 is diagnostic only.

### Figure 4.7

Common live miss = new-miss lower-request commit through final lower response. Primary metric = per-SM cycle average.

### Figure 4.2

Formal categories: PIB/waiting-buffer full, true Tag & Cacheline allocation failure, MSHR capacity/merge, Miss Queue/lower capacity. Tag-bank arbitration is diagnostic only.

## Compute problem behavior

Use `M5_PROBLEM_RESOLUTION_POLICY.md`.

Do not STOP merely for missing workload/input/wrapper, build/PTX/parser failure, assertions, operation-count mismatch, weak speedup, timeout with progress, counter gap, unexpected platform bottleneck, repairable source-backed bug, or significant performance change after a fidelity correction.

Diagnose -> repair/reconstruct -> regress -> invalidate stale data when required -> continue.

## Graphics behavior

The existing G1 result `UNAVAILABLE_WITH_CURRENT_INFRA` means no ready-made source-backed path exists. It does not terminate the post-compute effort.

After M5.6, follow `M5_GRAPHICS_POST_COMPUTE_PLAN.md`:

1. close provenance for all five thesis scenes;
2. deeply search original thesis/project artifacts and historical graphics-enabled simulator paths;
3. investigate defensible direct integration and source-backed trace/replay;
4. if a source-backed path exists, integrate/test/pilot and run all five scenes;
5. if exhaustive recovery proves no source-backed path exists, preserve negative evidence and finish without fabricating a proxy.

A calibrated memory proxy is supplemental only and cannot appear in formal paper graphics bars or `GM-ALL-PAPER`.

If graphics uses a different driver/path from compute, `GM-ALL-PAPER` requires an explicit cross-path performance-metric comparability proof.

## Workload discipline

Compute M5.0B must recover/source-verify all ten thesis compute algorithms, including explicit alias audit for `gemv/gemver`, `gesu/gesummv`, and `conv2d/2DConvolution`.

Graphics M5.7 must source-resolve all five thesis glmark2 workloads without silent scene substitution.

Input/scene selection must come from source/paper provenance, never from whichever choice gives the largest DTC benefit.

## Formal-result discipline

Every result records source SHAs, config hash, workload/asset/binary/PTX/trace hashes as applicable, parser schema, and classification.

Invalidated FORMAL data becomes OBSOLETE. Preserve diagnostic evidence accurately. Do not relabel ratio-25 data as ratio-0 or proxy graphics as source-backed graphics.

Do not commit raw logs, traces, binaries, build trees, or large datasets. Commit compact evidence plus raw-log indexes.

## Git discipline

- Never `git add .` or `git add -A`.
- Stage explicit paths only.
- Keep semantic commits separate.
- Do not force-push shared branches.
- Preserve pre-policy evidence.
- Use clean worktrees and `git diff --check` at handoffs.

## Handoff progression

Use `M5_HANDOFF_CONTRACT.md` for compute and `M5_GRAPHICS_HANDOFF_CONTRACT.md` after compute freeze.

PASS is checkpoint-and-continue, not an ordinary approval stop. Pause only at a genuine researcher-decision boundary or a final M5 review state.

Figure 4.6 area/synthesis is outside this Goal and requires separate M6 authorization.
