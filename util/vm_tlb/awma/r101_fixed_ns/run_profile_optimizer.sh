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
for edge in 256 512; do
  dir="$ROOT/raw/nsys/optimizer_L$edge"
  mkdir -p "$dir"
  flock -x /data/c16/locks/c16_gpu_campaign.lock \
    /usr/local/bin/nsys profile --trace=cuda,nvtx,osrt,cublas \
      --cuda-graph-trace=node --sample=none --cpuctxsw=none \
      --force-overwrite=true --output="$dir/optimizer_L$edge" \
      "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/r101_fixed_ns/profile_optimizer.py" --edge "$edge" \
      >"$dir/nsys.stdout.log" 2>"$dir/nsys.stderr.log"
  /usr/local/bin/nsys export --type sqlite --force-overwrite=true \
    --output="$dir/optimizer_L$edge.sqlite" "$dir/optimizer_L$edge.nsys-rep" >/dev/null 2>&1
  echo "OPTIMIZER_NSYS_COMPLETE L$edge"
done
