#!/usr/bin/env bash
set -euo pipefail
REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-residency-cost-benefit-closure-109-v1
OUT=/data/c16/e1_residency_cost_benefit_closure_v1/ncu/primary
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=$(python3 -c "import json; print(','.join(json.load(open('/data/c16/e1_residency_cost_benefit_closure_v1/metric_query/METRIC_SELECTION.json'))['profile_metric_list']))")
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -n 9 || exit 75
mkdir -p "$OUT/reports" "$OUT/logs";cd "$REPO"
run_profile(){ local budget=$1;local prefix=$2;local category=$3;local condition="${prefix}_${budget}";local profile="L0_${category^^}_D3_${condition}";local range="C16_E1_COST_${condition}_L0_${category^^}_D3"; "$NCU" --nvtx --nvtx-include "${range}/" --target-processes application-only --replay-mode application --cache-control none --metrics "$METRICS" --force-overwrite -o "$OUT/reports/$profile" "$PYTHON" util/vm_tlb/c16/e1_cost_benefit_natural.py --condition "$condition" --run-index 700 > "$OUT/logs/$profile.log" 2>&1; "$NCU" --import "$OUT/reports/$profile.ncu-rep" --csv --page raw --print-units base > "$OUT/reports/$profile.base.csv"; "$NCU" --import "$OUT/reports/$profile.ncu-rep" --csv --page session > "$OUT/reports/$profile.session.csv"; echo "PASS NCU $profile"; }
for budget in B16 BFULL; do for prefix in CONTROL FAIR; do run_profile "$budget" "$prefix" up_proj; run_profile "$budget" "$prefix" self_attn; done; done
printf 'PASS\n' > "$OUT/COMPLETE"
