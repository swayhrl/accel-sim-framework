#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r54_fastpath_requal_v1r1_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r54-fastpath-requal-v1r1
export HF_HOME="$ROOT/hf_home"
export HF_ENDPOINT=https://hf-mirror.com
unset HF_HUB_OFFLINE
export HF_HUB_DISABLE_XET=1
export USE_HUB_KERNELS=YES
export PYTHONUNBUFFERED=1
mkdir -p "$ROOT/raw/fastpath" "$ROOT/logs"
/usr/local/bin/nsys profile \
  --trace=cuda,nvtx,osrt,cublas \
  --sample=none \
  --cpuctxsw=none \
  --force-overwrite=true \
  --output="$ROOT/raw/fastpath/r54_v1r1_fastpath" \
  "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/r54_fastpath_requal_v1r1/fastpath_canary.py" \
  2>&1 | tee "$ROOT/logs/fastpath_canary.log"
