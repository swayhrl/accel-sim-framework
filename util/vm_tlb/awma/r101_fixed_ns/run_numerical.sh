#!/usr/bin/env bash
set -euo pipefail
which="$1"
ROOT=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-fixed-ns-v1
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
export PYTHONUNBUFFERED=1
mkdir -p "$HF_HOME" "$TRITON_CACHE_DIR" "$CUDA_CACHE_PATH" "$TORCHINDUCTOR_CACHE_DIR" "$XDG_CACHE_HOME" "$TMPDIR" "$ROOT/logs"
flock -x /data/c16/locks/c16_gpu_campaign.lock \
  "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/r101_fixed_ns/numerical_canary.py" \
  --which "$which" \
  >"$ROOT/logs/numerical_${which}.stdout.log" \
  2>"$ROOT/logs/numerical_${which}.stderr.log"
tail -1 "$ROOT/logs/numerical_${which}.stdout.log"
