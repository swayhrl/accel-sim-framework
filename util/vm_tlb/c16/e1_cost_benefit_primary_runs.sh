#!/usr/bin/env bash
set -euo pipefail
REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-residency-cost-benefit-closure-109-v1
OUT=/data/c16/e1_residency_cost_benefit_closure_v1/primary/native
PYTHON=/data/c16/env/c16-awq-v6/bin/python
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -n 9 || exit 75
cd "$REPO"
for budget in B8 B16 B24 BFULL; do
 for prefix in CONTROL FAIR; do
  condition="${prefix}_${budget}";mkdir -p "$OUT/$condition"
  for i in 0 1 2 3 4 5 6; do "$PYTHON" util/vm_tlb/c16/e1_cost_benefit_natural.py --condition "$condition" --run-index "$i" --output "$OUT/$condition/run${i}.json" > "$OUT/$condition/run${i}.stdout.log" 2>&1; done
  echo "PASS cost-benefit $condition"
 done
done
printf 'PASS\n' > "$OUT/COMPLETE"
