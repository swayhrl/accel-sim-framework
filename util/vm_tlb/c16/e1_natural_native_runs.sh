#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-natural-reuse-residency-109-v1
OUT=/data/c16/e1_natural_reuse_residency_v1/natural/native
PYTHON=/data/c16/env/c16-awq-v6/bin/python

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing concurrent natural decode" >&2
  exit 75
fi

cd "$REPO"
test -f "$OUT/run0.json"
for run_index in 1 2 3 4 5 6; do
  "$PYTHON" util/vm_tlb/c16/e1_natural_decode.py \
    --run-index "$run_index" \
    --output "$OUT/run${run_index}.json" \
    > "$OUT/run${run_index}.stdout.log" 2>&1
done

printf 'PASS\n' > "$OUT/NATIVE_COMPLETE"
