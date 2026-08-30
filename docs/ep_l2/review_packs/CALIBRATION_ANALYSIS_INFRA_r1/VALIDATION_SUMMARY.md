# Lane-D V2 validation summary

Validated on 2026-08-30 using existing C7e artifacts only; no simulator was
launched or rerun.

- `python3 -m pytest -q tests/ep_l2_analysis/test_lane_d_analysis.py`: **12 passed**.
- Analyzer smoke: 22 records from the formal interim 22/26 scope (11
  workloads × Legacy/Banked), all `PASS_FULL_WINDOWS_ONLY` after duplicate and
  per-stream gap checks.
- Provenance fixtures cover same-SHA pairing, reviewed equivalent changed-SHA
  pairing, missing equivalence evidence, wrong base lineage, and hidden
  effective-config changes.
- `git diff --check`: PASS (recorded in `validation/git_diff_check.txt`).
- `validation/pytest.txt` retains the test runner output. The intentionally
  empty `validation/git_status.txt` is the clean-status capture after the
  evidence commit.
