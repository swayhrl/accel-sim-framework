# DTC-L1 M5 Explicit Goal Launch Contract

Status: **ACTIVE — M5 v3 PAPER COMPUTE + EXTENDED-20; GRAPHICS RESEARCH CLOSED SOURCE-BACKED-UNAVAILABLE**

Current durable scheduling authority:

- `docs/dtc_l1/m5/M5_V3_PARALLEL_TRACKS_APPROVAL.md`
- `docs/dtc_l1/m5/M5_GRAPHICS_RESEARCH_CLOSEOUT_APPROVAL.md`

## Persistent scientific goal

Demonstrate and explain the performance effect of the validated Decoupled-Tag Cache mechanism:

`traditional L1 structural limits -> constrained live misses -> DTC removes limits -> concurrency/latency hiding changes -> performance effect`

Do not fit architecture/workload inputs to thesis speedup numbers.

The active M5 execution scope is now:

- Paper-10 compute reproduction;
- approved Extended-20 generalization;
- final M5.12 synthesis carrying the accepted graphics-unavailability evidence.

The separate graphics research track has completed at `GRAPHICS_SOURCE_BACKED_UNAVAILABLE`; M5.9-M5.11 are skipped unless genuinely new source-backed graphics artifacts reopen M5.8.

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

M5-T005/R5DV is closed. Continue active M5.0B workload recovery from existing valid checkpoints.

Continue:

`M5.0B -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

Ordinary issues are resolved inside the Goal under `M5_PROBLEM_RESOLUTION_POLICY.md`.

## Track B — Extended-20 compute

Selection is approved from immutable selection evidence:

`hrl/decoupled-l1-exp-m5-extended20-select-v0@d43b6eec93f68efa94057f34ffa699463b53e6a6`

Do not redo selection or use DTC benefit to alter membership.

Use the review-refined final portfolio in `M5_EXTENDED20_APPROVAL.md` and `extended20/EXTENDED20_APPROVED.tsv`.

Sequence:

`M5.E1 formalization -> M5.E2 60 primary runs -> M5.E3 synthesis`

E1 may prepare early when host CPU/RAM/disk/I/O conditions permit without disturbing active Paper jobs.

E2 begins only after Paper M5.2 PASS establishes the common formal Core/Framework/config/parser/metric anchor.

E2 primary matrix:

`20 x {PAPER_BASE, PAPER_IO, PAPER_OO} = 60`

Use `M5_PARALLEL_BATCH_POLICY.md`: long independent jobs should run in a measured-safe dynamic worker pool, not unnecessarily one-by-one.

After M5.2, Paper M5.3-M5.6 and Extended E2/E3 may progress concurrently in wall-clock time.

## Graphics research closeout

Reviewed graphics branch:

`hrl/decoupled-l1-exp-m5-graphics-research-v0@ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`

Accepted result:

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE`

Consequences under current evidence:

- treat the graphics-research branch as frozen evidence;
- do not modify GPGPU-Sim Core for graphics;
- do not create graphics integration branches after compute freeze;
- skip M5.9/M5.10/M5.11;
- do not run formal graphics Base/IO/OO experiments;
- do not emit `GM-GRAPHICS` or `GM-ALL-PAPER`;
- carry four source-equivalent scene mappings plus unresolved `2D-tex` and the M5.8 negative path audit into M5.12.

Reopen M5.8 only if genuinely new original/source-backed artifacts meet the explicit admission contract in the accepted M5.8 handoff.

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

## M5.12 final dependency

After `M5.COMPUTE_FREEZE`, proceed directly to M5.12 negative-evidence synthesis.

M5.12 requires:

- Paper M5.6 PASS;
- Extended M5.E3 PASS;
- `M5.COMPUTE_FREEZE`;
- accepted graphics closeout commit `ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`;
- no unresolved correctness/fidelity issue.

Final reporting groups:

- `GM-PAPER10` / `GM-GP` — original ten compute;
- `GM-EXTENDED20` — supplemental twenty;
- `GM-ALL-COMPUTE30` — supplemental union.

No graphics aggregate is emitted under the current closeout.

## Branch ownership

Follow `M5_BRANCH_OWNERSHIP.md`.

Never let two Codex windows write the same branch/worktree/mutable report. Preserve live jobs and uncommitted artifacts before integrating documentation updates.

The graphics-research window has reached its accepted terminal state and does not need to keep running unless new source-backed evidence appears.

## Problem-resolution behavior

Do not pause for ordinary:

- missing workload/dependency;
- build/PTX failure;
- parser/counter gap;
- simulator assertion that can be source-correctly repaired;
- timeout with diagnosable progress;
- weak/negative speedup;
- unexpected bottleneck/traffic result;
- isolated batch-job failure.

Diagnose -> classify -> repair/reconstruct -> regress -> invalidate stale identities -> continue.

## Pause conditions

Pause only for a genuine researcher decision that changes frozen architecture/experiment meaning, an approved Extended substitution that cannot be resolved by the pre-performance alternate rules, a cross-track finding that requires changing a frozen common metric/config definition, or the final M5 review state.

## Final M5 state

Current expected terminal state:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`

Figure 4.6 fresh RTL/synthesis area work is excluded and requires separate M6 authorization.
