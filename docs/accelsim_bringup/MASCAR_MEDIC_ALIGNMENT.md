# Mascar And MeDiC Alignment

`scripts/accelsim/a9_mascar_medic_alignment.sh` maps the existing Accel-Sim trace workflow to the review-pack and stats style used by prior Mascar and MeDiC GPGPU-Sim reproduction work.

The script searches cautiously under `/workspace/repos` for likely prior artifacts using names such as `gpgpu`, `mascar`, `medic`, `review_pack`, `stats`, `benchmark`, and `workload`. It avoids deep build-directory scans.

The mapping CSV contains:

```text
source,paper,prior_benchmark_name,prior_app_or_workload,accel_trace_candidate,trace_available,runner,config,status,notes
```

If available trace names match prior-style workloads, A9 can run a bounded aligned smoke using A7B. It does not reproduce Mascar or MeDiC results and does not run a full suite.

This differs from A8: A8 is a small Accel-Sim baseline; A9 is a workflow alignment layer and naming/stats/review-pack bridge.
