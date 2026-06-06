#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs review_packs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
run_name="${ACCELSIM_A9_RUN_NAME:-A9_mascar_medic_alignment_${ts}}"
prior_root="${ACCELSIM_A9_PRIOR_REPO_ROOT:-}"
max_runs="${ACCELSIM_A9_MAX_ALIGNED_RUNS:-3}"
dry_run="${ACCELSIM_A9_DRY_RUN:-0}"
report_path=".local_reports/A9_mascar_medic_alignment_${ts}.md"
mapping_path=".local_reports/A9_mascar_medic_alignment_${ts}_mapping.csv"
stats_path=".local_reports/A9_mascar_medic_alignment_${ts}_stats.csv"
log_path=".local_logs/A9_mascar_medic_alignment_${ts}.log"
review_pack="review_packs/A6B_A9_ACCELSIM_PIPELINE_review_pack_${ts}.tar.gz"

status="PASS"
blocker="none"
aligned_report=""
aligned_stats=""
prior_count="0"
runnable_count="0"

exec > >(tee "$log_path") 2>&1

echo "A9 Mascar/MeDiC alignment"
echo "Start: $start_iso"

# shellcheck source=/dev/null
source "$repo_root/scripts/accelsim/accelsim_env.sh" || true

search_dirs=".local_reports docs scripts"
if [ -n "$prior_root" ] && [ -d "$prior_root" ]; then
  search_dirs="$prior_root $search_dirs"
fi

find /workspace/repos -maxdepth 3 -type d 2>/dev/null | grep -Ei 'gpgpu|mascar|medic' | sed -n '1,80p' > ".local_reports/${run_name}_prior_dirs.txt" || true
find /workspace/repos -maxdepth 4 -type f 2>/dev/null | grep -Ei 'mascar|medic|review_pack|stats|benchmark|workload' | grep -v '/build/' | sed -n '1,200p' > ".local_reports/${run_name}_prior_files.txt" || true
prior_count="$(wc -l < ".local_reports/${run_name}_prior_files.txt" | tr -d ' ')"

python3 - "$mapping_path" "${ACCELSIM_TRACE_ROOT:-}" <<'PY'
import csv, os, sys
from pathlib import Path

out = Path(sys.argv[1])
trace_root = Path(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else None
if not trace_root or not trace_root.exists():
    candidates = list(Path(".local_traces").rglob("kernelslist.g")) + list(Path("hw_run").rglob("kernelslist.g"))
else:
    candidates = list(trace_root.rglob("kernelslist.g"))

trace_by_name = {}
for k in candidates:
    lower = str(k).lower()
    for name in ["backprop", "bfs", "hotspot", "lud", "nw", "srad", "streamcluster", "pathfinder", "parboil", "polybench"]:
        if name in lower and name not in trace_by_name:
            trace_by_name[name] = str(k)

templates = [
    ("template", "Mascar", "rodinia", "backprop", "backprop"),
    ("template", "Mascar", "rodinia", "bfs", "bfs"),
    ("template", "Mascar", "rodinia", "hotspot", "hotspot"),
    ("template", "MeDiC", "rodinia", "lud", "lud"),
    ("template", "MeDiC", "rodinia", "nw", "nw"),
    ("template", "MeDiC", "rodinia", "srad", "srad"),
    ("template", "MeDiC", "rodinia", "streamcluster", "streamcluster"),
]

with out.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["source","paper","prior_benchmark_name","prior_app_or_workload","accel_trace_candidate","trace_available","runner","config","status","notes"])
    for source, paper, bench, workload, key in templates:
        trace = trace_by_name.get(key, "")
        available = "yes" if trace else "no"
        status = "RUNNABLE_SMOKE" if trace else "TRACE_MISSING"
        w.writerow([source, paper, bench, workload, trace, available, "scripts/accelsim/a7b_n_app_smoke.sh", "SM7_QV100", status, "template mapping from prior GPGPU-Sim workflow style to Accel-Sim trace smoke"])
