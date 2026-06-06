#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs .local_runs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
run_name="${ACCELSIM_A10D_RUN_NAME:-A10D_aligned_smoke_${ts}}"
max_runs="${ACCELSIM_A10D_MAX_RUNS:-3}"
timeout_sec="${ACCELSIM_A10D_TIMEOUT_SEC:-900}"
dry_run="${ACCELSIM_A10D_DRY_RUN:-0}"
require_high="${ACCELSIM_A10D_REQUIRE_HIGH_EVIDENCE:-1}"
mapping_path="${ACCELSIM_A10C_MAPPING:-}"
report_path=".local_reports/A10D_aligned_smoke_${ts}.md"
stats_path=".local_reports/A10D_aligned_smoke_${ts}.csv"
selection_path=".local_reports/A10D_aligned_smoke_${ts}_selection.csv"
log_path=".local_logs/A10D_aligned_smoke_${ts}.log"
run_root="$repo_root/.local_runs/$run_name"

status="PASS"
blocker="none"
selected_count=0
passed_count=0
failed_count=0
timeout_count=0

exec > >(tee "$log_path") 2>&1

echo "A10D aligned smoke"
echo "Start: $start_iso"

if [ -z "$mapping_path" ]; then
  mapping_path="$(ls -t .local_reports/A10C_trace_mapping_*.csv 2>/dev/null | head -1 || true)"
fi

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED_ENV"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

config_dir="SM7_QV100"
base_config="${GPGPUSIM_ROOT:-$repo_root/gpu-simulator/gpgpu-sim}/configs/tested-cfgs/$config_dir/gpgpusim.config"
trace_config="${ACCELSIM_ROOT:-$repo_root/gpu-simulator}/configs/tested-cfgs/$config_dir/trace.config"
sim_bin="${ACCELSIM_ROOT:-$repo_root/gpu-simulator}/bin/release/accel-sim.out"

if [ "$status" = "PASS" ]; then
  if [ -z "$mapping_path" ] || [ ! -f "$mapping_path" ]; then
    status="BLOCKED_NO_MAPPING"
    blocker="missing A10C mapping CSV"
  elif [ ! -x "$sim_bin" ] || [ ! -f "$base_config" ] || [ ! -f "$trace_config" ]; then
    status="FAILED_CONFIG"
    blocker="missing simulator binary or SM7_QV100 config"
  fi
fi

if [ "$status" = "PASS" ]; then
  python3 - "$mapping_path" "$selection_path" "$max_runs" "$require_high" <<'PY'
import csv
import sys
from collections import defaultdict

mapping_path, selection_path, max_runs, require_high = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
with open(mapping_path, newline="") as f:
    rows = list(csv.DictReader(f))
eligible = []
seen = set()
for r in rows:
    r = {k: (v or "").replace("\r", "").replace("\n", "").strip() for k, v in r.items()}
    if r.get("runnable") != "yes" or r.get("mapping_status") != "TRACE_AVAILABLE":
        continue
    if r.get("match_type") not in {"exact", "alias", "suite_alias"}:
        continue
    if require_high == "1" and r.get("evidence_strength") != "high":
        continue
    key = (r.get("paper"), r.get("prior_normalized_name"), r.get("kernelslist_path"))
    if key in seen:
        continue
    seen.add(key)
    eligible.append(r)
by_paper = defaultdict(list)
for r in eligible:
    by_paper[r.get("paper")].append(r)
selected = []
for paper in ["Mascar", "MeDiC", "both", "unknown"]:
    if by_paper.get(paper) and len(selected) < max_runs:
        selected.append(by_paper[paper].pop(0))
for r in eligible:
    if len(selected) >= max_runs:
        break
    if r not in selected:
        selected.append(r)
fields = ["run_id","paper","prior_workload_id","prior_name","normalized_name","kernelslist_path","config","mapping_id","evidence_strength"]
with open(selection_path, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields)
    w.writeheader()
    for i, r in enumerate(selected[:max_runs], 1):
        w.writerow({
            "run_id": i,
            "paper": r.get("paper"),
            "prior_workload_id": r.get("prior_workload_id"),
            "prior_name": r.get("prior_original_name"),
            "normalized_name": r.get("prior_normalized_name"),
            "kernelslist_path": r.get("kernelslist_path"),
            "config": r.get("config") or "SM7_QV100",
            "mapping_id": r.get("mapping_id"),
            "evidence_strength": r.get("evidence_strength"),
        })
PY
fi

echo "run_id,paper,prior_workload_id,prior_name,normalized_name,kernelslist_path,status,exit_code,timed_out,log_path,gpgpu_simulation_time,gpgpu_simulation_rate_inst_sec,gpgpu_simulation_rate_cycle_sec,gpgpu_n_tot_w_icount,gpu_tot_sim_cycle,gpu_tot_ipc,l2_total_cache_accesses,l2_total_cache_misses,exit_detected,notes" > "$stats_path"

if [ "$dry_run" = "1" ]; then
  echo "Dry run: $dry_run"
  echo "Mapping CSV: $mapping_path"
  echo "Selection CSV: $selection_path"
  [ -f "$selection_path" ] && sed -n '1,40p' "$selection_path"
  [ "$status" = "PASS" ] && status="PASS_DRY_RUN"
fi

