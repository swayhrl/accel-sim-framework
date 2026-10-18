#!/usr/bin/env bash
set -euo pipefail
r=/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_R3_METADATA_AND_COST_OPT_lane2/R3B_FINAL_QUAL_RESUME_r2
# Already PASSED owner-stress and concurrency use their original exact receipts.
# Base had NO completed case; new output revision preserves incomplete VVP.
python3 rtl/ep_l2/flow/run_functional.py --full-top --sim-timeout 2400 --out "$r/functional"
python3 rtl/ep_l2/flow/run_lane3_bytes_r2.py --out "$r/lane3-bytes"
python3 rtl/ep_l2/flow/run_functional.py --full-top --unified-last-physical --sim-timeout 2400 --out "$r/unified-last-physical"
