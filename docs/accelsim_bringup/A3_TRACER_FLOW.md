# A3 NVBit tracer flow

## Purpose

Bring up the trace generation side using NVBit and gpu-app-collection, then feed the generated trace into Accel-Sim.

This phase is conditional. If no GPU is visible, mark A3 as BLOCKED_NO_GPU and do not treat it as a failed round.

## Required tracked script

Create:

    scripts/accelsim/a3_trace_rodinia_smoke.sh

Required behavior:

- cd to repo root.
- Source scripts/accelsim/accelsim_env.sh.
- Detect GPU:
    nvidia-smi
    ls -l /dev/nvidia*
- If no GPU is visible, write report and return with a distinct blocked status.
- Build NVBit tracer:
    ./util/tracer_nvbit/install_nvbit.sh
    make -j$(nproc) -C ./util/tracer_nvbit/
- Clone or reuse gpu-app-collection under:
    .local_runs/gpu-app-collection
- If .local_runs/gpu-app-collection exists, fetch status but do not reset user changes unless it is clearly a local throwaway clone.
- Source:
    .local_runs/gpu-app-collection/src/setup_environment
- Build smallest Rodinia functional tests:
    make -j$(nproc) -C .local_runs/gpu-app-collection/src rodinia_2.0-ft
    make -C .local_runs/gpu-app-collection/src data
- Generate trace:
    ./util/tracer_nvbit/run_hw_trace.py -B rodinia_2.0-ft -D ${ACCELSIM_GPU_DEVICE:-0}
- Find generated kernelslist.g:
    find ./hw_run/traces -type f -name kernelslist.g
- Then run A2-style simulation on the generated trace:
    ./util/job_launching/run_simulations.py -B rodinia_2.0-ft -C QV100-SASS -T GENERATED_TRACE_ROOT -N A3_generated_trace_smoke_TIMESTAMP
    ./util/job_launching/monitor_func_test.py -v -N RUN_NAME
    ./util/job_launching/get_stats.py -N RUN_NAME
- Save logs and stats:
    .local_logs/A3_trace_rodinia_TIMESTAMP.log
    .local_reports/A3_trace_rodinia_TIMESTAMP.md
    .local_reports/A3_trace_rodinia_TIMESTAMP_stats.csv

## Important safety constraints

- Do not commit gpu-app-collection.
- Do not commit hw_run or traces.
- Do not modify benchmark source except inside .local_runs if necessary.
- If network clone fails, mark BLOCKED_NETWORK.
- If tracer build fails due CUDA/NVBit mismatch, record exact error and suggested fix.
- If generated trace exists but simulation fails, record both tracer success and sim failure separately.

## A3 pass criteria

- Generated kernelslist.g exists under hw_run/traces.
- A generated-trace simulation finishes and stats CSV is nonempty.
- Or A3 is blocked with a precise reason:
  - BLOCKED_NO_GPU
  - BLOCKED_NETWORK
  - BLOCKED_TRACER_BUILD
  - BLOCKED_APP_BUILD
  - BLOCKED_TRACE_RUNTIME
