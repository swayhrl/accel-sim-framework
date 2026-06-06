#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs .local_runs .local_traces

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
log_path=".local_logs/A2_pretrace_smoke_${ts}.log"
report_path=".local_reports/A2_pretrace_smoke_${ts}.md"
stats_path=".local_reports/A2_pretrace_smoke_${ts}_stats.csv"
download_root="$repo_root/.local_traces/pretraces"

bench="${ACCELSIM_BENCH:-rodinia_2.0-ft}"
config="${ACCELSIM_CONFIG:-QV100-SASS}"
run_name="${ACCELSIM_RUN_NAME:-A2_pretrace_smoke_${ts}}"
run_dir="$repo_root/.local_runs/$run_name"
timeout_hours="${ACCELSIM_MONITOR_TIMEOUT_HOURS:-0.25}"
trace_root="${ACCELSIM_TRACE_ROOT:-}"
cuda_version="${CUDA_VERSION:-$(basename "${CUDA_INSTALL_PATH:-/usr/local/cuda-11.8}" | sed 's/^cuda-//')}"
compat_run_link="$repo_root/sim_run_${cuda_version}"
launch_mode="${ACCELSIM_A2_LAUNCH_MODE:-direct}"
direct_timeout_seconds="${ACCELSIM_DIRECT_TIMEOUT_SECONDS:-300}"

status="PASS"
blocker="none"
trace_source="not_found"
run_status="not_run"
monitor_status="not_run"
stats_status="not_run"

exec > >(tee "$log_path") 2>&1

run_cmd() {
  echo
  echo "+ $*"
  "$@"
}

discover_kernels() {
  find . .local_traces hw_run -type f -name kernelslist.g 2>/dev/null | sort
}

choose_trace_root_from_kernels() {
  local kernels_file
  kernels_file="$(discover_kernels | head -1)"
  if [ -z "$kernels_file" ]; then
    return 1
  fi
  python3 - "$kernels_file" <<'PY'
import os, sys
p = os.path.abspath(sys.argv[1])
# kernelslist.g -> traces -> args -> benchmark -> trace root.
for _ in range(4):
    p = os.path.dirname(p)
print(p)
PY
}

extract_downloaded_traces() {
  local tgz
  find "$download_root" -maxdepth 1 -type f -name '*.tgz' -print | sort | while read -r tgz; do
    echo
    echo "+ tar -xzf $tgz -C $download_root"
    tar -xzf "$tgz" -C "$download_root"
  done
}

echo "A2 pre-trace minimal simulation"
echo "Start: $start_iso"
echo "Command: bash scripts/accelsim/a2_pretrace_smoke.sh"
echo "Benchmark: $bench"
echo "Config: $config"
echo "Run name: $run_name"
echo "Run dir: $run_dir"
echo "Launch mode: $launch_mode"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

if [ "$status" != "FAILED" ]; then
  mkdir -p "$run_dir"
  if [ -e "$compat_run_link" ] && [ ! -L "$compat_run_link" ]; then
    status="FAILED"
    blocker="$compat_run_link exists and is not a symlink; cannot create monitor compatibility link"
  else
    echo
    echo "+ ln -sfn .local_runs/$run_name sim_run_${cuda_version}"
    ln -sfn ".local_runs/$run_name" "$compat_run_link"
  fi
fi

if [ "$status" != "FAILED" ]; then
  echo
  echo "Discovered local kernelslist.g files before download:"
  discover_kernels || true

  if [ -n "$trace_root" ]; then
    trace_root="$(cd "$trace_root" && pwd)"
    trace_source="ACCELSIM_TRACE_ROOT"
  elif trace_root="$(choose_trace_root_from_kernels)"; then
    trace_source="existing_local"
  else
    echo
    echo "+ python3 ./get-accel-sim-traces.py --help"
    python3 ./get-accel-sim-traces.py --help || true
    mkdir -p "$download_root"
    echo
    echo "No local traces found. rodinia_2.0-ft is listed in the official trace summary as 7.20M compressed / 162M uncompressed."
    if run_cmd python3 ./get-accel-sim-traces.py -a tesla-v100/rodinia_2.0-ft -d "$download_root"; then
      trace_source="downloaded_tesla-v100_rodinia_2.0-ft"
      extract_downloaded_traces
      if trace_root="$(choose_trace_root_from_kernels)"; then
        :
      else
        status="BLOCKED_NEED_TRACE"
        blocker="download completed but no kernelslist.g was found after extraction"
      fi
    else
      status="BLOCKED_NEED_TRACE"
      blocker="official trace downloader failed for tesla-v100/rodinia_2.0-ft"
    fi
  fi
fi

