# A10 Aligned Smoke

`scripts/accelsim/a10d_run_aligned_smoke.sh` runs a bounded direct Accel-Sim smoke for rows that are both present in real prior workload evidence and mapped to available traces.

Default selection:

- `runnable == yes`
- `mapping_status == TRACE_AVAILABLE`
- `match_type` is `exact`, `alias`, or `suite_alias`
- `evidence_strength == high`
- maximum 3 runs

The command uses `gpu-simulator/bin/release/accel-sim.out` with the SM7_QV100 GPGPU-Sim and trace configs. Logs go to `.local_logs/`, run directories go to `.local_runs/`, and normalized stats go to `.local_reports/A10D_aligned_smoke_TIMESTAMP.csv`.

A10D is not a paper reproduction. It validates that the real prior workload intersection can execute in the current Accel-Sim trace-driven path.
