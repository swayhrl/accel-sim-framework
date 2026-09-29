#!/usr/bin/env bash
set -euo pipefail
arm="${1:?F128 or K128}"
case "$arm" in F128|K128) ;; *) echo 'unregistered arm' >&2; exit 2 ;; esac
root=/data/c16/awma/r101r2_s128_native_profile_20260929
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r2-s128-native-profile-109-v1
python=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/env/bin/python
ncu=/opt/nvidia/nsight-compute/2025.1.1/ncu
directory="$root/raw/ncu/$arm"
mkdir -p "$directory"
metrics=$(jq -r '[.selected_profile_metrics[], .selected_launch_metrics[]] | join(",")' "$root/NCU_METRIC_SET.json")
test -n "$metrics"
export HF_HOME="$root/cache/hf"
export TRITON_CACHE_DIR="$root/cache/triton"
export CUDA_CACHE_PATH="$root/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$root/cache/inductor"
export XDG_CACHE_HOME="$root/cache/xdg"
export TMPDIR="$root/tmp"
export PYTHONUNBUFFERED=1
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
timeout --signal=TERM 1800 \
    "$ncu" --nvtx --nvtx-include "R101R2_NCU_${arm}]" \
    --devices 0 --target-processes application-only \
    --graph-profiling node --replay-mode application \
    --cache-control none --clock-control none --pipeline-boost-state dynamic \
    --metrics "$metrics" --force-overwrite --export "$directory/$arm" \
    "$python" "$worktree/util/vm_tlb/awma/r101r2_native_profile/ncu_target.py" \
    --arm "$arm" > "$directory/ncu.stdout.log" 2> "$directory/ncu.stderr.log"
flock -u 9
"$ncu" --import "$directory/$arm.ncu-rep" --csv --page raw \
    > "$directory/$arm.raw.csv"
tail -4 "$directory/ncu.stdout.log"
echo "NCU_COMPLETE $arm"
