#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-coverage-scaling-109-v1
OUT=/data/c16/e1_coverage_scaling_v1/census/native
PYTHON=/data/c16/env/c16-awq-v6/bin/python

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing census" >&2
  exit 75
fi

mkdir -p "$OUT"
cd "$REPO"
for run_index in 0 1 2 3 4 5 6; do
  "$PYTHON" util/vm_tlb/c16/e1_coverage_natural.py \
    --condition CENSUS_FFN_NO_PERSIST --run-index "$run_index" \
    --output "$OUT/run${run_index}.json" \
    > "$OUT/run${run_index}.stdout.log" 2>&1
done
"$PYTHON" util/vm_tlb/c16/e1_coverage_freeze_census.py
printf 'PASS\n' > "$OUT/COMPLETE"
