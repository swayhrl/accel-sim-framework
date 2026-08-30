# Reproducibility checks

```text
python3 -m unittest util/ep_l2/tests/test_parse_epl2_m0a.py
python3 util/ep_l2/analyze_m0a_observability.py --results /workspace/results/ep_l2_m0a --out <fresh-dir>
git diff --check 2da5dba^ 2da5dba
git -C /workspace/worktrees/gpgpu-sim-ep-l2-m0a diff --check 666f0ba^ 666f0ba
```

All passed for the frozen evidence stated in the parent pack.
