#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-fixed-ns-v1
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
export PYTHONUNBUFFERED=1
flock -x /data/c16/locks/c16_gpu_campaign.lock \
  "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/r101_fixed_ns/graph_control.py" \
  >"$ROOT/logs/graph_control.stdout.log" \
  2>"$ROOT/logs/graph_control.stderr.log"
tail -5 "$ROOT/logs/graph_control.stdout.log"
