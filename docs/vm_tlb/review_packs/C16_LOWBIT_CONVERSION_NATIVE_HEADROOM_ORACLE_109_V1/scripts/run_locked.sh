#!/usr/bin/env bash
set -euo pipefail
LOCK=/data/c16/locks/c16_gpu_campaign.lock
PYTHON=/data/c16/env/c16-awq-v6/bin/python
RUNNER=${1:?runner required}
EXTENSION=${2:?extension required}
EXPECTED_SHA=${3:?extension sha required}
ISOLATION=${4:?isolation audit required}
RAW=${5:?raw output directory required}
mkdir -p "$RAW"
test "$(sha256sum "$EXTENSION" | awk '{print $1}')" = "$EXPECTED_SHA"
exec 9>"$LOCK"
if ! flock -w 2700 9; then
  printf '%s\n' GPU_LOCK_45MIN_TIMEOUT_STOP >"$RAW/GPU_LOCK_45MIN_TIMEOUT_STOP"
  exit 75
fi
START=$(date -u +%Y-%m-%dT%H:%M:%SZ)
printf '%s\n' "$START" >"$RAW/GPU_LOCK_START_UTC.txt"
cleanup() {
  code=$?
  END=$(date -u +%Y-%m-%dT%H:%M:%SZ)
  printf '%s\n' "$END" >"$RAW/GPU_LOCK_END_UTC.txt"
  printf '{"lock":"%s","start_utc":"%s","end_utc":"%s","exit_code":%d}\n' "$LOCK" "$START" "$END" "$code" >"$RAW/GPU_LOCK_RECEIPT.json"
  flock -u 9 || true
  exit "$code"
}
trap cleanup EXIT INT TERM
nvidia-smi --query-gpu=name,uuid,compute_cap,memory.total,memory.free --format=csv,noheader >"$RAW/GPU_PRE.csv"
"$PYTHON" "$RUNNER" --extension "$EXTENSION" --out "$RAW" --isolation-audit "$ISOLATION"
nvidia-smi --query-gpu=name,uuid,compute_cap,memory.total,memory.free --format=csv,noheader >"$RAW/GPU_POST.csv"
printf '%s\n' PASS >"$RAW/LOCKED_CAMPAIGN_COMPLETE"
