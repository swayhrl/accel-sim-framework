#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-fixed-ns-v1
export HF_HOME="$root/cache/hf"
export TRITON_CACHE_DIR="$root/cache/triton"
export CUDA_CACHE_PATH="$root/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$root/cache/inductor"
export XDG_CACHE_HOME="$root/cache/xdg"
export TMPDIR="$root/tmp"
export PYTHONUNBUFFERED=1
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
"$root/env/bin/python" "$worktree/util/vm_tlb/awma/r101_fixed_ns/holdout_optimizer.py"
