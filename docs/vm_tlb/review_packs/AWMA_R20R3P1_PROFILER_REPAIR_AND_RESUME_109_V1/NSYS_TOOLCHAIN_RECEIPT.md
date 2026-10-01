# Node109 installed Nsight Systems admission (CPU-only)

Read from the installed binary before any R20R3P1 GPU run:

- `which nsys`: `/usr/local/bin/nsys`
- `nsys --version`: `NVIDIA Nsight Systems version 2024.6.2.225-246235244400v0`
- `nsys status --environment`: supported; timestamp counter, perf-event sampling environment and Linux checks reported OK (Ubuntu, kernel 7.0.0-31-generic). This is a CPU/tool-status receipt, not proof of CUDA trace admission.
- Installed `nsys profile --help` supports `--capture-range=nvtx`, `--nvtx-capture=<range>`, absolute `-o/--output=<prefix>`, `-f/--force-overwrite=true`, `--export=sqlite`, and `--cuda-graph-trace=node` (node granularity rather than graph-only reporting).
- Installed `nsys export --help` supports explicit `--type=sqlite`, `--output=<path>`, and `--force-overwrite=true` from a `.nsys-rep`; `nsys stats --help` accepts `.nsys-rep` or SQLite and NVTX-filtered reports.

The parent R20R3 used direct `nvtxRangePushA` with a dynamic string but received no report despite process exit 0. This installed help does not specify registered-only trigger behavior. The bounded engineering canary will explicitly set `NSYS_NVTX_PROFILER_REGISTER_ONLY=0` and prove range plus CUDA kernel rows before any new scientific profile. No profiler version, driver, CUDA, or scientific solver source is changed.

The R20R3P1 Goal also names `r20r3_active_world_solver_native_v1/STATUS_AFTER_R20R3_PROFILE_STOP.md` as a review aid. That file is absent from the exact starting tree; the parent `PROFILE_FAILURE_AUDIT.md`, `ELIGIBLE_STAGE_AUDIT.md`, `REVISED_NUMERICAL_CONTRACT.md`, and `RUN_RECEIPTS.json` were available and read in full. This missing optional review note does not change the frozen scientific inputs or gates.