if [ "$status" != "FAILED" ] && [ "$status" != "BLOCKED_NEED_TRACE" ]; then
  if [ -z "$trace_root" ] || [ ! -d "$trace_root" ]; then
    status="BLOCKED_NEED_TRACE"
    blocker="trace root is empty or missing: ${trace_root:-<empty>}"
  else
    echo
    echo "Resolved trace root: $trace_root"
    echo "Trace root source: $trace_source"
    echo "kernelslist.g under trace root:"
    find "$trace_root" -type f -name kernelslist.g | sort | sed -n '1,40p'

    run_args=(./util/job_launching/run_simulations.py -B "$bench" -C "$config" -T "$trace_root" -N "$run_name" -r "$run_dir" -l local -c 1)
    if [ "$launch_mode" = "direct" ]; then
      run_args+=(-n)
    fi
    if run_cmd "${run_args[@]}"; then
      run_status="PASS"
    else
      run_status="FAILED"
      status="FAILED"
      blocker="run_simulations.py failed"
    fi
  fi
fi

if [ "$status" = "PASS" ] && [ "$launch_mode" = "direct" ]; then
  first_run_dir="$(find "$run_dir" -mindepth 3 -maxdepth 3 -type d -name "$config" | sort | head -1)"
  if [ -z "$first_run_dir" ] || [ ! -f "$first_run_dir/justrun.sh" ]; then
    status="FAILED"
    blocker="direct mode could not find a generated justrun.sh under $run_dir"
  else
    echo
    echo "Direct smoke run dir: $first_run_dir"
    echo "+ timeout $direct_timeout_seconds bash justrun.sh > direct_smoke.o0 2> direct_smoke.e0"
    (
      cd "$first_run_dir" &&
        timeout "$direct_timeout_seconds" bash ./justrun.sh > direct_smoke.o0 2> direct_smoke.e0
    )
    direct_rc=$?
    if [ "$direct_rc" -eq 0 ]; then
      monitor_status="SKIPPED_DIRECT_MODE"
    else
      monitor_status="FAILED_DIRECT_RUN_RC_${direct_rc}"
      status="FAILED"
      blocker="direct justrun.sh failed or timed out with rc $direct_rc"
    fi
  fi
fi

if [ "$status" = "PASS" ] && [ "$launch_mode" != "direct" ]; then
  if run_cmd ./util/job_launching/monitor_func_test.py -v -N "$run_name" -S 10 -T "$timeout_hours" -K -s "$stats_path"; then
    monitor_status="PASS"
  else
    monitor_status="FAILED"
    status="FAILED"
    blocker="monitor_func_test.py reported failed or timed-out jobs"
  fi
fi

if [ "$status" = "PASS" ]; then
  echo
  if [ "$launch_mode" = "direct" ]; then
    echo "+ ./util/job_launching/get_stats.py -r $run_dir -B $bench -C $config -I > $stats_path"
    ./util/job_launching/get_stats.py -r "$run_dir" -B "$bench" -C "$config" -I > "$stats_path"
  else
    echo "+ ./util/job_launching/get_stats.py -N $run_name > $stats_path"
    ./util/job_launching/get_stats.py -N "$run_name" > "$stats_path"
  fi
  get_stats_rc=$?
  if [ "$get_stats_rc" -eq 0 ]; then
    if [ -s "$stats_path" ]; then
      stats_status="PASS"
    else
      stats_status="FAILED_EMPTY"
      status="FAILED"
      blocker="get_stats.py produced an empty stats CSV"
    fi
  else
    stats_status="FAILED"
    status="FAILED"
    blocker="get_stats.py failed with rc $get_stats_rc"
  fi
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A2 Pre-Trace Smoke

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a2_pretrace_smoke.sh\`
- Log: \`$log_path\`
- Stats CSV: \`$stats_path\`
- Blocker: $blocker
- Next action: proceed to A3 tracer flow; A3 may be blocked if no GPU is visible.

## Run Settings

- Benchmark: \`$bench\`
- Config: \`$config\`
- Run name: \`$run_name\`
- Run dir: \`$run_dir\`
- Monitor compatibility link: \`$compat_run_link\`
- Launch mode: \`$launch_mode\`
- Trace root: \`${trace_root:-}\`
- Trace source: $trace_source
- run_simulations.py: $run_status
- monitor_func_test.py: $monitor_status
- get_stats.py: $stats_status

## Trace Files

\`\`\`
$(if [ -n "${trace_root:-}" ] && [ -d "${trace_root:-/nonexistent}" ]; then find "$trace_root" -type f -name kernelslist.g | sort | sed -n '1,80p'; fi)
\`\`\`

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

echo
echo "A2 report: $report_path"
echo "A2 log: $log_path"
echo "A2 stats: $stats_path"
echo "A2 status: $status"

case "$status" in
  PASS|BLOCKED_NEED_TRACE) exit 0 ;;
  *) exit 1 ;;
esac
