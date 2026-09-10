# FAST64.6 — Frozen sensitivity acquisition handoff

Status: **FROZEN; THREE PHYSICAL PRECOMPUTATION ROWS STRICT-TERMINAL, SIX
ACTIVE, AND TWO PRESERVED CAPACITY-BOUND FAILURES UNDER
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`**

Logical stage order remains unchanged: FAST64.3, FAST64.4 and FAST64.5 must
pass before FAST64.6 logical acceptance.  This handoff freezes only the
independent physical-acquisition contract authorized after FAST64.2 PASS.

## Authority and mode policy

The dissertation-derived M5 authority is unambiguous.  M5.3 specifies the
logical 16/32/64 KiB formal sweep as PAPER_IO and PAPER_OO, with Base only an
optional supplemental capacity control; M5.4 specifies physical 16.5/24/32/
40/48 KiB for IO and OO; and M5.5 specifies IO/OO PIB 32/64/128/192, with
FAST64 retaining its already-frozen 256-entry diagnostic saturation point.
The exact sources are `M5_EXPERIMENT_MATRIX.md` §§M5.3--M5.5 and
`FAST64_SENSITIVITY_CONFIG_PLAN.md`.  Thus no researcher decision is needed.

The formal roster is frozen pre-performance as BICG, GESUMMV and Btree.  The
machine-readable 78-row IO/OO matrix is
`generated/FAST64_6_SENSITIVITY_MATRIX_V1.tsv`.  It records each config SHA,
exact physical-line mapping, per-dimension reference point, and pending
classification.  The nine materialized Base logical controls are retained as
source-supported *supplemental* configurations and are not part of the formal
FAST64.6 bar/matrix roster.

## Exact identities

- scientific Framework snapshot: `037f008b330eb230353b60edf126d6be9f45afdc`;
- config materialization source: `180e81c68816012165c26dab577e693b3b798292`;
- repaired Core/runtime: `95ccdb7a056f2d53f740d90869785cac6d4ee0f5` /
  `462d105cf28efe98a8a20131fd671f3d28ad374a3e4b5448a597df702cc4dbc9`;
- A1 observer: `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`.

Every acquisition uses a fresh namespace, unique UUID, immutable runner and
atomic START/TERMINAL receipts.  Versioned dispatcher
`dispatch_fast64_sensitivity_row_v4.sh` separately validates the historical
scientific snapshot and the later config-materialization commit, then gives
the immutable runner only the scientific snapshot identity.  This avoids
silently claiming that a configuration-only commit changed scientific inputs.
Future dispatches use `dispatch_fast64_sensitivity_row_v5.sh`, which performs
the same checks against the detached clean Core-`95ccdb7a...` formal worktree.
The active Core worktree may advance only for diagnostic-only descendants; its
HEAD is never allowed to substitute for the frozen formal Core identity.

## One-dimensional controls and normalization

- Logical: only `logical_sets`, IO/OO, normalize to the same mode at 16 KiB.
- Physical: only `physical_lines`, IO/OO, normalize per source to IO at 32 KiB.
  The exact 128-B mappings are 132/16,896 B, 192/24,576 B, 256/32,768 B,
  320/40,960 B and 384/49,152 B.
- PIB: only the mode-local PIB/coupled candidate-queue capacity, IO/OO,
  normalize per source to IO at 128 entries.  The 256 point is explicitly
  retained as a diagnostic saturation point and never relabelled as a thesis
  Figure-4.10 primary bar.

No matching historical-Core row is treated as repaired-Core sensitivity by
renaming.  A baseline point can be reused only after repaired-Core terminal
identity, exact payload/config/observer/snapshot, parser and drain checks.
All new rows must naturally exit zero and strict-validate lower/dependency and
mode-specific drain before any later logical promotion.

## First physical-acquisition wave (2026-09-10)

The two fresh three-window V3 resource audits recorded
`PASS_FUTURE_PRECOMPUTE_ADMISSION_V3`: no sampled swap-out, OOM, memory PSI,
CFS throttling or pathological cgroup I/O.  The target-20 audit at
`/tmp/fast64-resource-audit-v3-20260910T1340Z-target20.tsv` observed 15 live
FAST64 leaves and admitted five more, projecting 20 total workers and about
88.4 GiB `MemAvailable` after the fixed 16-GiB reserve.  This was followed by
ten nonduplicate physical-pool rows, all with atomic START receipts and
separate read-only closeout monitors:

| Physical pool | Workloads/modes |
| --- | --- |
| 16.5 KiB (132 lines, 16,896 B) | BICG IO/OO; GESUMMV IO/OO; Btree IO/OO |
| 24 KiB (192 lines, 24,576 B) | BICG IO/OO; GESUMMV IO/OO |

After the Btree/16.5-KiB/OO terminal freed one of the admitted slots, a fresh
three-window target-20 refill audit at
`/tmp/fast64-resource-audit-v3-20260910T1422Z-target20-refill.tsv` passed for
one new worker (no sustained swap-out, PSI, OOM, CFS throttle or pathological
I/O; projected `MemAvailable` 57.6 GiB after the fixed reserve).  The next
frozen, nonduplicate point, Btree / 24 KiB / IO, launched with immutable START
receipt UUID `c0902c8e-e9b8-4783-a021-933494c8b558` on CPU 29.  Its collector
is versioned separately as `collect_fast64_6_precompute_v2.sh`, so the live
v1 closeout dependency was not modified.

`generated/FAST64_6_PRECOMPUTE_DISPATCH_V1.tsv` is the compact immutable
attempt index (namespace, CPU, supervisor/simulator PID, UUID and config
hash).  The Btree / 16.5-KiB / OO row (UUID
`3a34fc35-38d0-48f3-a0e0-399f72c348f1`) naturally terminated exit 0 at
`2026-09-10T14:06:03Z` and strict-validated into
`generated/fast64_6_precomputed_v1/fast64_sens_v1_btree_physical16p5_oo.json`.
Its exact repaired-Core/runtime/scientific/A1 identities, payload trace hash,
receipt hashes, lower acquire/release `501958/501958`, dependency
`2388513/2388513`, and final lower/PIB/inflight/OO-ref drains are recorded
there; lower-cap-full is zero.  This is a retained physical precompute only.
All rows, including that terminal row, remain
`PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`: no FAST64.6 logical promotion or
performance conclusion is claimed.

## Terminal and failure accounting update (2026-09-10)

Two further Btree IO rows naturally exited zero and passed immutable receipt,
strict-parser, payload/config/identity, lower/dependency-conservation and
terminal-drain checks.  They remain retained precomputes only:

| Workload / point / mode | UUID | terminal UTC | cycles / instructions | lower acquire/release | dependencies closed/count | terminal resource state |
| --- | --- | --- | --- | --- | --- | --- |
| Btree / 16.5 KiB / IO | `3936327b-fe50-4212-bb1d-b0e79b2c6e23` | `2026-09-10T14:36:40Z` | 548,243 / 444,467,849 | 507,647 / 507,647 | 2,388,513 / 2,388,513 | lower, PIB, inflight and partial entries/lines drain to zero; cap-full 0 |
| Btree / 24 KiB / IO | `c0902c8e-e9b8-4783-a021-933494c8b558` | `2026-09-10T15:39:55Z` | 244,231 / 444,467,849 | 507,779 / 507,779 | 2,388,513 / 2,388,513 | lower, PIB, inflight and partial entries/lines drain to zero; cap-full 0 |

Their compact records are `generated/fast64_6_precomputed_v1/fast64_sens_v1_btree_physical16p5_io.json` and `generated/fast64_6_precomputed_v1/fast64_sens_v1_btree_physical24_io.json`.  Both bind repaired Core `95ccdb7a...`, repaired runtime `462d105c...`, scientific Framework `037f008b...`, A1 observer and exact Btree trace payload.  Both remain only `PRECOMPUTED_PENDING_FAST64_4_5_ACCEPTANCE`.

The BICG / 16.5-KiB IO and OO attempts are preserved failures, never result
records.  Both use the frozen repaired-Core/runtime/A1 identity and immutable
runner, but their TERMINAL receipts record exit 1: IO UUID
`cf459ee2-7ac4-4caa-8649-26eeb31d1d4e` at `2026-09-10T17:34:54Z`; OO UUID
`a6061cae-52b5-4263-a7fd-04434386ffaa` at `2026-09-10T17:17:10Z`.  The IO
fatal dump is source-classified as the frozen valid undersized-pool IO circular
resource dependency: 132/132 physical lines allocated, zero free, one
non-ready FIFO head per affected SM and 28--31 partially held lines, with zero
lower-create/issue/inflight work.  `DTC_L1_SPEC.md` §§3.4 and 8 expressly
require retained partial allocations/no rollback and identify this
undersized-configuration deadlock as emergent behavior.  It must not be
"fixed" by changing allocation semantics.  The OO failure is also preserved
and excluded; its current fatal dump lacks a mode-equivalent DTC resource
snapshot, so it remains an observability follow-up rather than an inferred
root cause.  `FAST64_6_BICG_PHYSICAL16P5_FAILURE.md` holds the exact evidence
and disposition.
