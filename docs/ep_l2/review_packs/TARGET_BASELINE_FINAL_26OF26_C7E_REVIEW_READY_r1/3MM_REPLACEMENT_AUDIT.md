# 3mm duplicate-write incident audit — PASS

The two obsolete diagnostic paths are listed in `EXCLUDED_DIAGNOSTIC_RUNS.csv` and remain retained only as evidence:

- `/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850/C7E_DUPLICATE_WRITE_DIAGNOSTIC/B0-Legacy/3mm` — `COMPLETE_VALID`, but provenance-ambiguous because duplicate writers targeted the output.
- `/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850/C7E_DUPLICATE_WRITE_DIAGNOSTIC/B0-Banked/3mm` — `FAILED` parser artifact from the same incident.

The accepted clean direct replacements are `/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850/B0-Legacy/3mm` and `/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850/B0-Banked/3mm`. Both are `COMPLETE_VALID`, use Core `ece1a3a77c5628763e0a4605bfd1c639ee6a1495`, Framework `f08d2ce857972fad73c4e1ab7162ba94c6336507`, config `85562fce759876616806d32791ea3b7d1b13ee68cf20a84e48c63c96f67b8c0d`, the same frozen `kernelslist.g` trace identity recorded in `ACCEPTED_FORMAL_RUNS.csv`, and report 1,661,135 terminal cycles.

The reviewed Lane-D V3 discovery code reads only `cell.root.glob("B0-*/*/run_status.json")` (`analysis/lane_d_v3` was generated from `docs/ep_l2/analysis/lane_d_analysis.py` in commit `cb83606eb8640382b7c1932d8981b70608d9d130`); it cannot descend into `C7E_DUPLICATE_WRITE_DIAGNOSTIC/`. `ACCEPTED_FORMAL_RUNS.csv` contains exactly one row for each direct `(workload, variant)` key, including exactly one clean Legacy and one clean Banked 3mm row. All aggregate CSVs in this pack are generated from that direct 26-row set.
