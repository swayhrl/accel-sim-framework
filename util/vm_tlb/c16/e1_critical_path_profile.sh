#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-shared-residency-feasibility-109-v1
OUT=/data/c16/e1_shared_residency_feasibility_v1/critical
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=$(python3 -c "import json; print(','.join(json.load(open('/data/c16/e1_shared_residency_feasibility_v1/metric_query/METRIC_SELECTION.json'))['profile_metric_list']))")

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing critical-path profiling" >&2
  exit 75
fi

mkdir -p "$OUT/reports" "$OUT/logs"
cd "$REPO"

run_profile() {
  local profile_id=$1
  local condition=$2
  local target=$3
  local decode_index=$4
  local range_name="C16_E1_L2P_${condition}_${target}_D${decode_index}"
  "$NCU" --nvtx --nvtx-include "${range_name}/" \
    --target-processes application-only --replay-mode application --cache-control none \
    --metrics "$METRICS" --force-overwrite -o "$OUT/reports/$profile_id" \
    "$PYTHON" util/vm_tlb/c16/e1_l2_persistence_natural.py \
      --condition "$condition" --run-index 300 \
    > "$OUT/logs/$profile_id.log" 2>&1
  "$NCU" --import "$OUT/reports/$profile_id.ncu-rep" --csv --page raw --print-units base > "$OUT/reports/$profile_id.base.csv"
  "$NCU" --import "$OUT/reports/$profile_id.ncu-rep" --csv --page session > "$OUT/reports/$profile_id.session.csv"
  echo "PASS critical $profile_id"
}

for condition in BASELINE SETASIDE_ONLY PERSIST_L0_UP PERSIST_L14_UP; do
  run_profile "L0_UP_D3_${condition}" "$condition" L0_UP 3
done
for condition in SETASIDE_ONLY PERSIST_L14_UP PERSIST_L0_UP; do
  run_profile "L14_UP_D3_${condition}" "$condition" L14_UP 3
done
for condition in SETASIDE_ONLY PERSIST_L0_DOWN PERSIST_L0_UP; do
  run_profile "L0_DOWN_D3_${condition}" "$condition" L0_DOWN 3
done

printf 'PASS\n' > "$OUT/COMPLETE"
