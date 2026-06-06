#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs .local_runs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
run_name="${ACCELSIM_A7B_RUN_NAME:-A7B_n_app_smoke_${ts}}"
max_apps="${ACCELSIM_A7B_MAX_APPS:-3}"
timeout_sec="${ACCELSIM_A7B_TIMEOUT_SEC:-600}"
app_filter="${ACCELSIM_A7B_APP_FILTER:-}"
dry_run="${ACCELSIM_A7B_DRY_RUN:-0}"
config_dir="${ACCELSIM_A7B_CONFIG_DIR:-SM7_QV100}"
trace_root="${ACCELSIM_TRACE_ROOT:-}"
run_root="$repo_root/.local_runs/$run_name"
report_path=".local_reports/A7B_n_app_smoke_${ts}.md"
stats_path=".local_reports/${run_name}_stats.csv"
log_path=".local_logs/A7B_n_app_smoke_${ts}.log"
selection_path=".local_reports/${run_name}_selection.csv"

status="PASS"
blocker="none"
selected_count="0"
passed_count="0"
failed_count="0"
timeout_count="0"

exec > >(tee "$log_path") 2>&1

echo "A7B N-app smoke"
echo "Start: $start_iso"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED_ENV"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

discover_trace_root() {
  if [ -n "$trace_root" ]; then
    [ -d "$trace_root" ] && { cd "$trace_root" && pwd; return 0; }
    return 1
  fi
  local from_report
  from_report="$(sed -n 's/^- Trace root: `\(.*\)`/\1/p' .local_reports/A7A*.md .local_reports/A6*.md 2>/dev/null | sed '/^$/d' | tail -1)"
  if [ -n "$from_report" ] && [ -d "$from_report" ]; then
    cd "$from_report" && pwd
    return 0
  fi
  local kernels
  kernels="$(find .local_traces hw_run . -type f -name kernelslist.g 2>/dev/null | sort | head -1)"
  if [ -n "$kernels" ]; then
    python3 - "$kernels" <<'PY'
import os, sys
p = os.path.abspath(sys.argv[1])
for _ in range(4):
    p = os.path.dirname(p)
print(p)
PY
    return 0
  fi
  return 1
}

if [ "$status" = "PASS" ]; then
  if trace_root="$(discover_trace_root)"; then
    :
  elif [ "$dry_run" = "1" ]; then
    status="DRY_RUN_BLOCKED_NO_TRACE"
    blocker="dry-run only: no trace root available for real execution"
  else
    status="BLOCKED_NO_TRACE"
    blocker="no trace root available; A7B does not download traces"
  fi
fi

base_config="$GPGPUSIM_ROOT/configs/tested-cfgs/$config_dir/gpgpusim.config"
trace_config="$ACCELSIM_ROOT/configs/tested-cfgs/$config_dir/trace.config"
sim_bin="$ACCELSIM_ROOT/bin/release/accel-sim.out"

if [ "$status" = "PASS" ] || [ "$status" = "DRY_RUN_BLOCKED_NO_TRACE" ]; then
  if [ "$status" = "PASS" ] && { [ ! -x "$sim_bin" ] || [ ! -f "$base_config" ] || [ ! -f "$trace_config" ]; }; then
    status="FAILED_CONFIG"
    blocker="missing simulator binary or config files"
  fi
fi

if [ "$status" = "PASS" ]; then
  python3 - "$trace_root" "$max_apps" "$app_filter" "$selection_path" <<'PY'
import csv, os, sys
from pathlib import Path

root = Path(sys.argv[1])
max_apps = int(sys.argv[2])
app_filter = sys.argv[3].lower()
out = Path(sys.argv[4])
preferred = ["backprop", "bfs", "gaussian", "hotspot", "lud", "nw", "srad", "streamcluster", "pathfinder"]
bad = ["scaled", "large", "full", "huge"]
rows = []
for k in sorted(root.rglob("kernelslist.g")):
    trace_dir = k.parent
    args_dir = trace_dir.parent
    app_dir = args_dir.parent
    app_name = app_dir.name
    joined = str(k).lower()
    if app_filter and app_filter not in joined:
        continue
    if any(token in joined for token in bad):
        continue
    pref = next((i for i, name in enumerate(preferred) if name in joined), len(preferred))
    rows.append((pref, app_name, str(k)))
rows.sort(key=lambda x: (x[0], x[1], x[2]))
with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["app_index", "app_name", "kernelslist"])
    for idx, (_, app_name, kernelslist) in enumerate(rows[:max_apps], 1):
        w.writerow([idx, app_name, kernelslist])
PY
fi

if [ "$dry_run" = "1" ]; then
  echo "Dry run: $dry_run"
  echo "Trace root: ${trace_root:-}"
  echo "Selection CSV: $selection_path"
  [ -f "$selection_path" ] && cat "$selection_path"
  if [ "$status" = "PASS" ]; then
    status="PASS_DRY_RUN"
  fi
