#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-natural-reuse-residency-109-v1
OUT=/data/c16/e1_natural_reuse_residency_v1
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
TRAFFIC_METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing concurrent profiling" >&2
  exit 75
fi

mkdir -p "$OUT/ncu/refill/reports" "$OUT/ncu/refill/logs" \
         "$OUT/ncu/knee/reports" "$OUT/ncu/knee/logs" \
         "$OUT/ncu/natural/reports" "$OUT/ncu/natural/logs"
cd "$REPO"

run_profile() {
  local family=$1
  local profile_id=$2
  local range_name=$3
  local metrics=$4
  shift 4
  "$NCU" --nvtx --nvtx-include "${range_name}/" \
    --target-processes application-only \
    --replay-mode application \
    --cache-control none \
    --metrics "$metrics" \
    --force-overwrite \
    -o "$OUT/ncu/$family/reports/$profile_id" \
    "$PYTHON" "$@" \
    > "$OUT/ncu/$family/logs/$profile_id.log" 2>&1
  echo "PASS $family/$profile_id"
}

for role in q_proj down_proj up_proj; do
  for implementation in RAW_FP16 AWQ_FP16_INPUT; do
    short_impl=AWQ
    if [[ "$implementation" == RAW_FP16 ]]; then short_impl=RAW; fi
    for selected_k in 1 2 4; do
      profile_id="${role}_M1_${short_impl}_K${selected_k}"
      range_name="C16_E1_REFILL_${role^^}_${short_impl}_K${selected_k}"
      run_profile refill "$profile_id" "$range_name" "$TRAFFIC_METRICS" \
        util/vm_tlb/c16/e1_refill_ncu_replay.py --role "$role" --impl "$implementation" --selected-k "$selected_k"
    done
  done
done

for dose in 0 32 48 56 60 64 72 96; do
  run_profile knee "q_proj_${dose}MIB" "C16_E1_KNEE_Q_PROJ_${dose}MIB" dram__bytes.sum \
    util/vm_tlb/c16/e1_knee_ncu_replay.py --role q_proj --dose-mib "$dose"
done
for dose in 0 16 24 28 32 36 48 64; do
  run_profile knee "down_proj_${dose}MIB" "C16_E1_KNEE_DOWN_PROJ_${dose}MIB" dram__bytes.sum \
    util/vm_tlb/c16/e1_knee_ncu_replay.py --role down_proj --dose-mib "$dose"
done
for dose in 0 16 24 28 30 32 36 40 48 64; do
  run_profile knee "up_proj_${dose}MIB" "C16_E1_KNEE_UP_PROJ_${dose}MIB" dram__bytes.sum \
    util/vm_tlb/c16/e1_knee_ncu_replay.py --role up_proj --dose-mib "$dose"
done

run_profile natural NAT_L0_UP_D0 C16_E1_NAT_L0_UP_D0 "$TRAFFIC_METRICS" util/vm_tlb/c16/e1_natural_decode.py --run-index 100
run_profile natural NAT_L0_UP_D1 C16_E1_NAT_L0_UP_D1 "$TRAFFIC_METRICS" util/vm_tlb/c16/e1_natural_decode.py --run-index 101
run_profile natural NAT_L0_UP_D3 C16_E1_NAT_L0_UP_D3 "$TRAFFIC_METRICS" util/vm_tlb/c16/e1_natural_decode.py --run-index 103
run_profile natural NAT_L14_UP_D0 C16_E1_NAT_L14_UP_D0 "$TRAFFIC_METRICS" util/vm_tlb/c16/e1_natural_decode.py --run-index 140
run_profile natural NAT_L14_UP_D3 C16_E1_NAT_L14_UP_D3 "$TRAFFIC_METRICS" util/vm_tlb/c16/e1_natural_decode.py --run-index 143
run_profile natural NAT_L0_DOWN_D0 C16_E1_NAT_L0_DOWN_D0 "$TRAFFIC_METRICS" util/vm_tlb/c16/e1_natural_decode.py --run-index 200
run_profile natural NAT_L0_DOWN_D3 C16_E1_NAT_L0_DOWN_D3 "$TRAFFIC_METRICS" util/vm_tlb/c16/e1_natural_decode.py --run-index 203

printf 'PASS\n' > "$OUT/ncu/PROFILE_COMPLETE"
