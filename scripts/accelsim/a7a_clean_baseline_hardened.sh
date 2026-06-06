#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
report_path=".local_reports/A7A_clean_baseline_hardened_${ts}.md"
log_path=".local_logs/A7A_clean_baseline_hardened_${ts}.log"

status="PASS"
blocker="none"
baseline_commit="$(git rev-parse HEAD)"
a6_summary=""
a6_status="MISSING"
a2_stats=""
a4_stats=""
trace_root=""

exec > >(tee "$log_path") 2>&1

echo "A7A clean baseline hardened"
echo "Start: $start_iso"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED_ENV"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

if [ "$status" = "PASS" ] && [ -n "$(git status --short)" ]; then
  status="FAILED_DIRTY_TREE"
  blocker="git status was not clean at A7A start"
fi

if [ "$status" = "PASS" ]; then
  if bash scripts/accelsim/a6_clean_baseline_rerun.sh; then
    :
  else
    echo "A6 runner exited nonzero; parsing summary for final status"
  fi
fi

a6_summary="$(ls -t .local_reports/A6_clean_baseline_summary_*.md 2>/dev/null | head -1 || true)"
if [ -n "$a6_summary" ]; then
  a6_status="$(awk '/^## Status/{getline; getline; print; exit}' "$a6_summary")"
  a2_stats="$(sed -n 's/^- Stats CSV: `\(.*A2.*_stats.csv\)`/\1/p' "$a6_summary" | head -1)"
  a4_stats="$(sed -n 's/^- Stats CSV: `\(.*A4.*_stats.csv\)`/\1/p' "$a6_summary" | tail -1)"
  trace_root="$(sed -n 's/^- Trace root: `\(.*\)`/\1/p' "$a6_summary" | head -1)"
fi

if [ "$status" = "PASS" ]; then
  case "$a6_status" in
    PASS|PASS_CLEAN_DIFF_ZERO|PASS_NO_DIRTY_MARKER|PASS_NO_DIRTY_MARKER_COMMIT_NOT_FOUND) status="PASS" ;;
    BLOCKED_NO_TRACE|FAILED_ENV) status="BLOCKED"; blocker="A6 status: $a6_status" ;;
    FAILED_DIRTY_TREE|FAILED_DIRTY_BUILD_STRING|FAILED_A2_SMOKE|FAILED_A4_SMOKE|FAILED_BUILD|FAILED_BINARY) status="FAIL"; blocker="A6 status: $a6_status" ;;
    *) status="NEEDS_REVIEW"; blocker="could not classify A6 status: ${a6_status:-MISSING}" ;;
  esac
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A7A Clean Baseline Hardened

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a7a_clean_baseline_hardened.sh\`
- Log: \`$log_path\`
- Blocker: $blocker

## Baseline

- Baseline commit: \`$baseline_commit\`
- A6 summary: \`$a6_summary\`
- A6 status: \`$a6_status\`
- Trace root: \`$trace_root\`
- A2 stats: \`$a2_stats\`
- A4 stats: \`$a4_stats\`

## Build String Excerpts

\`\`\`
$(if [ -n "$a6_summary" ]; then awk '/### Excerpts/{flag=1;next}/### Version string classification|### Dirty marker grep/{flag=0}flag' "$a6_summary" | sed -n '1,120p'; fi)
\`\`\`

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

echo "A7A report: $report_path"
echo "A7A status: $status"

case "$status" in
  PASS|BLOCKED) exit 0 ;;
  *) exit 1 ;;
esac
