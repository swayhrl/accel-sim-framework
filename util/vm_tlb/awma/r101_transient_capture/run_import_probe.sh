#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101_transient_l2_sim_capture_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-transient-l2-sim-capture-109-v1
export PATH=/usr/local/cuda-12.8/bin:$PATH
export NVDISASM=/usr/local/cuda-12.8/bin/nvdisasm
export NO_EAGER_LOAD=1
export CUDA_INJECTION64_PATH="$root/bin/route_b_r101_multi.so"
export ROUTE_B_LAUNCH_CENSUS_ONLY=1
export ROUTE_B_FUNCTION_REGEX='.*'
export ROUTE_B_MULTI_SELECTED_COUNT=1
export ROUTE_B_RAW_DIR="$root/raw/import_probe"
export TOOL_VERBOSE=0
export PYTHONUNBUFFERED=1
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
timeout --signal=TERM 90 \
    /data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927/env/bin/python \
    "$worktree/util/vm_tlb/awma/r101_transient_capture/import_probe.py" \
    > "$root/logs/import_probe.stdout.log" \
    2> "$root/logs/import_probe.stderr.log"
flock -u 9
tail -8 "$root/logs/import_probe.stdout.log"
