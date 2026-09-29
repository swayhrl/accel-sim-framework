# R101R2 S128 Native diagnostic profile

This code uses the accepted R101 S128 payload and pinned HiMuon source. It does not create gradients, models, timing baselines, holdout data, or mechanisms.

Execution order on node109: `metric_query.sh`, `metric_freeze.py`, `prepare.py`, `run_path_nsys.sh`, `analyze_nsys.py`, `static_sass.py`, then `run_ncu.sh F128` and `run_ncu.sh K128` sequentially, followed by `analyze_ncu.py`, `finalize.py`, `write_reports.py`, `publish.py`. Every CUDA run or CUDA-tool action holds `/data/c16/locks/c16_gpu_campaign.lock`; offline parsing, reports, and node164 publication do not.

The first NCU reports omitted the supported LDGSTS opcode class. They are retained as ATTEMPT0, with exactly one bounded same-config metric-engineering retry per arm supplying formal results. `NCU_METRIC_PREREGISTRATION.md` records the amendment. Original R101 graph timing is the sole performance authority.
