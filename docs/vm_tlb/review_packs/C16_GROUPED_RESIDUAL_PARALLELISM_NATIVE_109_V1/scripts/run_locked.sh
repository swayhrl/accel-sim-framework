#!/usr/bin/env bash
set -euo pipefail
LOCK=/data/c16/locks/c16_gpu_campaign.lock
PYTHON=/data/c16/env/c16-awq-v6/bin/python
NCU=/opt/nvidia/nsight-compute/2025.1.1/target/linux-desktop-glibc_2_11_3-x64/ncu
RUNNER=${1:?runner path required}
EXTENSION=${2:?extension path required}
RAW=${3:?raw output directory required}
EXPECTED_EXT_SHA=${4:?expected extension sha256 required}
METRICS=lts__t_sectors_srcunit_tex_op_read_lookup_hit.sum,lts__t_sectors_srcunit_tex_op_read_lookup_miss.sum,l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum,gpu__time_duration.sum,sm__warps_active.avg.pct_of_peak_sustained_elapsed
mkdir -p "$RAW"
test "$(sha256sum "$EXTENSION" | awk '{print $1}')" = "$EXPECTED_EXT_SHA"
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
nvidia-smi -q >"$RAW/NVIDIA_SMI_PRE.txt"
"$PYTHON" "$RUNNER" campaign --extension "$EXTENSION" --out "$RAW"
for m in 1 16 32 64; do
  for split in 8 1; do
    label="C16_RESIDUAL_M${m}_S${split}"
    stem="$RAW/ncu_M${m}_S${split}"
    "$NCU" --target-processes all --replay-mode application --cache-control none \
      --nvtx --nvtx-include "${label}]" --disable-extra-suffixes --metrics "$METRICS" \
      --force-overwrite -o "$stem" \
      "$PYTHON" "$RUNNER" profile --extension "$EXTENSION" --m "$m" --split "$split" \
      >"${stem}.stdout.log" 2>"${stem}.stderr.log"
    "$NCU" --import "${stem}.ncu-rep" --csv --page raw >"${stem}.csv" 2>"${stem}.export.log"
  done
done
nvidia-smi -q >"$RAW/NVIDIA_SMI_POST.txt"
printf '%s\n' PASS >"$RAW/LOCKED_CAMPAIGN_COMPLETE"
