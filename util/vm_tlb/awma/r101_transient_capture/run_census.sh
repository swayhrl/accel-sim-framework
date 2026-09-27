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
export PATH=/usr/local/cuda-12.8/bin:$PATH
export NVDISASM=/usr/local/cuda-12.8/bin/nvdisasm
export NO_EAGER_LOAD=1
export CUDA_INJECTION64_PATH="$root/bin/route_b_r101_multi.so"
export ROUTE_B_RAW_DIR="$root/raw/census/traces"
export ROUTE_B_FUNCTION_REGEX='.*'
export ROUTE_B_MULTI_SELECTED_COUNT=64
export ROUTE_B_LAUNCH_CENSUS_ONLY=1
export TOOL_VERBOSE=0
export PYTHONUNBUFFERED=1
mkdir -p "$root/raw/census" "$root/logs"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
"$python" "$worktree/util/vm_tlb/awma/r101_transient_capture/capture_driver.py" \
    --mode census --outdir "$root/raw/census" \
    > "$root/logs/census.stdout.log" 2> "$root/logs/census.stderr.log"
flock -u 9
tail -5 "$root/logs/census.stdout.log"
