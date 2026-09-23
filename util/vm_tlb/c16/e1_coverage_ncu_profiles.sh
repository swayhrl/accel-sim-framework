#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-coverage-scaling-109-v1
OUT=/data/c16/e1_coverage_scaling_v1/ncu/primary
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=$(python3 -c "import json; print(','.join(json.load(open('/data/c16/e1_coverage_scaling_v1/metric_query/METRIC_SELECTION.json'))['profile_metric_list']))")

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing coverage NCU" >&2
  exit 75
fi

mkdir -p "$OUT/reports" "$OUT/logs"
cd "$REPO"

run_profile() {
  local layer=$1
  local set_name=$2
  local prefix=$3
  local condition="${prefix}_${set_name}"
  local profile_id="L${layer}_UP_D3_${condition}"
  local range_name="C16_E1_COV_${condition}_L${layer}_UP_PROJ_D3"
  "$NCU" --nvtx --nvtx-include "${range_name}/" \
    --target-processes application-only --replay-mode application --cache-control none \
    --metrics "$METRICS" --force-overwrite -o "$OUT/reports/$profile_id" \
    "$PYTHON" util/vm_tlb/c16/e1_coverage_natural.py --condition "$condition" --run-index 500 \
    > "$OUT/logs/$profile_id.log" 2>&1
  "$NCU" --import "$OUT/reports/$profile_id.ncu-rep" --csv --page raw --print-units base > "$OUT/reports/$profile_id.base.csv"
  "$NCU" --import "$OUT/reports/$profile_id.ncu-rep" --csv --page session > "$OUT/reports/$profile_id.session.csv"
  echo "PASS coverage NCU $profile_id"
}

for set_name in N1 N8 N28; do
  run_profile 0 "$set_name" CONTROL
  run_profile 0 "$set_name" FAIR
done
for set_name in N2 N8 N28; do
  run_profile 14 "$set_name" CONTROL
  run_profile 14 "$set_name" FAIR
done
for set_name in N4 N28; do
  run_profile 27 "$set_name" CONTROL
  run_profile 27 "$set_name" FAIR
done

printf 'PASS\n' > "$OUT/COMPLETE"
