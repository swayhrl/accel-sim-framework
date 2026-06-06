#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs review_packs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
summary_path=".local_reports/A10E_final_alignment_summary_${ts}.md"
log_path=".local_logs/A10E_final_alignment_summary_${ts}.log"
review_pack="review_packs/A10_REAL_WORKLOAD_ALIGNMENT_review_pack_${ts}.tar.gz"

exec > >(tee "$log_path") 2>&1

echo "A10E closeout"
echo "Start: $start_iso"

a10a_report="$(ls -t .local_reports/A10A_prior_artifact_discovery_*.md 2>/dev/null | head -1 || true)"
a10a_inventory="$(ls -t .local_reports/A10A_prior_artifact_inventory_*.csv 2>/dev/null | head -1 || true)"
a10b_report="$(ls -t .local_reports/A10B_prior_inventory_summary_*.md 2>/dev/null | head -1 || true)"
a10b_workloads="$(ls -t .local_reports/A10B_prior_workload_inventory_*.csv 2>/dev/null | head -1 || true)"
a10b_stats="$(ls -t .local_reports/A10B_prior_stats_field_inventory_*.csv 2>/dev/null | head -1 || true)"
a10c_summary="$(ls -t .local_reports/A10C_mapping_summary_*.md 2>/dev/null | head -1 || true)"
a10c_mapping="$(ls -t .local_reports/A10C_trace_mapping_*.csv 2>/dev/null | head -1 || true)"
a10d_report="$(ls -t .local_reports/A10D_aligned_smoke_*.md 2>/dev/null | head -1 || true)"
a10d_stats="$(ls -t .local_reports/A10D_aligned_smoke_*.csv 2>/dev/null | grep -v '_selection.csv' | head -1 || true)"

status_a10a="$(sed -n 's/^- Status: //p' "$a10a_report" 2>/dev/null | head -1)"
status_a10b="$(sed -n 's/^- Status: //p' "$a10b_report" 2>/dev/null | head -1)"
status_a10c="$(sed -n 's/^- Status: //p' "$a10c_summary" 2>/dev/null | head -1)"
status_a10d="$(sed -n 's/^- Status: //p' "$a10d_report" 2>/dev/null | head -1)"

artifact_count="$(awk 'END{print NR>0 ? NR-1 : 0}' "$a10a_inventory" 2>/dev/null || echo 0)"
workload_count="$(awk 'END{print NR>0 ? NR-1 : 0}' "$a10b_workloads" 2>/dev/null || echo 0)"
high_workload_count="$(awk -F, 'NR>1 && $12=="high"{c++} END{print c+0}' "$a10b_workloads" 2>/dev/null || echo 0)"
mapped_count="$(awk -F, 'NR>1 && $14=="TRACE_AVAILABLE"{c++} END{print c+0}' "$a10c_mapping" 2>/dev/null || echo 0)"
run_count="$(awk 'END{print NR>0 ? NR-1 : 0}' "$a10d_stats" 2>/dev/null || echo 0)"

status="PASS"
if [ "${status_a10a:-}" = "BLOCKED_NO_PRIOR_ARTIFACTS" ] || [ "$artifact_count" -eq 0 ]; then
  status="BLOCKED_NO_PRIOR_ARTIFACTS"
elif [ "$run_count" -eq 0 ]; then
  status="PARTIAL_PASS_NO_ALIGNED_RUNS"
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$summary_path" <<EOF
# A10E Final Alignment Summary

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a10e_collect_alignment_pack.sh\`
- Log: \`$log_path\`
- Review pack: \`$review_pack\`
- Baseline commit: \`$(git rev-parse HEAD)\`

## Phase Outputs

- A10A status: \`${status_a10a:-missing}\`
- A10A inventory: \`${a10a_inventory:-}\`
- A10B status: \`${status_a10b:-missing}\`
- A10B workload inventory: \`${a10b_workloads:-}\`
- A10B stats field inventory: \`${a10b_stats:-}\`
- A10C status: \`${status_a10c:-missing}\`
- A10C mapping: \`${a10c_mapping:-}\`
- A10D status: \`${status_a10d:-missing}\`
- A10D smoke stats: \`${a10d_stats:-}\`

## Counts

- Prior artifact rows: $artifact_count
- Prior workload rows: $workload_count
- High evidence workload rows: $high_workload_count
- Trace-available mapping rows: $mapped_count
- Aligned smoke rows: $run_count

## Gaps

- Workload equivalence is based on normalized benchmark names and source evidence, not paper-level metric equivalence.
- Prior stats fields are inventoried best-effort from discovered scripts, logs, docs, and CSV files.
- A10 does not validate NVBit tracer and does not run a full campaign.

## Recommended Next Round

Create an A11 stats-equivalence plan that selects one Mascar workload and one MeDiC workload, pins prior config files, and compares only matching GPGPU-Sim/Accel-Sim stat fields.

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

tar_inputs=()
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find docs/accelsim_bringup -maxdepth 1 -type f \( -name 'A10*.md' -o -name 'RUNBOOK.md' -o -name 'KNOWN_ISSUES.md' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find scripts/accelsim -maxdepth 1 -type f \( -name 'a10*.sh' -o -name 'a10*.py' -o -name 'README.md' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_reports -maxdepth 1 -type f \( -name 'A10A*.md' -o -name 'A10A*.csv' -o -name 'A10B*.md' -o -name 'A10B*.csv' -o -name 'A10C*.md' -o -name 'A10C*.csv' -o -name 'A10D*.md' -o -name 'A10D*.csv' -o -name 'A10E*.md' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_logs -maxdepth 1 -type f -name 'A10*.log' -size -3M | sort)

tar -czf "$review_pack" "${tar_inputs[@]}"

echo "A10E summary: $summary_path"
echo "A10E review pack: $review_pack"
echo "A10E status: $status"

case "$status" in
  PASS|PARTIAL_PASS_NO_ALIGNED_RUNS|PARTIAL_PASS_NO_PRIOR_ARTIFACTS|BLOCKED_NO_PRIOR_ARTIFACTS) exit 0 ;;
  *) exit 1 ;;
esac
