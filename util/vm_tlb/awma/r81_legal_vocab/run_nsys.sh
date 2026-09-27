#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r81_legal_vocab_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r81-legal-vocab-v1
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
export PYTHONUNBUFFERED=1
for arm in A0_DENSE_VENDOR A1_DENSE_FUSED A2_INDEXED_UNION A3_RAGGED_DIRECT; do
  dir="$ROOT/raw/nsys/C1_HETEROGENEOUS_DISCOVERY/$arm"
  mkdir -p "$dir"
  flock -x /data/c16/locks/c16_gpu_campaign.lock \
    /usr/local/bin/nsys profile --trace=cuda,nvtx,osrt,cublas \
      --sample=none --cpuctxsw=none --force-overwrite=true \
      --output="$dir/$arm" \
      "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/r81_legal_vocab/profile_canary.py" --arm "$arm" \
      >"$dir/nsys.stdout.log" 2>"$dir/nsys.stderr.log"
  /usr/local/bin/nsys export --type sqlite --force-overwrite=true \
    --output="$dir/$arm.sqlite" "$dir/$arm.nsys-rep" >/dev/null 2>&1
  echo "NSYS_COMPLETE $arm"
done
