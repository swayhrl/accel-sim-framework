#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101_transient_l2_sim_capture_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-transient-l2-sim-capture-109-v1
python=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/env/bin/python
export HF_HOME="$root/cache/hf"
export TRITON_CACHE_DIR="$root/cache/triton"
export CUDA_CACHE_PATH="$root/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$root/cache/inductor"
export XDG_CACHE_HOME="$root/cache/xdg"
export TMPDIR="$root/tmp"
export PYTHONUNBUFFERED=1
mkdir -p "$root/cache/hf" "$root/cache/triton" "$root/cache/cuda" \
    "$root/cache/inductor" "$root/cache/xdg" "$root/tmp" "$root/raw/audit"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
"$python" "$worktree/util/vm_tlb/awma/r101_transient_capture/capture_driver.py" \
    --mode audit --outdir "$root/raw/audit"
