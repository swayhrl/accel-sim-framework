#!/usr/bin/env bash
# Lightweight NSYS/CUPTI census only.  No NCU, NVBit, traceg, or simulator action.
set -euo pipefail
if [ "$#" -ne 8 ]; then
  echo "usage: $0 SCENARIO TOKENS SHA256 B PREFILL DECODE INPUT_AUTHORITY RUN_DIR" >&2
  exit 64
fi
scenario=$1; tokens=$2; expected=$3; batch=$4; prefill=$5; decode=$6; authority=$7; run=$8
repo=/home/huangrulin/workspace/worktrees/accel-sim-awma-qwen25-cross-context-census-v1
driver="$repo/util/vm_tlb/awma/kernel_census/qwen25_cross_context_driver.py"
mkdir -p "$run"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -n 9 || { echo GPU_LOCK_BUSY; exit 75; }
cp "$driver" "$run/driver.py"
sha256sum "$run/driver.py" "$tokens" > "$run/INPUT_AND_DRIVER_SHA256SUMS"
nvidia-smi --query-gpu=name,uuid,memory.used,driver_version --format=csv,noheader > "$run/gpu_before.csv"
nsys profile --force-overwrite=true --trace=cuda,nvtx --sample=none --output "$run/census" \
  /data/c16/env/c16-py310/bin/python "$run/driver.py" \
  --scenario "$scenario" --tokens "$tokens" --expected-sha256 "$expected" \
  --batch "$batch" --prefill "$prefill" --decode "$decode" --input-authority "$authority" \
  > "$run/driver.stdout" 2> "$run/driver.stderr"
grep -q AWMA_QWEN25_CROSS_CONTEXT_CENSUS_EXECUTION_COMPLETE "$run/driver.stdout"
nsys export --type sqlite --force-overwrite true --output "$run/census.sqlite" "$run/census.nsys-rep" > "$run/nsys_export.stdout" 2> "$run/nsys_export.stderr"
nsys stats --report cuda_gpu_trace --format csv --output "$run/cuda_gpu_trace" "$run/census.nsys-rep" > "$run/nsys_gpu_stats.stdout" 2> "$run/nsys_gpu_stats.stderr" || true
nsys stats --report nvtxpptrace --format csv --output "$run/nvtx_trace" "$run/census.nsys-rep" > "$run/nsys_nvtx_stats.stdout" 2> "$run/nsys_nvtx_stats.stderr" || true
nvidia-smi --query-gpu=name,uuid,memory.used,driver_version --format=csv,noheader > "$run/gpu_after.csv"
sha256sum "$run"/* > "$run/SHA256SUMS"
echo "NSYS_CENSUS_CAPTURE_PASS scenario=$scenario run=$run"