if [ "$status" = "PASS" ]; then
  mkdir -p "$run_root"
  while IFS=, read -r run_id paper prior_workload_id prior_name normalized_name kernelslist_path config mapping_id evidence_strength; do
    [ "$run_id" = "run_id" ] && continue
    kernelslist_path="$(printf '%s' "$kernelslist_path" | tr -d '\r\n')"
    selected_count=$((selected_count + 1))
    safe_name="$(printf '%s' "$normalized_name" | sed 's/[^A-Za-z0-9_.-]/_/g')"
    app_run_dir="$run_root/${run_id}_${safe_name}"
    app_log="$repo_root/.local_logs/${run_name}_${run_id}_${safe_name}.log"
    mkdir -p "$app_run_dir"
    cp "$GPGPUSIM_ROOT/configs/tested-cfgs/$config_dir"/*.{icnt,xml,csv} "$app_run_dir" 2>/dev/null || true
    {
      sed 's/\r$//' "$base_config"
      echo
      echo "#SASS"
      echo "#SASS-Driven Accel-Sim"
      echo
      sed 's/\r$//' "$trace_config"
    } > "$app_run_dir/gpgpusim.config"
    rm -f "$app_run_dir/traces"
    ln -s "$(dirname "$kernelslist_path")" "$app_run_dir/traces"
    echo "Running A10D $run_id $paper $normalized_name"
    (
      cd "$app_run_dir" &&
        timeout "$timeout_sec" "$sim_bin" -config ./gpgpusim.config -trace ./traces/kernelslist.g > "$app_log" 2>&1
    )
    rc=$?
    row_status="PASS"
    timed_out="no"
    if [ "$rc" -eq 124 ]; then
      row_status="TIMEOUT"
      timed_out="yes"
      timeout_count=$((timeout_count + 1))
    elif [ "$rc" -ne 0 ]; then
      row_status="FAIL"
      failed_count=$((failed_count + 1))
    elif grep -q 'GPGPU-Sim: \*\*\* exit detected \*\*\*' "$app_log"; then
      passed_count=$((passed_count + 1))
    else
      row_status="FAIL_NO_EXIT_DETECTED"
      failed_count=$((failed_count + 1))
    fi
    python3 - "$stats_path" "$run_id" "$paper" "$prior_workload_id" "$prior_name" "$normalized_name" "$kernelslist_path" "$row_status" "$rc" "$timed_out" "$app_log" <<'PY'
import csv
import re
import sys

stats_path, run_id, paper, wid, prior, norm, kernels, status, rc, timed_out, log_path = sys.argv[1:]
text = open(log_path, errors="replace").read() if log_path else ""
def first(pattern):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else "NA"
row = [
    run_id, paper, wid, prior, norm, kernels, status, rc, timed_out, log_path,
    first(r"gpgpu_simulation_time\s*=.*\(([^)]*)\)"),
    first(r"gpgpu_simulation_rate\s*=\s*([0-9.]+)\s*\(inst/sec\)"),
    first(r"gpgpu_simulation_rate\s*=\s*([0-9.]+)\s*\(cycle/sec\)"),
    first(r"gpgpu_n_tot_w_icount\s*=\s*(.*)"),
    first(r"gpu_tot_sim_cycle\s*=\s*(.*)"),
    first(r"gpu_tot_ipc\s*=\s*(.*)"),
    first(r"l2_total_cache_accesses\s*=\s*(.*)"),
    first(r"l2_total_cache_misses\s*=\s*(.*)"),
    str("GPGPU-Sim: *** exit detected ***" in text),
    "bounded aligned smoke, not paper reproduction",
]
with open(stats_path, "a", newline="") as f:
    csv.writer(f).writerow(row)
PY
  done < "$selection_path"
  if [ "$selected_count" -eq 0 ]; then
    status="BLOCKED_NO_RUNNABLE_ALIGNED_WORKLOADS"
    blocker="A10C mapping has no qualifying runnable high-evidence rows"
  elif [ "$failed_count" -gt 0 ] || [ "$timeout_count" -gt 0 ]; then
    status="PARTIAL_PASS_WITH_FAILURES"
  fi
fi

if [ -f 0 ] && [ "$(wc -c < 0)" -le 16 ] && git status --short -- 0 | grep -q '^?? 0$'; then
  rm -f 0
  blocker="$blocker; removed transient untracked file 0"
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A10D Aligned Smoke

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a10d_run_aligned_smoke.sh\`
- Log: \`$log_path\`
- Mapping CSV: \`$mapping_path\`
- Selection CSV: \`$selection_path\`
- Stats CSV: \`$stats_path\`
- Blocker: $blocker

## Settings

- Max runs: $max_runs
- Timeout seconds: $timeout_sec
- Dry run: $dry_run
- Require high evidence: $require_high
- Config: SM7_QV100

## Results

- Selected: $selected_count
- Passed: $passed_count
- Failed: $failed_count
- Timed out: $timeout_count

## Limitations

This is a bounded trace-driven smoke for prior/Accel-Sim workload intersection, not a Mascar or MeDiC paper reproduction.

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

echo "A10D report: $report_path"
echo "A10D stats: $stats_path"
echo "A10D status: $status"

case "$status" in
  PASS|PASS_DRY_RUN|PARTIAL_PASS_WITH_FAILURES|BLOCKED_NO_RUNNABLE_ALIGNED_WORKLOADS) exit 0 ;;
  *) exit 1 ;;
esac
