#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-coverage-scaling-109-v1
OUT=/data/c16/e1_coverage_scaling_v1/coverage/native
PYTHON=/data/c16/env/c16-awq-v6/bin/python

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing coverage runs" >&2
  exit 75
fi

cd "$REPO"
for set_name in N1 N2 N4 N8 N14A N28 N14B; do
  for prefix in CONTROL FAIR; do
    condition="${prefix}_${set_name}"
    mkdir -p "$OUT/$condition"
    for run_index in 0 1 2 3 4 5 6; do
      "$PYTHON" util/vm_tlb/c16/e1_coverage_natural.py \
        --condition "$condition" --run-index "$run_index" \
        --output "$OUT/$condition/run${run_index}.json" \
        > "$OUT/$condition/run${run_index}.stdout.log" 2>&1
    done
    echo "PASS coverage $condition"
  done
done

printf 'PASS\n' > "$OUT/PRIMARY_COMPLETE"
