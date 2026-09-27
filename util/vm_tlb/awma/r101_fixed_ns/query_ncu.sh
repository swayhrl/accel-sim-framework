#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927
NCU=/opt/nvidia/nsight-compute/2025.1.1/ncu
flock -x /data/c16/locks/c16_gpu_campaign.lock \
  "$NCU" --query-metrics --devices 0 --query-metrics-mode base \
  >"$ROOT/logs/ncu_available_metrics.txt" 2>"$ROOT/logs/ncu_query.stderr.log"
grep -E '^dram__bytes_(read|write)|^lts__t_bytes|^sm__cycles_active|^sm__warps_active|^launch__registers_per_thread|^launch__shared_mem_per_block' \
  "$ROOT/logs/ncu_available_metrics.txt" | head -35
flock -x /data/c16/locks/c16_gpu_campaign.lock \
  "$NCU" --query-metrics-mode suffix --devices 0 \
    --metrics dram__bytes_read,dram__bytes_write,lts__t_bytes,sm__cycles_active,sm__warps_active \
  >"$ROOT/logs/ncu_metric_suffixes.txt" 2>"$ROOT/logs/ncu_suffix_query.stderr.log"
grep -E 'dram__bytes_read|dram__bytes_write|lts__t_bytes|sm__cycles_active|sm__warps_active' \
  "$ROOT/logs/ncu_metric_suffixes.txt" | head -45
