#!/usr/bin/env bash
set -euo pipefail
arm="$1"
ROOT=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-fixed-ns-v1
NCU=/opt/nvidia/nsight-compute/2025.1.1/ncu
dir="$ROOT/raw/ncu/$arm"
mkdir -p "$dir"
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
export PYTHONUNBUFFERED=1
flock -x /data/c16/locks/c16_gpu_campaign.lock \
  "$NCU" --nvtx --nvtx-include "R101_NCU_$arm]" \
    --devices 0 --target-processes application-only \
    --cache-control none --clock-control none --pipeline-boost-state dynamic \
    --metrics dram__bytes_read.sum,dram__bytes_write.sum,lts__t_bytes.sum,sm__cycles_active.sum,sm__warps_active.avg.pct_of_peak_sustained_active \
    --force-overwrite --export "$dir/$arm" \
    "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/r101_fixed_ns/ncu_target.py" --arm "$arm" \
    >"$dir/ncu.stdout.log" 2>"$dir/ncu.stderr.log"
"$NCU" --import "$dir/$arm.ncu-rep" --csv --page raw >"$dir/$arm.raw.csv"
tail -4 "$dir/ncu.stdout.log"
echo "NCU_COMPLETE $arm"
