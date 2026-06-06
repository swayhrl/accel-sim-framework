#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_logs
ts="$(date +%Y%m%d_%H%M%S)"
log_path=".local_logs/A11_A15_run_all_${ts}.log"
exec > >(tee "$log_path") 2>&1

echo "A11_A15_PAPER_REPRODUCTION_PIPELINE"
echo "Start: $(date -Iseconds)"

if [ -n "$(git status --short)" ]; then
  echo "ERROR: git status is not clean before A11-A15 run"
  git status --short
  exit 1
fi

python3 scripts/accelsim/a11_stats_equivalence_narrow.py
python3 scripts/accelsim/a12_workload_config_lockdown.py
ACCELSIM_A13_DRY_RUN=1 python3 scripts/accelsim/a13_experiment_matrix_runner.py
python3 scripts/accelsim/a13_experiment_matrix_runner.py
bash scripts/accelsim/a14_reproduction_readiness_closeout.sh
bash scripts/accelsim/a15_trace_gpu_gap_plan.sh

echo "End: $(date -Iseconds)"
git status --short
