#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
run_name="${ACCELSIM_A8_RUN_NAME:-A8_small_benchmark_baseline_${ts}}"
max_apps="${ACCELSIM_A8_MAX_APPS:-5}"
timeout_sec="${ACCELSIM_A8_TIMEOUT_SEC:-900}"
include_micro="${ACCELSIM_A8_INCLUDE_MICRO:-1}"
dry_run="${ACCELSIM_A8_DRY_RUN:-0}"
report_path=".local_reports/A8_small_benchmark_baseline_${ts}.md"
stats_path=".local_reports/A8_small_benchmark_baseline_${ts}_stats.csv"
log_path=".local_logs/A8_small_benchmark_baseline_${ts}.log"

status="PASS"
blocker="none"
a7a_status="MISSING"
a7b_report=""
a7b_stats=""

exec > >(tee "$log_path") 2>&1

echo "A8 small benchmark baseline"
echo "Start: $start_iso"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED_ENV"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

if [ "$status" = "PASS" ] && [ ! -x "$ACCELSIM_ROOT/bin/release/accel-sim.out" ]; then
  status="FAILED_BINARY"
  blocker="missing simulator binary"
fi

latest_a7a="$(ls -t .local_reports/A7A_clean_baseline_hardened_*.md 2>/dev/null | head -1 || true)"
if [ -n "$latest_a7a" ]; then
  a7a_status="$(sed -n 's/^- Status: //p' "$latest_a7a" | head -1)"
fi

if [ "$status" = "PASS" ]; then
  if ACCELSIM_A7B_RUN_NAME="$run_name" \
    ACCELSIM_A7B_MAX_APPS="$max_apps" \
    ACCELSIM_A7B_TIMEOUT_SEC="$timeout_sec" \
    ACCELSIM_A7B_DRY_RUN="$dry_run" \
    bash scripts/accelsim/a7b_n_app_smoke.sh; then
    :
  else
    status="PARTIAL_PASS_WITH_A7B_FAILURE"
    blocker="A7B runner returned nonzero"
  fi
fi

a7b_report="$(ls -t .local_reports/A7B_n_app_smoke_*.md 2>/dev/null | head -1 || true)"
a7b_stats="$(sed -n 's/^- Stats CSV: `\(.*\)`/\1/p' "$a7b_report" 2>/dev/null | head -1)"
if [ -n "$a7b_stats" ] && [ -f "$a7b_stats" ]; then
  cp "$a7b_stats" "$stats_path"
fi

if [ "$status" = "PASS" ] && [ "$dry_run" != "1" ] && [ "$a7a_status" != "PASS" ]; then
  status="PARTIAL_PASS_NOT_BASELINE_QUALITY"
  blocker="latest A7A status is $a7a_status"
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

passed="$(awk -F, 'NR>1 && $3=="PASS"{c++} END{print c+0}' "$stats_path" 2>/dev/null || echo 0)"
failed="$(awk -F, 'NR>1 && $3 ~ /FAIL/{c++} END{print c+0}' "$stats_path" 2>/dev/null || echo 0)"
timed_out="$(awk -F, 'NR>1 && $3=="TIMEOUT"{c++} END{print c+0}' "$stats_path" 2>/dev/null || echo 0)"
selected="$(awk 'END{print NR>0 ? NR-1 : 0}' "$stats_path" 2>/dev/null || echo 0)"

cat > "$report_path" <<EOF
# A8 Small Benchmark Baseline

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a8_small_benchmark_baseline.sh\`
- Log: \`$log_path\`
- Stats CSV: \`$stats_path\`
- Blocker: $blocker

## Baseline Quality

- Latest A7A report: \`${latest_a7a:-}\`
- Latest A7A status: \`$a7a_status\`
- Baseline commit: \`$(git rev-parse HEAD)\`

## Settings

- Run name: \`$run_name\`
- Max apps: \`$max_apps\`
- Timeout seconds: \`$timeout_sec\`
- Include micro if already present: \`$include_micro\`
- Dry run: \`$dry_run\`

## Results

- Selected: $selected
- Passed: $passed
- Failed: $failed
- Timed out: $timed_out
- A7B report: \`$a7b_report\`
- A7B stats: \`$a7b_stats\`

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

echo "A8 report: $report_path"
echo "A8 stats: $stats_path"
echo "A8 status: $status"

case "$status" in
  PASS|PARTIAL_PASS_NOT_BASELINE_QUALITY|PARTIAL_PASS_WITH_A7B_FAILURE) exit 0 ;;
  *) exit 1 ;;
esac
