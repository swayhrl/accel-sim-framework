#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101r2_s128_native_profile_20260929
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101r2-s128-native-profile-109-v1
python=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/env/bin/python
export HF_HOME="$root/cache/hf"
export TRITON_CACHE_DIR="$root/cache/triton"
export CUDA_CACHE_PATH="$root/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$root/cache/inductor"
export XDG_CACHE_HOME="$root/cache/xdg"
export TMPDIR="$root/tmp"
export PYTHONUNBUFFERED=1
mkdir -p "$root/raw/nsys" "$root/logs"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
/usr/local/bin/nsys profile --trace=cuda,nvtx,osrt,cublas \
    --cuda-graph-trace=node --sample=none --cpuctxsw=none \
    --force-overwrite=true --output="$root/raw/nsys/s128_path" \
    "$python" "$worktree/util/vm_tlb/awma/r101r2_native_profile/path_canary.py" \
    > "$root/logs/path_nsys.stdout.log" \
    2> "$root/logs/path_nsys.stderr.log"
flock -u 9
/usr/local/bin/nsys export --type sqlite --force-overwrite=true \
    --output="$root/raw/nsys/s128_path.sqlite" \
    "$root/raw/nsys/s128_path.nsys-rep" >/dev/null 2>&1
tail -3 "$root/logs/path_nsys.stdout.log"
