# Lane-D V3 validation summary

Validated on 2026-08-30 using existing C7e artifacts only; no simulator was
launched or rerun.

- `python3 -m pytest -q tests/ep_l2_analysis/test_lane_d_analysis.py`: **17 passed**.
- Analyzer smoke: 22 records from the formal interim 22/26 scope (11
  workloads × Legacy/Banked), all `PASS_FULL_WINDOWS_ONLY` after duplicate,
  per-stream gap, and exact time-group alignment checks.
- Provenance fixtures cover same-SHA pairing, reviewed equivalent changed-SHA
  pairing, missing equivalence evidence, wrong base lineage, hidden
  effective-config changes, runtime-config hash mismatch, and config-delta
  PASS binding.
- Native DRAM recovery selects only the final complete 32-channel snapshot;
  unequal-channel fixture verifies `sum(util_i*n_cmd_i)/sum(n_cmd_i)` rather
  than a last-channel result. Missing imbalance denominators fail closed.
- `git diff --check`: PASS (recorded in `validation/git_diff_check.txt`).
- `validation/pytest.txt` retains the test runner output. The clean-status
  capture is summarized in `validation/git_status.txt`.
