# DTC-L1 M5 Explicit Goal Launch Contract

Status: **ACTIVE — M5 v3 PAPER COMPUTE + EXTENDED-20 + PARALLEL GRAPHICS RESEARCH**

Current durable scheduling authority:

`docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`

## Persistent scientific goal

Demonstrate and explain the performance effect of the validated Decoupled-Tag Cache mechanism:

`traditional L1 structural limits -> constrained live misses -> DTC removes limits -> concurrency/latency hiding changes -> performance effect`

Do not fit architecture/workload inputs to thesis speedup numbers.

M5 now contains three coordinated tracks:

- Paper-10 compute reproduction;
- approved Extended-20 generalization;
- five-workload graphics source-backed reproduction/recovery.

## Frozen Paper compute definitions

### Main modes

- PAPER_BASE: conventional 16 KiB L1, 128B, 4-way, PIB=8, MSHR=32.
- PAPER_IO: 16 KiB logical Tag capacity + 80 KiB physical array, PIB=256.
- PAPER_OO: 16 KiB logical Tag capacity + 80 KiB physical array, PIB=128.

### Dirty-victim policy

All paper-facing/formal configs use:

`-gpgpu_l1_cache_write_ratio 0`

Ratio 25 is diagnostic only.

### Figure 4.7

Common live miss = new-miss lower-request commit through final lower response; primary metric = per-SM cycle average.

### Figure 4.2

Formal categories = PIB full, true Tag/cacheline allocation failure, MSHR capacity/merge, Miss Queue/lower capacity. Tag-bank arbitration is diagnostic only.

## Track A — Paper-10 compute

Active compute branches:

- Core `hrl/decoupled-l1-m5-v0`
- Framework `hrl/decoupled-l1-exp-m5-v0`

Current state remains M5.0B/R5DV until canonical ratio-zero SpMV closes M5-T005.

Continue:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

Ordinary issues are resolved inside the Goal under `M5_PROBLEM_RESOLUTION_POLICY.md`.

## Track B — Extended-20 compute

Selection is approved from immutable selection evidence:

`hrl/decoupled-l1-exp-m5-extended20-select-v0@d43b6eec93f68efa94057f34ffa699463b53e6a6`

Do not redo selection or use DTC benefit to alter membership.

Sequence:

`M5.E1 formalization -> M5.E2 60 primary runs -> M5.E3 synthesis`

E1 can prepare early.

E2 begins only after Paper M5.2 PASS establishes the common formal Core/Framework/config/parser/metric anchor.

E2 primary matrix:

`20 x {PAPER_BASE, PAPER_IO, PAPER_OO} = 60`

Use `M5_PARALLEL_BATCH_POLICY.md`: long independent jobs should run in a measured-safe dynamic worker pool, not unnecessarily one-by-one.

After M5.2, Paper M5.3-M5.6 and Extended E2/E3 may progress concurrently in wall-clock time.

## Track C — graphics research/integration

A separate Framework-only research window/branch may execute now:

`M5.7 provenance -> M5.8 source-backed path recovery`

Research branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0`

The research window must not modify active compute branches/Core or active compute `LATEST_REPORT.md`.

M5.9+ Core integration is forbidden before compute freeze.

If M5.8 finds a source-backed path, research-only state becomes:

`M5_GRAPHICS_RESEARCH_READY_FOR_COMPUTE_FREEZE`

If exhaustive source/artifact/direct/trace recovery fails:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

No proxy may be relabeled formal.

## Compute-freeze join barrier

Paper M5.6 is not by itself terminal/freeze.

Create `M5.COMPUTE_FREEZE` only after:

1. Paper M5.6 PASS;
2. Extended M5.E3 PASS;
3. no unresolved correctness/fidelity issue;
4. compute Core/Framework branches pushed/clean.

Emit:

`docs/dtc_l1/m5/handoffs/M5_COMPUTE_FREEZE.md`

with exact:

- `COMPUTE_FREEZE_CORE_SHA`
- `COMPUTE_FREEZE_FRAMEWORK_SHA`

If Paper finishes first, use `M5_PAPER10_READY_WAITING_FOR_EXTENDED20` and continue Extended work rather than freezing Core.

## Graphics integration after compute freeze

If M5.8 established a source-backed path, create fresh branches from the exact compute-freeze SHAs:

- Core `hrl/decoupled-l1-m5-graphics-v0`
- Framework `hrl/decoupled-l1-exp-m5-graphics-v0`

Then execute:

`M5.9 -> M5.10 -> M5.11 -> M5.12`

If M5.8 exhaustively established graphics unavailable, skip M5.9-M5.11 and proceed to M5.12 negative-evidence synthesis after compute freeze.

## M5.12 final dependency

M5.12 requires:

- Paper M5.6 PASS;
- Extended M5.E3 PASS;
- `M5.COMPUTE_FREEZE`;
- graphics M5.11 PASS or exhaustive `GRAPHICS_SOURCE_BACKED_UNAVAILABLE` evidence;
- no unresolved correctness/fidelity issue.

Final reporting groups:

- `GM-PAPER10` / `GM-GP` — original ten compute;
- `GM-EXTENDED20` — supplemental twenty;
- `GM-ALL-COMPUTE30` — supplemental union;
- `GM-GRAPHICS` — five graphics if source-backed;
- `GM-ALL-PAPER` — original ten compute + five graphics only, and only with cross-path metric comparability proof.

Extended-20 is never included in `GM-ALL-PAPER`.

## Branch ownership

Follow `M5_BRANCH_OWNERSHIP.md`.

Never let two Codex windows write the same branch/worktree/mutable report. Preserve live jobs and uncommitted artifacts before integrating documentation updates.

## Problem-resolution behavior

Do not pause for ordinary:

- missing workload/asset/dependency;
- build/PTX/shader failure;
- parser/counter gap;
- simulator assertion that can be source-correctly repaired;
- timeout with diagnosable progress;
- weak/negative speedup;
- unexpected bottleneck/traffic result;
- isolated batch-job failure.

Diagnose -> classify -> repair/reconstruct -> regress -> invalidate stale identities -> continue.

## Pause conditions

Pause only for a genuine researcher decision that changes frozen architecture/experiment meaning, a required approximation to make a formal graphics claim, irreducible metric/comparability ambiguity, or a final M5 review state.

## Final M5 states

Successful source-backed graphics reproduction:

`M5_FULL_REPRO_READY_FOR_REVIEW`

Exhaustive formal graphics unavailability:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

Figure 4.6 fresh RTL/synthesis area work is excluded and requires separate M6 authorization.
