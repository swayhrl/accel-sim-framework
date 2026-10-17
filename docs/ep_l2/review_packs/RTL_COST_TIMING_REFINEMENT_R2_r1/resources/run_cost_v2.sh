#!/usr/bin/env bash
set -euo pipefail
r=/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2
for mode in B16 S64 UNIFIED; do
 python3 rtl/ep_l2/flow/run_open.py --mapping fast-clean --mode "$mode" --liberty /workspace/ep_l2_rtl_cost_open_flow_v1/r1/Nangate45_typ.lib --out "$r/$mode-map-v2"
done
python3 rtl/ep_l2/flow/summarize.py --liberty /workspace/ep_l2_rtl_cost_open_flow_v1/r1/Nangate45_typ.lib --out "$r/FINAL_SUMMARY_v2" "$r/B16-map-v2" "$r/S64-map-v2" "$r/UNIFIED-map-v2"
python3 rtl/ep_l2/flow/compare_r1_r2.py --r2-summary "$r/FINAL_SUMMARY_v2/COST_SUMMARY.json" --out "$r/FINAL_COMPARISON_v2"
