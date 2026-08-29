# C6d/C7d closeout — recommended review entry point

Status: **CONDITIONAL PASS — NOT READY FOR FINAL 26 RUN**.

| Item | Value |
| --- | --- |
| C6d status | PASS for corrected bank-arbitration smoke evidence |
| C7d status | CONDITIONAL PASS; source/schema work is present, but final-SHA completeness evidence has gaps listed in `OPEN_ISSUES.md` |
| Core final SHA | `88e243e8e421002079adc85b9efae3452c02a828` |
| Framework final SHA | `2aef9fad48207415a9697f9b891068b42008e0a8` |
| Core branch/worktree | `hrl/ep-l2-c7d-char-v0` / `/workspace/worktrees/gpgpu-sim-ep-l2-c7d` |
| Framework branch/worktree | `hrl/ep-l2-c7d-char-v0` / `/workspace/worktrees/accel-sim-ep-l2-c7d` |
| Worktree state at packaging | Core clean. Framework source index clean; two untracked C7d validation-output directories are excluded from Git and indexed in `RAW_LOG_INDEX.tsv`. |
| Final 13x2 run started? | No |

Review order:

1. `FORMAL_RUN_READINESS.md` and `OPEN_ISSUES.md`.
2. `C6D_CLOSEOUT.md` and `C6D_SMOKE_COMPARISON.csv`.
3. `C7D_SEMANTIC_FIXES.md`, `C7D_FIELD_MATRIX.csv`, and the C7d schema/source map.
4. `VALIDATION_SUMMARY.md`, then `samples/` and `RAW_LOG_INDEX.tsv`.

Data classes are intentionally isolated:

- **FORMAL**: none; the 13x2 campaign has not started on the final source pair.
- **DIAGNOSTIC**: C6d smoke and C7d natural-sample outputs. They are useful
  correctness/equivalence evidence but predate the final C7d SHA pair.
- **PRE-FIX / OBSOLETE**: prior C5c/old-Banked campaign data; excluded from all
  formal inference. A compact status inventory is in
  `C6D_DIAGNOSTIC_RUN_STATUS.csv`.
