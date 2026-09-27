#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-l2-lifetime-control-v1r1
python=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/env/bin/python
ncu=/opt/nvidia/nsight-compute/2025.1.1/ncu
directory="$root/raw/ncu/ARENA_PAIR"
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
"$ncu" --nvtx --nvtx-include 'R101R1_NCU_ARENA_L512_A0]' \
    --nvtx-include 'R101R1_NCU_ARENA_L512_D2]' \
    --devices 0 --target-processes application-only \
    --graph-profiling node --replay-mode application \
    --cache-control none --clock-control none --pipeline-boost-state dynamic \
    --metrics dram__bytes_read.sum,dram__bytes_write.sum,lts__t_bytes.sum,sm__cycles_active.sum,launch__registers_per_thread,launch__shared_mem_per_block \
    --force-overwrite --export "$directory/ARENA_PAIR" \
    "$python" "$worktree/util/vm_tlb/awma/r101_l2_lifetime_control_v1r1/arena_ncu_target.py" \
    >"$directory/ncu.stdout.log" 2>"$directory/ncu.stderr.log"
flock -u 9
"$ncu" --import "$directory/ARENA_PAIR.ncu-rep" --csv --page raw \
    >"$directory/ARENA_PAIR.raw.csv"
tail -3 "$directory/ncu.stdout.log"
echo NCU_COMPLETE_ARENA_PAIR
