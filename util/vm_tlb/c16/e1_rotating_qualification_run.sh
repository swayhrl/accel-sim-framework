#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-shared-residency-feasibility-109-v1
OUT=/data/c16/e1_shared_residency_feasibility_v1/rotating
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=$(python3 -c "import json; print(','.join(json.load(open('/data/c16/e1_shared_residency_feasibility_v1/metric_query/METRIC_SELECTION.json'))['profile_metric_list']))")

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing rotating qualification" >&2
  exit 75
fi

mkdir -p "$OUT/reports" "$OUT/logs"
cd "$REPO"
for condition in ROTATE_PERSIST_A_B_A ROTATE_NORMAL_CONTROL_A_B_A; do
  "$PYTHON" util/vm_tlb/c16/e1_rotating_window_qualification.py \
    --condition "$condition" --repetitions 9 --output "$OUT/${condition}_native.json" \
    > "$OUT/${condition}_native.stdout.log" 2>&1
  range_name="C16_E1_ROTATE_${condition}_A_RETURN"
  "$NCU" --nvtx --nvtx-include "${range_name}/" \
    --target-processes application-only --replay-mode application --cache-control none \
    --metrics "$METRICS" --force-overwrite -o "$OUT/reports/$condition" \
    "$PYTHON" util/vm_tlb/c16/e1_rotating_window_qualification.py --condition "$condition" --repetitions 1 \
    > "$OUT/logs/$condition.log" 2>&1
  "$NCU" --import "$OUT/reports/$condition.ncu-rep" --csv --page raw --print-units base > "$OUT/reports/$condition.base.csv"
  "$NCU" --import "$OUT/reports/$condition.ncu-rep" --csv --page session > "$OUT/reports/$condition.session.csv"
  echo "PASS rotating $condition"
done

printf 'PASS\n' > "$OUT/COMPLETE"
