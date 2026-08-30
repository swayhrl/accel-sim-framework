# Lane-D V3 reprocessing provenance

The formal C7e result root was consumed read-only from the runtime worktree.
The analyzer was run in the separate `hrl/ep-l2-cal-analysis-v0` worktree at
`cb83606eb8640382b7c1932d8981b70608d9d130` with this command:

```text
python3 docs/ep_l2/analysis/lane_d_analysis.py \
  --cell D256_BASE:/workspace/worktrees/accel-sim-ep-l2-c7e/docs/ep_l2/target_baseline_results_final_850:256:BASE:docs/ep_l2/calibration/contracts/D256_BASE.json \
  --out <this-pack>/analysis/lane_d_v3
```

The source and contract used for that invocation are copied under
`analysis/source/`. `analysis/lane_d_v3/ANALYSIS_MANIFEST.json` records 26
records and the exact input root. The reviewed analyzer discovers only direct
`B0-*/*/run_status.json` paths, so diagnostic subtrees are outside its input
set by construction.
