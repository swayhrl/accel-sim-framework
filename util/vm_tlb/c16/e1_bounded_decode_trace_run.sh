#!/usr/bin/env bash
set -euo pipefail
mode=${1:?mode census, canary, or formal}
run=${2:?run directory}
prefix_start=${3:--1}
prefix_end=${4:--1}
repo=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-bounded-decode-trace-109-v1
tool=/data/c16/e1_bounded_decode_trace_v1/bin/route_b_bounded_decode.so
python=/data/c16/env/c16-py310/bin/python
driver="$repo/util/vm_tlb/c16/e1_bounded_decode_trace_driver.py"
mkdir -p "$run/raw"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -n 9 || { echo GPU_LOCK_BUSY; exit 75; }
export PATH=/usr/local/cuda-12.8/bin:$PATH
export NVDISASM=/usr/local/cuda-12.8/bin/nvdisasm
export NO_EAGER_LOAD=0
df -B1 /data > "$run/disk_before.txt"
nvidia-smi --query-gpu=uuid,memory.used,memory.free --format=csv,noheader > "$run/gpu_before.csv"
common=(CUDA_INJECTION64_PATH="$tool" TOOL_VERBOSE=0 PYTHONUNBUFFERED=1)
if [[ "$mode" == census ]]; then
 env "${common[@]}" ROUTE_B_LAUNCH_CENSUS_ONLY=1 "$python" "$driver" --mode "$mode" \
  --receipt "$run/DRIVER_RECEIPT.json" --qweight-sidecar "$run/ORACLE_QWEIGHT_REGIONS.json" \
  --events "$run/DRIVER_EVENTS.jsonl" > "$run/stdout.log" 2> "$run/stderr.log"
else
 [[ "$prefix_start" =~ ^[0-9]+$ && "$prefix_end" =~ ^[0-9]+$ && "$prefix_end" -ge "$prefix_start" ]]
 env "${common[@]}" ROUTE_B_RAW_DIR="$run/raw" ROUTE_B_PREFIX_START="$prefix_start" ROUTE_B_PREFIX_END="$prefix_end" \
  "$python" "$driver" --mode "$mode" --receipt "$run/DRIVER_RECEIPT.json" \
  --qweight-sidecar "$run/ORACLE_QWEIGHT_REGIONS.json" --events "$run/DRIVER_EVENTS.jsonl" \
  > "$run/stdout.log" 2> "$run/stderr.log"
fi
grep -q '^C16_TRACE_DRIVER_COMPLETE ' "$run/stdout.log"
test -s "$run/DRIVER_RECEIPT.json"
test -s "$run/ORACLE_QWEIGHT_REGIONS.json"
if [[ "$mode" != census ]]; then
 expected=$((prefix_end-prefix_start+1))
 actual=$(find "$run/raw" -maxdepth 1 -type f -name 'kernel-*.trace.xz' | wc -l)
 [[ "$actual" -eq "$expected" ]]
 [[ $(grep -c '^ROUTEB_TERMINAL_COMPLETE ' "$run/stdout.log") -eq "$expected" ]]
 test -z "$(find "$run/raw" -maxdepth 1 -type f -name '*.partial' -print -quit)"
fi
df -B1 /data > "$run/disk_after.txt"
nvidia-smi --query-gpu=uuid,memory.used,memory.free --format=csv,noheader > "$run/gpu_after.csv"
sha256sum "$run/DRIVER_RECEIPT.json" "$run/ORACLE_QWEIGHT_REGIONS.json" "$run/DRIVER_EVENTS.jsonl" "$run/stdout.log" "$run/stderr.log" > "$run/CONTROL_SHA256SUMS"
echo C16_BOUNDED_DECODE_TRACE_RUN_PASS mode="$mode" run="$run"
