#!/usr/bin/env bash
set -euo pipefail
r=/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3/qualification-vector
mkdir "$r"
python3 rtl/ep_l2/flow/prove_metadata_r2.py --induct-only --out "$r/word-induction"
python3 rtl/ep_l2/flow/run_lane3_bytes_r2.py --out "$r/lane3-bytes"
python3 rtl/ep_l2/flow/run_functional.py --full-top --sim-timeout 2400 --out "$r/functional"
python3 rtl/ep_l2/flow/run_functional.py --full-top --unified-last-physical --sim-timeout 2400 --out "$r/unified-last-physical"
