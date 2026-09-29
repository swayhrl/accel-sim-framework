#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101r2_s128_native_profile_20260929
ncu=/opt/nvidia/nsight-compute/2025.1.1/ncu
mkdir -p "$root/raw" "$root/logs" "$root/cache/triton" "$root/cache/inductor" \
    "$root/cache/cuda" "$root/cache/xdg" "$root/tmp"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
"$ncu" --version > "$root/raw/ncu_version.txt"
"$ncu" --query-metrics-mode all --devices 0 \
    > "$root/raw/ncu_supported_all.txt" \
    2> "$root/logs/ncu_metric_query.stderr.log"
"$ncu" --query-metrics-mode all --query-metrics-collection launch --devices 0 \
    > "$root/raw/ncu_supported_launch.txt" \
    2> "$root/logs/ncu_launch_metric_query.stderr.log"
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap \
    --format=csv,noheader > "$root/raw/gpu_identity.txt"
flock -u 9
wc -l "$root/raw/ncu_supported_all.txt"
cat "$root/raw/gpu_identity.txt"
