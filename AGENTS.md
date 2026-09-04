# AGENTS.md — Decoupled-Tag L1 M5 Research Workflow

This repository coordinates M5 mechanism/performance reproduction.

## Mandatory read order on `hrl/decoupled-l1-exp-m5-v0`

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`
3. `docs/dtc_l1/m5/M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`
4. `docs/dtc_l1/m5/M5_V1_APPROVAL.md`
5. `docs/dtc_l1/m5/M5_DIRTY_VICTIM_POLICY_RESOLUTION.md`
6. `docs/dtc_l1/m5/M5_EXTENDED20_APPROVAL.md`
7. `docs/dtc_l1/m5/M5_EXTENDED20_FORMAL_MATRIX.md`
8. `docs/dtc_l1/m5/M5_PARALLEL_BATCH_POLICY.md`
9. `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md`
10. `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md`
11. `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md`
12. `docs/dtc_l1/m5/M5_EXTENDED20_HANDOFF_CONTRACT.md`
13. `docs/dtc_l1/m5/M5_BRANCH_OWNERSHIP.md`
14. `docs/dtc_l1/chatgpt_handoff/CODEX_NEXT_STAGE.md`
15. `docs/dtc_l1/chatgpt_handoff/GOAL_START.md`
16. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
17. `docs/dtc_l1/implementation/M5_ISSUE_LOG.md`
18. final M4 review pack
19. Core M5 `AGENTS.md`
20. Core `docs/dtc_l1/DTC_L1_SPEC.md`

`M5_V3_PARALLEL_TRACKS_APPROVAL.md` is the current scheduling authority. `M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md` consumes the completed graphics M5.7/M5.8 research result and supersedes any older wording that treats M5.9-M5.11 as currently active.

## Branch/window ownership

Follow `M5_BRANCH_OWNERSHIP.md` strictly.

### Compute window owns

- Core `hrl/decoupled-l1-m5-v0`
- Framework `hrl/decoupled-l1-exp-m5-v0`

It executes current Paper-10 work plus the approved Extended-20 formal track when dependencies are satisfied.

### Extended selection evidence

Framework `hrl/decoupled-l1-exp-m5-extended20-select-v0` at reviewed commit `d43b6eec93f68efa94057f34ffa699463b53e6a6` is frozen selection provenance. Do not run formal experiments there.

### Graphics research evidence

Framework `hrl/decoupled-l1-exp-m5-graphics-research-v0` at accepted closeout commit `ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d` is frozen graphics evidence.

Accepted status:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

Do not keep a graphics Codex window active merely to repeat already-audited routes. Reopen only if genuinely new original/source-backed evidence appears.

Under current evidence:

- no M5.9/M5.10/M5.11;
- no graphics Core integration branch;
- no graphics Base/IO/OO formal runs;
- no `GM-GRAPHICS` or `GM-ALL-PAPER`.

## Current progression

M5.0A is PASS. M5-T005/R5DV is CLOSED. Current Paper-10 work is M5.0B workload recovery.

Paper sequence:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

Extended sequence:

`M5.E0(selection approved) -> M5.E1 -> M5.E2 -> M5.E3`

- E1 metadata/build/input formalization may prepare before M5.2 when host resources permit.
- E2's 60 Base/IO/OO runs begin only after M5.2 freezes the common formal anchor.
- E2 uses resource-aware parallel worker-pool execution; do not unnecessarily serialize independent jobs.

After Paper M5.6 + Extended M5.E3, create `M5.COMPUTE_FREEZE` and proceed directly to M5.12 negative-evidence synthesis under the accepted graphics closeout.

## Compute-freeze join barrier

M5.6 alone is not a freeze boundary.

`M5.COMPUTE_FREEZE` requires:

- Paper M5.6 PASS;
- Extended M5.E3 PASS;
- no unresolved correctness/fidelity issue;
- active compute branches pushed/clean.

Record exact `COMPUTE_FREEZE_CORE_SHA` and `COMPUTE_FREEZE_FRAMEWORK_SHA` in `docs/dtc_l1/m5/handoffs/M5_COMPUTE_FREEZE.md`.

## Scientific objective

M5 targets mechanism/trend fidelity, not fitting thesis speedup numbers.

`Base structural limits -> constrained live misses -> DTC removes limits -> concurrency/latency hiding changes -> performance effect`

Weak/negative results are classified, not tuned away.

## Frozen compute definitions

### Main result

- PAPER_BASE: conventional 16 KiB L1, 128B, 4-way, PIB=8, MSHR=32.
- PAPER_IO: 16 KiB logical Tag + 80 KiB physical array, PIB=256.
- PAPER_OO: 16 KiB logical Tag + 80 KiB physical array, PIB=128.

### Dirty-victim policy

All paper-facing/formal M5 configurations use explicit:

`-gpgpu_l1_cache_write_ratio 0`

Ratio 25 is diagnostic platform policy only.

### Figure 4.7

Common live miss = new-miss lower-request commit through final lower response; primary metric = per-SM cycle average.

### Figure 4.2

Formal categories: PIB full, true Tag/cacheline allocation failure, MSHR capacity/merge, Miss Queue/lower capacity. Tag-bank arbitration remains diagnostic.

## Extended-20 reporting boundary

Approved Extended-20 is supplemental generalization evidence.

Use separate labels:

- `GM-PAPER10` / `GM-GP`
- `GM-EXTENDED20`
- `GM-ALL-COMPUTE30`

Extended-20 never enters `GM-ALL-PAPER`.

## Problem behavior

Use `M5_PROBLEM_RESOLUTION_POLICY.md`.

Ordinary workload/build/assertion/parser/counter/timeout/performance issues are resolve-in-goal. Diagnose -> repair/reconstruct -> regress -> invalidate stale data -> continue.

Do not stop merely because performance is weak/negative or a workload differs from thesis trend.

## Parallel batch behavior

Follow `M5_PARALLEL_BATCH_POLICY.md` for long independent runs.

Default is a measured-safe worker pool with isolated job directories and resumable identities, not one-workload-at-a-time execution.

## Formal-result discipline

Every result records source/Core/Framework/config/workload/PTX/input/parser identity. Invalidated FORMAL data becomes OBSOLETE; preserve evidence rather than deleting/relabeling it.

Do not commit raw logs, traces, binaries, datasets or build trees.

## Git discipline

- never `git add .` or `git add -A`;
- stage explicit paths only;
- no force-push;
- distinct worktree per Codex window;
- preserve live processes/uncommitted artifacts owned by another window;
- use `git diff --check` at handoffs.

## Final M5 dependency

M5.12 requires Paper M5.6 + Extended M5.E3 + `M5.COMPUTE_FREEZE` + accepted graphics closeout commit `ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d` + no unresolved correctness/fidelity issue.

Current expected final state:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

Figure 4.6 area/synthesis remains outside M5 and requires M6 authorization.
