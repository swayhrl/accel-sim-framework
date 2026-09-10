# FAST64.6 — Frozen sensitivity acquisition handoff

Status: **FROZEN PRE-DISPATCH; PHYSICAL PRECOMPUTATION MAY RUN UNDER
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
