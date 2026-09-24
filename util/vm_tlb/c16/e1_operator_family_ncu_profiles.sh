#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-operator-family-expansion-109-v1
OUT=/data/c16/e1_operator_family_expansion_v1/ncu/primary
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=$(python3 -c "import json; print(','.join(json.load(open('/data/c16/e1_operator_family_expansion_v1/metric_query/METRIC_SELECTION.json'))['profile_metric_list']))")

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing operator-family NCU" >&2
  exit 75
fi

mkdir -p "$OUT/reports" "$OUT/logs"
cd "$REPO"

run_profile() {
  local role=$1
  local condition=$2
  local profile_id="L0_${role^^}_D3_${condition}"
  local range_name="C16_E1_OPF_${condition}_L0_${role^^}_D3"
  "$NCU" --nvtx --nvtx-include "${range_name}/" \
    --target-processes application-only --replay-mode application --cache-control none \
    --metrics "$METRICS" --force-overwrite -o "$OUT/reports/$profile_id" \
    "$PYTHON" util/vm_tlb/c16/e1_operator_family_natural.py --condition "$condition" --run-index 600 \
    > "$OUT/logs/$profile_id.log" 2>&1
  "$NCU" --import "$OUT/reports/$profile_id.ncu-rep" --csv --page raw --print-units base > "$OUT/reports/$profile_id.base.csv"
  "$NCU" --import "$OUT/reports/$profile_id.ncu-rep" --csv --page session > "$OUT/reports/$profile_id.session.csv"
  echo "PASS operator-family NCU $profile_id"
}

for condition in CONTROL_GATE28 FAIR_GATE28 CONTROL_GUD84 FAIR_GUD84; do run_profile gate_proj "$condition"; done
for condition in CONTROL_UP28 FAIR_UP28 CONTROL_GUD84 FAIR_GUD84; do run_profile up_proj "$condition"; done
for condition in CONTROL_DOWN28 FAIR_DOWN28 CONTROL_GUD84 FAIR_GUD84; do run_profile down_proj "$condition"; done

printf 'PASS\n' > "$OUT/COMPLETE"
