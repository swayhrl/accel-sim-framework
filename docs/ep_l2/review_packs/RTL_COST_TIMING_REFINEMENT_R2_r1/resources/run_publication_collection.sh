#!/usr/bin/env bash
set -euo pipefail
python3 /workspace/ep_l2_rtl_cost_timing_r2/publish_r2_v3.py
python3 /workspace/ep_l2_rtl_cost_timing_r2/final_annotations_v3.py
python3 - <<'PY'
from pathlib import Path
import subprocess
r=Path('/workspace/worktrees/accel-sim-ep-l2-rtl-cost-r2-fanout-v3');p=Path('/workspace/ep_l2_potential20261017_lane5_results/EPL2_RTL_COST_TIMING_REFINEMENT_R2_lane2_v3/PUBLIC_REVIEW_PACK_R2/contracts_and_proofs/COORDINATION_R2_SCIENTIFIC_REVIEW_AND_BOUNDED_GOAL.md');p.write_bytes(subprocess.check_output(['git','show','f2a2fec3ee5e1bb42aa298c84d25bdd9bd70e13e:docs/ep_l2/chatgpt_handoff/paper_closure_2026_10_17_v1/RTL_R1_SCIENTIFIC_REVIEW_AND_R2_BOUNDED_GOAL.md'],cwd=r))
PY
python3 /workspace/ep_l2_rtl_cost_timing_r2/final_resource_snapshot.py
python3 /workspace/ep_l2_rtl_cost_timing_r2/finalize_repository_v3.py
