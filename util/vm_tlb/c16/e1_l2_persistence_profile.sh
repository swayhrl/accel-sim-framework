#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-l2-persistence-intervention-109-v1
OUT=/data/c16/e1_l2_persistence_intervention_v1
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing concurrent persistence profiling" >&2
  exit 75
fi

mkdir -p "$OUT/ncu/isolated/reports" "$OUT/ncu/isolated/logs" \
         "$OUT/ncu/natural/reports" "$OUT/ncu/natural/logs"
cd "$REPO"

run_profile() {
  local family=$1
  local profile_id=$2
  local range_name=$3
  shift 3
  "$NCU" --nvtx --nvtx-include "${range_name}/" \
    --target-processes application-only --replay-mode application --cache-control none \
    --metrics "$METRICS" --force-overwrite \
    -o "$OUT/ncu/$family/reports/$profile_id" \
    "$PYTHON" "$@" > "$OUT/ncu/$family/logs/$profile_id.log" 2>&1
  echo "PASS $family/$profile_id"
}

for condition in ISO_BASELINE_DENSE ISO_QWEIGHT_PERSIST_DENSE; do
  run_profile isolated "$condition" "C16_E1_L2P_${condition}" \
    util/vm_tlb/c16/e1_l2_persistence_isolated_replay.py --condition "$condition"
done

for decode_index in 1 3; do
  for condition in BASELINE SETASIDE_ONLY PERSIST_L0_UP PERSIST_L14_UP; do
    run_profile natural "L0_UP_D${decode_index}_${condition}" "C16_E1_L2P_${condition}_L0_UP_D${decode_index}" \
      util/vm_tlb/c16/e1_l2_persistence_natural.py --condition "$condition" --run-index 100
  done
done

for condition in BASELINE SETASIDE_ONLY PERSIST_L14_UP PERSIST_L0_UP; do
  run_profile natural "L14_UP_D3_${condition}" "C16_E1_L2P_${condition}_L14_UP_D3" \
    util/vm_tlb/c16/e1_l2_persistence_natural.py --condition "$condition" --run-index 140
done

for condition in BASELINE SETASIDE_ONLY PERSIST_L0_DOWN PERSIST_L0_UP; do
  run_profile natural "L0_DOWN_D3_${condition}" "C16_E1_L2P_${condition}_L0_DOWN_D3" \
    util/vm_tlb/c16/e1_l2_persistence_natural.py --condition "$condition" --run-index 200
done

printf 'PASS\n' > "$OUT/ncu/PRIMARY_PROFILE_COMPLETE"
