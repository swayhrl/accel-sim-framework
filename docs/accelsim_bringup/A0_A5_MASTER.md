# Accel-Sim A0-A5 bringup master plan

## Goal

Bring up Accel-Sim in /workspace/repos/accel-sim-framework as a reusable simulator infrastructure for later paper reproduction work.

This is one large Codex round, but it must be executed in ordered phases:

- A0: environment and local directory hygiene
- A1: reproducible simulator build and binary smoke check
- A2: minimal pre-trace simulation smoke test
- A3: NVBit tracer flow and locally generated rodinia trace, only if GPU and tracer prerequisites are available
- A4: reusable benchmark pipeline scripts
- A5: result validation, documentation, and review pack

The round should be aggressive enough to complete the simulator bringup, but safe enough to avoid polluting git state and avoid large uncontrolled downloads.

## Current known baseline from repo check

- Repo path: /workspace/repos/accel-sim-framework
- Branch: hrl/tlb-latency-v0
- HEAD: 3016c658f810bdae9a14bf4534ee99e9945eedae
- Tag visible on HEAD: accel-baseline-3016c65
- No .gitmodules were reported.
- Existing important files include:
  - README.md
  - requirements.txt
  - gpu-simulator/setup_environment.sh
  - gpu-simulator/Makefile
  - gpu-simulator/CMakeLists.txt
  - gpu-simulator/bin/release/accel-sim.out
  - util/job_launching/run_simulations.py
  - util/job_launching/monitor_func_test.py
  - util/job_launching/get_stats.py
  - util/tracer_nvbit/install_nvbit.sh
  - util/tracer_nvbit/run_hw_trace.py
  - get-accel-sim-traces.py
- Current environment has:
  - Ubuntu 22.04
  - gcc/g++ 11.4
  - cmake 3.22
  - python3 3.10
  - nvcc from /usr/local/cuda-11.8/bin/nvcc
  - CUDA_HOME empty
  - CUDA_PATH empty
  - ACCELSIM_ROOT set to /workspace/repos/accel-sim-framework/gpu-simulator
  - GPGPUSIM_ROOT empty
  - Python packages yaml, numpy, pandas, matplotlib, scipy, plotly, psutil, requests, six present

## Hard rules

1. Do not push.
2. Do not use git add . or git add -A.
3. Do not commit generated logs, traces, benchmark outputs, downloaded apps, or build products.
4. Put generated local outputs under ignored paths:
   - .local_reports/
   - .local_logs/
   - .local_runs/
   - .local_traces/
   - hw_run/
   - review_packs/
5. Ensure these ignored paths are listed in .git/info/exclude, not in .gitignore, unless explicitly requested.
6. For each phase, write a phase report into .local_reports/.
7. For each phase, record:
   - start time
   - end time
   - wall clock seconds
   - commands run
   - pass/fail/blocked
   - important output paths
   - next action
8. If a phase is blocked by missing GPU, network, permissions, or missing traces, do not fake success. Mark it BLOCKED, keep going where possible.
9. Prefer targeted smoke tests over large benchmark suites.
10. Do not run long all-app simulations in this round.
11. If a command may download a large dataset, first inspect help/options and choose the smallest usable target. If the tool is interactive, document the prompt and chosen option.
12. A0 and A1 are mandatory. A2 is mandatory unless no trace can be acquired. A3 is conditional on GPU and tracer availability. A4 and A5 are mandatory, using whatever result state was actually achieved.

## Expected final state

At the end of A0-A5, the repo should contain tracked reusable documentation and scripts, and local ignored outputs should contain logs/reports/results.

Tracked files expected:

- docs/accelsim_bringup/A0_A5_MASTER.md
- docs/accelsim_bringup/A0_ENV_AND_LOCAL_DIRS.md
- docs/accelsim_bringup/A1_BUILD_AND_BINARY_SMOKE.md
- docs/accelsim_bringup/A2_PRETRACE_MINIMAL_SIM.md
- docs/accelsim_bringup/A3_TRACER_FLOW.md
- docs/accelsim_bringup/A4_BENCHMARK_PIPELINE.md
- docs/accelsim_bringup/A5_RESULTS_AND_DOCS.md
- docs/accelsim_bringup/CODEX_PROMPT_A0_A5.md
- scripts/accelsim/accelsim_env.sh
- scripts/accelsim/a0_env_check.sh
- scripts/accelsim/a1_build_smoke.sh
- scripts/accelsim/a2_pretrace_smoke.sh
- scripts/accelsim/a3_trace_rodinia_smoke.sh
- scripts/accelsim/a4_run_smoke_suite.sh
- scripts/accelsim/a5_collect_results.sh
- scripts/accelsim/README.md

Tracked docs may be adjusted if Codex finds better names, but keep the structure clear.

Ignored local output expected:

- .local_reports/A0_*.md or .log
- .local_reports/A1_*.md or .log
- .local_reports/A2_*.md or .log
- .local_reports/A3_*.md or .log
- .local_reports/A4_*.md or .log
- .local_reports/A5_*.md or .log
- .local_logs/*.log
- review_packs/A0_A5_ACCELSIM_BRINGUP_review_pack_*.tar.gz

## Phase dependency

A0 -> A1 -> A2 -> A3 -> A4 -> A5

A3 may be marked BLOCKED and skipped if no GPU is visible or if NVBit cannot be installed. A4 and A5 must still complete by documenting A3 as blocked and by providing scripts that can be used later.

## High level pass criteria

A0 pass:
- env script works
- CUDA variables are set consistently after source
- ACCELSIM_ROOT and GPGPUSIM_ROOT point to valid dirs
- git status does not show local runtime dirs

A1 pass:
- simulator builds or existing binary is verified with a recorded reason
- gpu-simulator/bin/release/accel-sim.out is executable
- binary help/version/smoke invocation is captured

A2 pass:
- at least one trace-driven SASS smoke simulation runs and stats are collected
- or phase is blocked with exact trace acquisition reason

A3 pass:
- NVBit tracer builds and a rodinia trace is generated
- or phase is blocked with exact GPU/tracer/network reason

A4 pass:
- reusable scripts can run a smoke suite with configurable benchmark, config, trace root, and run name
- scripts avoid hardcoded timestamp-only paths where possible
- results go under ignored local dirs

A5 pass:
- final summary report clearly states what works, what is blocked, and how to reproduce
- review pack exists
- git status is clean except intentional tracked changes before commit
- tracked docs/scripts are committed with a clear commit message

## Suggested commit policy

Commit once after adding guidance docs if they are not already committed.
Then Codex may commit once at the end of implementation with all tracked scripts/docs.

Commit messages:

- docs: add accel-sim A0-A5 bringup guidance
- scripts: add accel-sim bringup smoke pipeline

Do not commit generated runtime logs or review packs.
