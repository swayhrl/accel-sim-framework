#!/usr/bin/env bash
set -euo pipefail
mode=$1
r=/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_R3_METADATA_AND_COST_OPT_lane2
python3 rtl/ep_l2/flow/run_open.py --compact-artifacts --mapping fast-clean --mode "$mode" --liberty /workspace/ep_l2_rtl_cost_open_flow_v1/r1/Nangate45_typ.lib --out "$r/R3B_FINAL_COST/$mode"
python3 /workspace/ep_l2_rtl_r3_metadata_cost/archive_phase.py "R3B_FINAL_COST/$mode"