fi

if [ "$status" = "PASS" ]; then
  mkdir -p "$run_root"
  echo "app_index,app_name,status,exit_code,timeout_sec,kernelslist,log_path,gpgpu_simulation_time,gpgpu_simulation_rate_inst_sec,gpgpu_simulation_rate_cycle_sec,gpgpu_n_tot_w_icount,exit_detected" > "$stats_path"
  while IFS=, read -r app_index app_name kernelslist; do
    [ "$app_index" = "app_index" ] && continue
    kernelslist="$(printf '%s' "$kernelslist" | tr -d '\r\n')"
    selected_count="$((selected_count + 1))"
    safe_app="$(printf '%s' "$app_name" | sed 's/[^A-Za-z0-9_.-]/_/g')"
    app_run_dir="$run_root/${app_index}_${safe_app}"
    app_log="$repo_root/.local_logs/${run_name}_${app_index}_${safe_app}.log"
    mkdir -p "$app_run_dir"
    cp "$GPGPUSIM_ROOT/configs/tested-cfgs/$config_dir"/*.{icnt,xml,csv} "$app_run_dir" 2>/dev/null || true
    {
      cat "$base_config"
      echo
      echo "#SASS"
      echo "#SASS-Driven Accel-Sim"
      echo
      cat "$trace_config"
    } > "$app_run_dir/gpgpusim.config"
    rm -f "$app_run_dir/traces"
    ln -s "$(dirname "$kernelslist")" "$app_run_dir/traces"
    echo "Running app $app_index $app_name"
    (
      cd "$app_run_dir" &&
        timeout "$timeout_sec" "$sim_bin" -config ./gpgpusim.config -trace ./traces/kernelslist.g > "$app_log" 2>&1
    )
    rc=$?
    app_status="PASS"
    if [ "$rc" -eq 124 ]; then
      app_status="TIMEOUT"
      timeout_count="$((timeout_count + 1))"
    elif [ "$rc" -ne 0 ]; then
      app_status="FAIL"
      failed_count="$((failed_count + 1))"
    elif grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$app_log"; then
      passed_count="$((passed_count + 1))"
    else
      app_status="FAIL_NO_EXIT_DETECTED"
      failed_count="$((failed_count + 1))"
    fi
    python3 - "$stats_path" "$app_index" "$app_name" "$app_status" "$rc" "$timeout_sec" "$kernelslist" "$app_log" <<'PY'
import csv, re, sys
stats_path, idx, app, status, rc, timeout, kernels, log_path = sys.argv[1:]
text = open(log_path, errors="replace").read() if log_path else ""
def first(pattern):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else "NA"
row = [
    idx, app, status, rc, timeout, kernels, log_path,
    first(r"gpgpu_simulation_time\s*=.*\(([^)]*)\)"),
    first(r"gpgpu_simulation_rate\s*=\s*([0-9.]+)\s*\(inst/sec\)"),
    first(r"gpgpu_simulation_rate\s*=\s*([0-9.]+)\s*\(cycle/sec\)"),
    first(r"gpgpu_n_tot_w_icount\s*=\s*(.*)"),
    str("GPGPU-Sim: *** exit detected ***" in text),
]
with open(stats_path, "a", newline="") as f:
    csv.writer(f).writerow(row)
PY
  done < "$selection_path"
  if [ "$selected_count" -eq 0 ]; then
    status="BLOCKED_NO_APPS"
    blocker="no kernelslist.g files selected"
  elif [ "$selected_count" -lt "$max_apps" ]; then
    status="PARTIAL_PASS_FEWER_APPS"
  elif [ "$failed_count" -gt 0 ] || [ "$timeout_count" -gt 0 ]; then
    status="PARTIAL_PASS_WITH_FAILURES"
  fi
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A7B N-App Smoke

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a7b_n_app_smoke.sh\`
- Log: \`$log_path\`
- Stats CSV: \`$stats_path\`
- Selection CSV: \`$selection_path\`
- Blocker: $blocker

## Settings

- Trace root: \`${trace_root:-}\`
- Run name: \`$run_name\`
- Max apps: \`$max_apps\`
- Timeout seconds: \`$timeout_sec\`
- App filter: \`$app_filter\`
- Dry run: \`$dry_run\`
- Config dir: \`$config_dir\`

## Results

- Selected: $selected_count
- Passed: $passed_count
- Failed: $failed_count
- Timed out: $timeout_count

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

echo "A7B report: $report_path"
echo "A7B stats: $stats_path"
echo "A7B status: $status"

case "$status" in
  PASS|PASS_DRY_RUN|PARTIAL_PASS_FEWER_APPS|PARTIAL_PASS_WITH_FAILURES|DRY_RUN_BLOCKED_NO_TRACE|BLOCKED_NO_TRACE) exit 0 ;;
  *) exit 1 ;;
esac
