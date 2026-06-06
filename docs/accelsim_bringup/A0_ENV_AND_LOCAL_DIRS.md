# A0 environment and local directory hygiene

## Purpose

Create a stable local environment wrapper for Accel-Sim work and keep all runtime artifacts out of git status.

This phase must not modify simulator source code.

## Inputs

Repo path:

    /workspace/repos/accel-sim-framework

Detected CUDA path:

    /usr/local/cuda-11.8

Expected simulator root:

    /workspace/repos/accel-sim-framework/gpu-simulator

Expected embedded GPGPU-Sim root:

    /workspace/repos/accel-sim-framework/gpu-simulator/gpgpu-sim

## Required local ignored directories

Create these directories:

    .local_reports
    .local_logs
    .local_runs
    .local_traces
    review_packs

Also use existing hw_run if Accel-Sim creates it.

Add these lines to .git/info/exclude if missing:

    .local_reports/
    .local_logs/
    .local_runs/
    .local_traces/
    hw_run/
    review_packs/

Do not modify .gitignore in this phase.

## Required tracked script

Create:

    scripts/accelsim/accelsim_env.sh

This script should be sourceable from the repo root or from elsewhere.

Required behavior:

- Detect repo root as the parent of scripts/accelsim, not by current directory only.
- Export CUDA_INSTALL_PATH=/usr/local/cuda-11.8 if that directory exists.
- Export CUDA_HOME and CUDA_PATH to the same CUDA directory.
- Prepend CUDA bin to PATH only if not already present.
- Prepend CUDA lib64 and lib to LD_LIBRARY_PATH only if not already present.
- Export ACCELSIM_REPO.
- Export ACCELSIM_ROOT=$ACCELSIM_REPO/gpu-simulator.
- Export GPGPUSIM_ROOT=$ACCELSIM_ROOT/gpgpu-sim.
- Export GPUWATTCH_ROOT=$GPGPUSIM_ROOT.
- Source gpu-simulator/setup_environment.sh if it exists.
- Do not print excessive output unless ACCELSIM_ENV_VERBOSE=1.
- Return nonzero if sourced from a shell and required paths are missing, but avoid killing the parent shell.

Implementation note:
Because this file is meant to be sourced, use return where possible and only use exit if the script is executed directly. Keep it POSIX-ish bash.

## Required tracked check script

Create:

    scripts/accelsim/a0_env_check.sh

Required behavior:

- cd to repo root.
- Source scripts/accelsim/accelsim_env.sh.
- Print:
  - date
  - hostname
  - pwd
  - git branch
  - git commit
  - CUDA_INSTALL_PATH
  - CUDA_HOME
  - CUDA_PATH
  - ACCELSIM_ROOT
  - GPGPUSIM_ROOT
  - GPUWATTCH_ROOT
  - nvcc --version
  - gcc --version first lines
  - g++ --version first lines
  - cmake --version
  - python3 --version
  - pip3 --version
  - python import check for yaml, numpy, pandas, matplotlib, scipy, plotly, psutil, requests, six
  - git status --short
- Write full output to .local_reports/A0_env_check_TIMESTAMP.log.
- Also write a concise markdown report to .local_reports/A0_env_check_TIMESTAMP.md.
- Return success only if required env paths exist and git status is clean except tracked files that are being intentionally edited during the Codex round.

## Commands Codex should run in A0

After creating the scripts:

    bash scripts/accelsim/a0_env_check.sh

Then inspect:

    git status --short
    ls -la .local_reports | tail

## A0 pass criteria

- scripts/accelsim/accelsim_env.sh exists and is sourceable.
- scripts/accelsim/a0_env_check.sh exists and runs.
- CUDA_HOME and CUDA_PATH are no longer empty after sourcing env script.
- GPGPUSIM_ROOT is set and points to gpu-simulator/gpgpu-sim.
- Runtime dirs do not appear in git status.
- A0 report exists under .local_reports.
