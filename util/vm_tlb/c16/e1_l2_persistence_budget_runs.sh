#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-l2-persistence-intervention-109-v1
OUT=/data/c16/e1_l2_persistence_intervention_v1
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum
FULL_BYTES=33947648

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing concurrent budget sensitivity" >&2
  exit 75
fi

cd "$REPO"
mkdir -p "$OUT/budget" "$OUT/ncu/budget/reports" "$OUT/ncu/budget/logs"

run_budget() {
  local label=$1
  local bytes=$2
  mkdir -p "$OUT/budget/$label"
  for run_index in 0 1 2 3 4 5 6; do
    "$PYTHON" util/vm_tlb/c16/e1_l2_persistence_natural.py \
      --condition BUDGET_L0_UP --budget-bytes "$bytes" --run-index "$run_index" \
      --output "$OUT/budget/$label/run${run_index}.json" \
      > "$OUT/budget/$label/run${run_index}.stdout.log" 2>&1
  done
  "$NCU" --nvtx --nvtx-include "C16_E1_L2P_BUDGET_L0_UP_L0_UP_D3/" \
    --target-processes application-only --replay-mode application --cache-control none \
    --metrics "$METRICS" --force-overwrite -o "$OUT/ncu/budget/reports/${label}" \
    "$PYTHON" util/vm_tlb/c16/e1_l2_persistence_natural.py \
      --condition BUDGET_L0_UP --budget-bytes "$bytes" --run-index 100 \
    > "$OUT/ncu/budget/logs/${label}.log" 2>&1
  "$NCU" --import "$OUT/ncu/budget/reports/${label}.ncu-rep" --csv --page raw --print-units base > "$OUT/ncu/budget/reports/${label}.base.csv"
  "$NCU" --import "$OUT/ncu/budget/reports/${label}.ncu-rep" --csv --page session > "$OUT/ncu/budget/reports/${label}.session.csv"
  echo "PASS budget $label"
}

run_budget 8MIB $((8 * 1024 * 1024))
run_budget 16MIB $((16 * 1024 * 1024))
run_budget 24MIB $((24 * 1024 * 1024))
run_budget 32MIB $((32 * 1024 * 1024))
run_budget FULL "$FULL_BYTES"

printf 'PASS\n' > "$OUT/BUDGET_COMPLETE"
