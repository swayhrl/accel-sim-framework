#!/usr/bin/env bash
set -euo pipefail
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -n 9 || { echo GPU_LOCK_BUSY; exit 75; }
export PATH=/usr/local/cuda-12.8/bin:$PATH
run=/data/c16/awma/qwen25_s2_kernel_census_20260917T$(date -u +%H%M%SZ)
mkdir -p "$run"
cp /tmp/q05_s2_kernel_census_driver.py "$run/driver.py"
sha256sum "$run/driver.py" > "$run/driver_SHA256SUMS"
nvidia-smi --query-gpu=uuid,memory.used,driver_version --format=csv,noheader > "$run/gpu_before.csv"
nsys profile --force-overwrite=true --trace=cuda,nvtx --sample=none --output "$run/qwen25_s2_census" \
  /data/c16/env/c16-py310/bin/python "$run/driver.py" > "$run/driver.stdout" 2> "$run/driver.stderr"
grep -q EXACT_Q05_S2_KERNEL_CENSUS_EXECUTION_COMPLETE "$run/driver.stdout"
nsys export --type sqlite --force-overwrite true --output "$run/qwen25_s2_census.sqlite" "$run/qwen25_s2_census.nsys-rep" > "$run/nsys_export.stdout" 2> "$run/nsys_export.stderr" || true
nsys stats --report cuda_gpu_trace --format csv --output "$run/cuda_gpu_trace" "$run/qwen25_s2_census.nsys-rep" > "$run/nsys_gpu_stats.stdout" 2> "$run/nsys_gpu_stats.stderr"
nsys stats --report nvtxpptrace --format csv --output "$run/nvtx_trace" "$run/qwen25_s2_census.nsys-rep" > "$run/nsys_nvtx_stats.stdout" 2> "$run/nsys_nvtx_stats.stderr"
nvidia-smi --query-gpu=uuid,memory.used,driver_version --format=csv,noheader > "$run/gpu_after.csv"
sha256sum "$run"/* > "$run/SHA256SUMS"
echo NSYS_CENSUS_CAPTURE_PASS run="$run"
