#!/usr/bin/env bash
set -euo pipefail
r=/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_R3_METADATA_AND_COST_OPT_lane2
python3 rtl/ep_l2/flow/run_sta.py --mapped-run "$r/R3B_FINAL_COST/UNIFIED" --phase sta-resume-r2 --mode UNIFIED --liberty /workspace/ep_l2_rtl_cost_open_flow_v1/r1/Nangate45_typ.lib
python3 /workspace/ep_l2_rtl_r3_metadata_cost/archive_phase.py R3B_FINAL_COST/UNIFIED
