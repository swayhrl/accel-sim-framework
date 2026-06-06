#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs review_packs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
report_path=".local_reports/A5_final_summary_${ts}.md"
review_pack="review_packs/A0_A5_ACCELSIM_BRINGUP_review_pack_${ts}.tar.gz"
log_path=".local_logs/A5_collect_results_${ts}.log"

status="PASS"
blocker="none"

exec > >(tee "$log_path") 2>&1

latest_report() {
  # Intentionally allow glob expansion for the phase pattern.
  ls -t .local_reports/$1 2>/dev/null | head -1 || true
}

report_status() {
  local file="$1"
  if [ -n "$file" ] && [ -f "$file" ]; then
    sed -n 's/^- Status: //p' "$file" | head -1
  else
    echo "MISSING"
  fi
}

echo "A5 collect results"
echo "Start: $start_iso"
echo "Command: bash scripts/accelsim/a5_collect_results.sh"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

a0_report="$(latest_report 'A0*.md')"
a1_report="$(latest_report 'A1*.md')"
a2_report="$(latest_report 'A2*.md')"
a3_report="$(latest_report 'A3*.md')"
a4_report="$(latest_report 'A4*.md')"

a0_status="$(report_status "$a0_report")"
a1_status="$(report_status "$a1_report")"
a2_status="$(report_status "$a2_report")"
a3_status="$(report_status "$a3_report")"
a4_status="$(report_status "$a4_report")"

overall="PARTIAL_PASS"
if [ "$a0_status" = "PASS" ] &&
   [ "$a1_status" = "PASS" ] &&
   [ "$a2_status" = "PASS" ] &&
   [ "$a4_status" = "PASS" ]; then
  if [ "$a3_status" = "PASS" ]; then
    overall="PASS"
  else
    overall="PARTIAL_PASS"
  fi
else
  overall="FAIL"
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A5 Final Summary

- Status: $status
- Overall bringup result: $overall
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a5_collect_results.sh\`
- Log: \`$log_path\`
- Review pack: \`$review_pack\`
- Blocker: $blocker

## Git

- Branch: \`$(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)\`
- Commit: \`$(git rev-parse HEAD 2>/dev/null || true)\`

\`\`\`
$(git status --short)
\`\`\`

## Toolchain

\`\`\`
CUDA_INSTALL_PATH=${CUDA_INSTALL_PATH:-}
$(nvcc --version 2>&1 | sed -n '1,4p')
$(gcc --version 2>&1 | sed -n '1p')
$(g++ --version 2>&1 | sed -n '1p')
$(cmake --version 2>&1 | sed -n '1p')
$(python3 --version 2>&1)
\`\`\`

## Binary

\`\`\`
$(file ./gpu-simulator/bin/release/accel-sim.out 2>&1 || true)
$(ldd ./gpu-simulator/bin/release/accel-sim.out 2>&1 | grep 'not found' || echo 'ldd missing libraries: none')
\`\`\`

## Phase Status

| Phase | Status | Report |
| --- | --- | --- |
| A0 | $a0_status | \`$a0_report\` |
| A1 | $a1_status | \`$a1_report\` |
| A2 | $a2_status | \`$a2_report\` |
| A3 | $a3_status | \`$a3_report\` |
| A4 | $a4_status | \`$a4_report\` |
| A5 | $status | \`$report_path\` |

## Stats CSV

\`\`\`
$(ls -t .local_reports/*_stats.csv 2>/dev/null || true)
\`\`\`

## Traces

\`\`\`
$(find .local_traces hw_run -type f -name kernelslist.g 2>/dev/null | sort | sed -n '1,120p')
\`\`\`

## Run Directories

\`\`\`
$(find .local_runs -maxdepth 1 -type d \( -name 'A2_*' -o -name 'A3_*' -o -name 'A4_*' \) 2>/dev/null | sort)
\`\`\`
EOF

tar_inputs=()
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find docs/accelsim_bringup -maxdepth 1 -type f -name '*.md' | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find scripts/accelsim -maxdepth 1 -type f \( -name '*.sh' -o -name 'README.md' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_reports -maxdepth 1 -type f \( -name 'A[0-5]*.md' -o -name '*_stats.csv' \) | sort)
while IFS= read -r f; do tar_inputs+=("$f"); done < <(find .local_logs -maxdepth 1 -type f -name 'A[0-5]*.log' -size -2M | sort)

echo
echo "+ tar -czf $review_pack ..."
tar -czf "$review_pack" "${tar_inputs[@]}"

echo "A5 report: $report_path"
echo "A5 log: $log_path"
echo "Review pack: $review_pack"
echo "A5 status: $status"

if [ "$status" = "PASS" ]; then
  exit 0
fi
exit 1
