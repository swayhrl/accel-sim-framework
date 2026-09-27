#!/usr/bin/env bash
set -euo pipefail
shape="${1:?K128 or L512}"
arm="${2:?B0 or D1}"
case "$shape:$arm" in
    K128:B0|K128:D1|L512:B0|L512:D1) ;;
    *) echo 'unregistered NCU target' >&2; exit 2 ;;
esac
root=/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-l2-lifetime-control-v1r1
python=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/env/bin/python
ncu=/opt/nvidia/nsight-compute/2025.1.1/ncu
target="$shape"_"$arm"
directory="$root/raw/ncu/$target"
mkdir -p "$directory"
export HF_HOME="$root/cache/hf"
export TRITON_CACHE_DIR="$root/cache/triton"
export CUDA_CACHE_PATH="$root/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$root/cache/inductor"
export XDG_CACHE_HOME="$root/cache/xdg"
export TMPDIR="$root/tmp"
export PYTHONUNBUFFERED=1
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
"$ncu" --nvtx --nvtx-include "R101R1_NCU_${target}]" \
    --devices 0 --target-processes application-only \
    --graph-profiling node --replay-mode application \
    --cache-control none --clock-control none --pipeline-boost-state dynamic \
    --metrics dram__bytes_read.sum,dram__bytes_write.sum,lts__t_bytes.sum,sm__cycles_active.sum,launch__registers_per_thread,launch__shared_mem_per_block \
    --force-overwrite --export "$directory/$target" \
    "$python" "$worktree/util/vm_tlb/awma/r101_l2_lifetime_control_v1r1/ncu_target.py" \
    --shape "$shape" --arm "$arm" \
    >"$directory/ncu.stdout.log" 2>"$directory/ncu.stderr.log"
flock -u 9
"$ncu" --import "$directory/$target.ncu-rep" --csv --page raw \
    >"$directory/$target.raw.csv"
tail -3 "$directory/ncu.stdout.log"
echo "NCU_COMPLETE $target"
