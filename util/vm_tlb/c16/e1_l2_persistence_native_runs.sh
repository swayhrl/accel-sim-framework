#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-l2-persistence-intervention-109-v1
OUT=/data/c16/e1_l2_persistence_intervention_v1
PYTHON=/data/c16/env/c16-awq-v6/bin/python

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing concurrent persistence intervention" >&2
  exit 75
fi

cd "$REPO"
"$PYTHON" util/vm_tlb/c16/e1_l2_persistence_isolated_native.py \
  > "$OUT/isolated_native.stdout.log" 2>&1

for condition in BASELINE SETASIDE_ONLY PERSIST_L0_UP PERSIST_L14_UP PERSIST_L0_DOWN; do
  mkdir -p "$OUT/natural/$condition"
  for run_index in 0 1 2 3 4 5 6; do
    "$PYTHON" util/vm_tlb/c16/e1_l2_persistence_natural.py \
      --condition "$condition" --run-index "$run_index" \
      --output "$OUT/natural/$condition/run${run_index}.json" \
      > "$OUT/natural/$condition/run${run_index}.stdout.log" 2>&1
  done
  echo "PASS native $condition"
done

printf 'PASS\n' > "$OUT/NATIVE_COMPLETE"
