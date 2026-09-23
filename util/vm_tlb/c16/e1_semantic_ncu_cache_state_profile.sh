#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-semantic-ncu-cache-state-repair-109-v1
OUT=/data/c16/e1_semantic_ncu_cache_state_repair_v1
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
REPLAY=util/vm_tlb/c16/e1_semantic_ncu_replay.py
METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing concurrent profiling" >&2
  exit 75
fi

mkdir -p "$OUT/reports" "$OUT/logs" "$OUT/environment"
cd "$REPO"

"$NCU" --version > "$OUT/environment/NCU_VERSION.txt"
"$NCU" --help > "$OUT/environment/NCU_HELP.txt"

profile_point() {
  local point_id=$1
  local range_name=$2
  local matrix_m=$3
  local implementation=$4

  "$NCU" \
    --nvtx \
    --nvtx-include "${range_name}/" \
    --target-processes application-only \
    --replay-mode application \
    --cache-control none \
    --metrics "$METRICS" \
    --force-overwrite \
    -o "$OUT/reports/$point_id" \
    "$PYTHON" "$REPLAY" --M "$matrix_m" --impl "$implementation" \
    2>&1 | tee "$OUT/logs/$point_id.log"
}

profile_point M1_RAW C16_E1_NCU_UP_M1_RAW_FP16 1 RAW_FP16
profile_point M1_AWQ C16_E1_NCU_UP_M1_AWQ 1 AWQ
profile_point M256_RAW C16_E1_NCU_UP_M256_RAW_FP16 256 RAW_FP16
profile_point M256_AWQ C16_E1_NCU_UP_M256_AWQ 256 AWQ

printf 'PASS\n' > "$OUT/PROFILE_COMPLETE"
