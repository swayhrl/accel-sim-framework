#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-operator-family-expansion-109-v1
OUT=/data/c16/e1_operator_family_expansion_v1/primary/native
PYTHON=/data/c16/env/c16-awq-v6/bin/python

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing operator-family runs" >&2
  exit 75
fi

cd "$REPO"
for set_name in GATE28 UP28 DOWN28 GU56 GD56 UD56 GUD84; do
  for prefix in CONTROL FAIR; do
    condition="${prefix}_${set_name}"
    mkdir -p "$OUT/$condition"
    for run_index in 0 1 2 3 4 5 6; do
      "$PYTHON" util/vm_tlb/c16/e1_operator_family_natural.py \
        --condition "$condition" --run-index "$run_index" \
        --output "$OUT/$condition/run${run_index}.json" \
        > "$OUT/$condition/run${run_index}.stdout.log" 2>&1
    done
    echo "PASS operator-family $condition"
  done
done

printf 'PASS\n' > "$OUT/PRIMARY_COMPLETE"
