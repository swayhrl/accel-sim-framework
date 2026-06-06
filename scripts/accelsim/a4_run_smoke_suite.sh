#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs .local_runs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
log_path=".local_logs/A4_smoke_suite_${ts}.log"
report_path=".local_reports/A4_smoke_suite_${ts}.md"
stats_path=".local_reports/A4_smoke_suite_${ts}_stats.csv"

bench_list="${ACCELSIM_BENCH_LIST:-rodinia_2.0-ft}"
config_list="${ACCELSIM_CONFIG_LIST:-QV100-SASS}"
trace_root="${ACCELSIM_TRACE_ROOT:-}"
run_name="${ACCELSIM_RUN_NAME:-A4_smoke_suite_${ts}}"
run_dir="$repo_root/.local_runs/$run_name"
max_jobs="${ACCELSIM_MAX_JOBS:-1}"
dry_run="${ACCELSIM_DRY_RUN:-0}"
launch_mode="${ACCELSIM_A4_LAUNCH_MODE:-direct}"
direct_timeout_seconds="${ACCELSIM_DIRECT_TIMEOUT_SECONDS:-300}"

status="PASS"
blocker="none"
run_status="not_run"
stats_status="not_run"

exec > >(tee "$log_path") 2>&1

run_cmd() {
  echo
  echo "+ $*"
  "$@"
}

discover_trace_root() {
  local kernels_file
  kernels_file="$(find .local_traces hw_run -type f -name kernelslist.g 2>/dev/null | sort | head -1)"
  if [ -z "$kernels_file" ]; then
    return 1
  fi
  python3 - "$kernels_file" <<'PY'
import os, sys
p = os.path.abspath(sys.argv[1])
for _ in range(4):
    p = os.path.dirname(p)
print(p)
PY
}

needs_trace() {
  case "$config_list" in
    *SASS*) return 0 ;;
    *) return 1 ;;
  esac
}

echo "A4 smoke suite"
echo "Start: $start_iso"
echo "Command: bash scripts/accelsim/a4_run_smoke_suite.sh"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

if [ "$status" = "PASS" ] && [ ! -x ./gpu-simulator/bin/release/accel-sim.out ]; then
  status="FAILED"
  blocker="gpu-simulator/bin/release/accel-sim.out is missing or not executable"
fi

if [ "$status" = "PASS" ] && needs_trace; then
  if [ -n "$trace_root" ]; then
    trace_root="$(cd "$trace_root" && pwd)"
  elif trace_root="$(discover_trace_root)"; then
    :
  elif [ "$dry_run" = "1" ]; then
    trace_root=""
  else
    status="BLOCKED_NEED_TRACE"
    blocker="SASS config requires ACCELSIM_TRACE_ROOT or discovered kernelslist.g"
  fi
fi

echo
echo "Resolved settings:"
echo "  ACCELSIM_BENCH_LIST=$bench_list"
echo "  ACCELSIM_CONFIG_LIST=$config_list"
echo "  ACCELSIM_TRACE_ROOT=${trace_root:-}"
echo "  ACCELSIM_RUN_NAME=$run_name"
echo "  ACCELSIM_MAX_JOBS=$max_jobs"
echo "  ACCELSIM_DRY_RUN=$dry_run"
echo "  ACCELSIM_A4_LAUNCH_MODE=$launch_mode"
echo "  run_dir=$run_dir"

run_args=(./util/job_launching/run_simulations.py -B "$bench_list" -C "$config_list" -N "$run_name" -r "$run_dir" -l local -c "$max_jobs")
if [ -n "${trace_root:-}" ]; then
  run_args+=(-T "$trace_root")
fi
if [ "$launch_mode" = "direct" ]; then
  run_args+=(-n)
fi

if [ "$status" = "PASS" ] && [ "$dry_run" = "1" ]; then
  echo
  echo "Dry-run command:"
  printf ' %q' "${run_args[@]}"
  echo
  run_status="DRY_RUN"
elif [ "$status" = "PASS" ]; then
  mkdir -p "$run_dir"
  if run_cmd "${run_args[@]}"; then
    run_status="PASS"
  else
    run_status="FAILED"
    status="FAILED"
    blocker="run_simulations.py failed"
  fi
fi

if [ "$status" = "PASS" ] && [ "$dry_run" != "1" ] && [ "$launch_mode" = "direct" ]; then
  mapfile -t direct_dirs < <(find "$run_dir" -mindepth 3 -maxdepth 3 -type d | sort | head -n "$max_jobs")
  if [ "${#direct_dirs[@]}" -eq 0 ]; then
    status="FAILED"
    blocker="direct mode found no generated run directories"
  else
    for direct_dir in "${direct_dirs[@]}"; do
      if [ -f "$direct_dir/justrun.sh" ]; then
        echo
        echo "Direct smoke run dir: $direct_dir"
        echo "+ timeout $direct_timeout_seconds bash justrun.sh > direct_smoke.o0 2> direct_smoke.e0"
        (
          cd "$direct_dir" &&
            timeout "$direct_timeout_seconds" bash ./justrun.sh > direct_smoke.o0 2> direct_smoke.e0
        )
        direct_rc=$?
        if [ "$direct_rc" -ne 0 ]; then
          status="FAILED"
          blocker="direct justrun.sh failed or timed out with rc $direct_rc in $direct_dir"
          break
        fi
      fi
    done
  fi
fi

if [ "$status" = "PASS" ] && [ "$dry_run" != "1" ]; then
  echo
  if [ "$launch_mode" = "direct" ]; then
    echo "+ ./util/job_launching/get_stats.py -r $run_dir -B $bench_list -C $config_list -I > $stats_path"
    ./util/job_launching/get_stats.py -r "$run_dir" -B "$bench_list" -C "$config_list" -I > "$stats_path"
  else
    echo "+ ./util/job_launching/monitor_func_test.py -v -N $run_name -S 10 -T 0.25 -K -s $stats_path"
    ./util/job_launching/monitor_func_test.py -v -N "$run_name" -S 10 -T 0.25 -K -s "$stats_path"
    echo "+ ./util/job_launching/get_stats.py -N $run_name > $stats_path"
    ./util/job_launching/get_stats.py -N "$run_name" > "$stats_path"
  fi
  stats_rc=$?
  if [ "$stats_rc" -eq 0 ] && [ -s "$stats_path" ]; then
    stats_status="PASS"
  else
    stats_status="FAILED"
    status="FAILED"
    blocker="stats collection failed or produced empty CSV"
  fi
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A4 Smoke Suite

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a4_run_smoke_suite.sh\`
- Log: \`$log_path\`
- Stats CSV: \`$stats_path\`
- Blocker: $blocker
- Next action: proceed to A5 result collection and documentation.

## Settings

- Bench list: \`$bench_list\`
- Config list: \`$config_list\`
- Trace root: \`${trace_root:-}\`
- Run name: \`$run_name\`
- Run dir: \`$run_dir\`
- Max jobs: \`$max_jobs\`
- Dry run: \`$dry_run\`
- Launch mode: \`$launch_mode\`
- run_simulations.py: $run_status
- stats collection: $stats_status

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

echo
echo "A4 report: $report_path"
echo "A4 log: $log_path"
echo "A4 stats: $stats_path"
echo "A4 status: $status"

case "$status" in
  PASS|BLOCKED_NEED_TRACE) exit 0 ;;
  *) exit 1 ;;
esac