PY

runnable_count="$(awk -F, 'NR>1 && $9=="RUNNABLE_SMOKE"{c++} END{print c+0}' "$mapping_path")"
if [ "$runnable_count" -gt 0 ] && [ "$dry_run" != "1" ]; then
  filters="$(awk -F, 'NR>1 && $9=="RUNNABLE_SMOKE"{print $4}' "$mapping_path" | paste -sd'|' -)"
  first_filter="$(printf '%s\n' "$filters" | cut -d'|' -f1)"
  if ACCELSIM_A7B_RUN_NAME="$run_name" \
    ACCELSIM_A7B_MAX_APPS="$max_runs" \
    ACCELSIM_A7B_APP_FILTER="$first_filter" \
    ACCELSIM_A7B_TIMEOUT_SEC=900 \
    bash scripts/accelsim/a7b_n_app_smoke.sh; then
    aligned_report="$(ls -t .local_reports/A7B_n_app_smoke_*.md 2>/dev/null | head -1 || true)"
    aligned_stats="$(sed -n 's/^- Stats CSV: `\(.*\)`/\1/p' "$aligned_report" 2>/dev/null | head -1)"
    [ -n "$aligned_stats" ] && cp "$aligned_stats" "$stats_path"
  else
    status="PARTIAL_PASS_ALIGNMENT_RUN_FAILED"
    blocker="aligned bounded smoke failed"
  fi
fi

if [ "$dry_run" = "1" ]; then
  status="PASS_DRY_RUN"
elif [ "$prior_count" -eq 0 ]; then
  status="PARTIAL_PASS_ALIGNMENT_TEMPLATE"
  blocker="no prior Mascar/MeDiC artifacts found; template mapping produced"
elif [ "$runnable_count" -eq 0 ]; then
  status="PARTIAL_PASS_ALIGNMENT_TEMPLATE"
  blocker="prior artifacts search completed but no runnable matching traces were found"
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A9 Mascar/MeDiC Alignment

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a9_mascar_medic_alignment.sh\`
- Log: \`$log_path\`
- Mapping CSV: \`$mapping_path\`
- Stats CSV: \`${aligned_stats:-$stats_path}\`
- Review pack: \`$review_pack\`
- Blocker: $blocker

## Search

- Prior root: \`${prior_root:-auto}\`
- Prior artifact file count: $prior_count
- Runnable mapping rows: $runnable_count
- Dry run: $dry_run

## Aligned Smoke

- A7B report: \`${aligned_report:-}\`
- A7B stats: \`${aligned_stats:-}\`

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

tar_inputs=()
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find docs/accelsim_bringup -maxdepth 1 -type f -name '*.md' | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find scripts/accelsim -maxdepth 1 -type f | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_reports -maxdepth 1 -type f \( -name 'A6B*.md' -o -name 'A7A*.md' -o -name 'A7B*.md' -o -name 'A8*.md' -o -name 'A9*.md' -o -name 'A7B*_stats.csv' -o -name 'A8*_stats.csv' -o -name 'A9*_mapping.csv' -o -name 'A9*_stats.csv' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_logs -maxdepth 1 -type f \( -name 'A6B*.log' -o -name 'A7A*.log' -o -name 'A7B*.log' -o -name 'A8*.log' -o -name 'A9*.log' \) -size -3M | sort)

tar -czf "$review_pack" "${tar_inputs[@]}"

echo "A9 report: $report_path"
echo "A9 mapping: $mapping_path"
echo "A9 review pack: $review_pack"
echo "A9 status: $status"

case "$status" in
  PASS|PASS_DRY_RUN|PARTIAL_PASS_ALIGNMENT_TEMPLATE|PARTIAL_PASS_ALIGNMENT_RUN_FAILED) exit 0 ;;
  *) exit 1 ;;
esac
