#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs

ts="$(date +%Y%m%d_%H%M%S)"
log_path=".local_logs/A10_run_all_${ts}.log"
exec > >(tee "$log_path") 2>&1

echo "A10_REAL_WORKLOAD_ALIGNMENT run-all"
echo "Start: $(date -Iseconds)"

if [ -n "$(git status --short)" ]; then
  echo "ERROR: git status is not clean before A10 run"
  git status --short
  exit 1
fi

run_phase() {
  phase="$1"
  shift
  echo "== $phase =="
  "$@"
  rc=$?
  echo "$phase rc=$rc"
  return 0
}

run_phase A10A bash scripts/accelsim/a10a_discover_prior_workflows.sh
run_phase A10B python3 scripts/accelsim/a10b_extract_prior_inventory.py
run_phase A10C python3 scripts/accelsim/a10c_build_trace_mapping.py
run_phase A10D_DRY env ACCELSIM_A10D_DRY_RUN=1 bash scripts/accelsim/a10d_run_aligned_smoke.sh
run_phase A10D bash scripts/accelsim/a10d_run_aligned_smoke.sh
run_phase A10E bash scripts/accelsim/a10e_collect_alignment_pack.sh

echo "End: $(date -Iseconds)"
git status --short
