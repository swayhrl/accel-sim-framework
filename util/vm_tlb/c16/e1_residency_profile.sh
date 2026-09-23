#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-residency-intervention-109-v1
OUT=/data/c16/e1_residency_intervention_v1
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing concurrent profiling" >&2
  exit 75
fi

mkdir -p "$OUT/ncu/reports" "$OUT/ncu/logs"
cd "$REPO"

run_ncu() {
  local point_id=$1
  local range_name=$2
  shift 2
  "$NCU" --nvtx --nvtx-include "${range_name}/" \
    --target-processes application-only \
    --replay-mode application \
    --cache-control none \
    --metrics "$METRICS" \
    --force-overwrite \
    -o "$OUT/ncu/reports/$point_id" \
    "$PYTHON" util/vm_tlb/c16/e1_residency_ncu_replay.py "$@" \
    2>&1 | tee "$OUT/ncu/logs/$point_id.log"
}

run_text() {
  local role=$1
  local matrix_m=$2
  local implementation=$3
  local state=$4
  local short_impl=AWQ
  if [[ "$implementation" == RAW_FP16 ]]; then short_impl=RAW; fi
  local point_id="TEXT_${role}_M${matrix_m}_${short_impl}_${state}"
  local range_name="C16_E1_RES_TEXT_${role^^}_M${matrix_m}_${short_impl}_${state}"
  run_ncu "$point_id" "$range_name" --input-kind TEXT --role "$role" --M "$matrix_m" --impl "$implementation" --state "$state"
}

run_code() {
  local implementation=$1
  local state=$2
  local short_impl=AWQ
  if [[ "$implementation" == RAW_FP16 ]]; then short_impl=RAW; fi
  local point_id="CODE_down_proj_M1_${short_impl}_${state}"
  local range_name="C16_E1_RES_CODE_DOWN_PROJ_M1_${short_impl}_${state}"
  run_ncu "$point_id" "$range_name" --input-kind CODE --role down_proj --M 1 --impl "$implementation" --state "$state"
}

# One shared-buffer pressure qualification process with both ranges.
"$NCU" --nvtx \
  --nvtx-include "C16_E1_PRESSURE_SPARSE_256MIB/" \
  --nvtx-include "C16_E1_PRESSURE_DENSE_256MIB/" \
  --target-processes application-only \
  --replay-mode application \
  --cache-control none \
  --metrics "$METRICS" \
  --force-overwrite \
  -o "$OUT/ncu/reports/PRESSURE_QUALIFICATION" \
  "$PYTHON" util/vm_tlb/c16/e1_residency_pressure_qualification.py \
  2>&1 | tee "$OUT/ncu/logs/PRESSURE_QUALIFICATION.log"

for role in q_proj down_proj up_proj; do
  for implementation in RAW_FP16 AWQ_FP16_INPUT; do
    run_text "$role" 1 "$implementation" WARM
    run_text "$role" 1 "$implementation" SPARSE_PAGE_PRESSURE
    run_text "$role" 1 "$implementation" DENSE_MEMORY_PRESSURE
  done
done

for implementation in RAW_FP16 AWQ_FP16_INPUT; do
  run_text up_proj 256 "$implementation" WARM
  run_text up_proj 256 "$implementation" DENSE_MEMORY_PRESSURE
done

# Native dose response is material for up_proj M1 AWQ; only the pre-authorized 64 MiB points are added.
for implementation in RAW_FP16 AWQ_FP16_INPUT; do
  run_text up_proj 1 "$implementation" DOSE64
done

# TEXT down_proj M1 AWQ dense intervention is material; run the pre-authorized CODE WARM/DENSE profiles.
for implementation in RAW_FP16 AWQ_FP16_INPUT; do
  run_code "$implementation" WARM
  run_code "$implementation" DENSE_MEMORY_PRESSURE
done

printf 'PASS\n' > "$OUT/ncu/PROFILE_COMPLETE"
