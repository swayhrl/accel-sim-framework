#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
report_path=".local_reports/A6B_version_string_audit_${ts}.md"
log_path=".local_logs/A6B_version_string_audit_${ts}.log"
sample_path=".local_reports/A6B_version_string_audit_${ts}_samples.csv"

status="PASS"
blocker="none"

exec > >(tee "$log_path") 2>&1

echo "A6B version string audit"
echo "Start: $start_iso"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED_ENV"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

python3 - "$sample_path" <<'PY'
import csv
import re
import sys

out = sys.argv[1]
samples = [
    ("accelsim-commit-2586635_modified_0.0_26-06-07-00-06-49", "CLEAN"),
    ("gpgpu-sim_git-commit-6c3cf4ff_modified_0.0", "CLEAN"),
    ("accelsim-commit-abc_modified_0", "CLEAN"),
    ("accelsim-commit-abc_modified_1.0", "DIRTY"),
    ("gpgpu-sim_git-commit-abc_modified_2", "DIRTY"),
    ("accelsim-commit-abc_dirty", "DIRTY"),
    ("gpgpu-sim_git-commit-abc_modified_0.0)", "CLEAN"),
    ("accelsim-commit-abc_modified_nonzero", "DIRTY"),
]
modified_re = re.compile(r"_modified_([0-9]+(?:\.[0-9]+)?)")

def classify(s):
    if "dirty" in s.lower():
        return "DIRTY"
    m = modified_re.search(s)
    if not m:
        return "DIRTY" if "_modified_" in s else "CLEAN"
    try:
        return "CLEAN" if float(m.group(1)) == 0 else "DIRTY"
    except ValueError:
        return "NEEDS_REVIEW"

with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sample", "expected", "actual", "pass"])
    for sample, expected in samples:
        actual = classify(sample)
        w.writerow([sample, expected, actual, str(actual == expected)])
PY

if grep -q ',False$' "$sample_path"; then
  status="FAILED_SAMPLE_CLASSIFICATION"
  blocker="one or more version string classifier samples failed"
fi

latest_a6="$(ls -t .local_reports/A6_clean_baseline_summary_*.md 2>/dev/null | head -1 || true)"
latest_scan="$(ls -t .local_reports/A6*_marker_scan_*.log .local_reports/A6_version_string_classification_*.log 2>/dev/null | head -1 || true)"
end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A6B Version String Audit

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a6b_version_string_audit.sh\`
- Log: \`$log_path\`
- Sample CSV: \`$sample_path\`
- Blocker: $blocker

## Git

- Branch: \`$(git branch --show-current)\`
- Commit: \`$(git rev-parse HEAD)\`

\`\`\`
$(git status --short)
\`\`\`

## Audited Files

- \`gpu-simulator/version_detection.mk\`
- \`gpu-simulator/gpgpu-sim/version_detection.mk\`
- \`scripts/accelsim/a6_clean_baseline_rerun.sh\`

## Version Makefile Excerpts

\`\`\`
$(grep -nE 'GIT_FILES_CHANGED|ACCELSIM_BUILD|GPGPUSIM_BUILD|modified' gpu-simulator/version_detection.mk gpu-simulator/gpgpu-sim/version_detection.mk)
\`\`\`

## Rule

\`_modified_0\`, \`_modified_0.0\`, and \`_modified_0.00\` mean clean diff zero in this repo when git status at build start and end is clean. Nonzero modified values and dirty tokens remain dirty.

## Sample Classification

\`\`\`
$(cat "$sample_path")
\`\`\`

## Previous A6 Evidence

- Latest A6 summary: \`${latest_a6:-}\`
- Latest A6 scan: \`${latest_scan:-}\`

\`\`\`
$(if [ -n "$latest_scan" ]; then sed -n '1,120p' "$latest_scan"; fi)
\`\`\`
EOF

echo "A6B report: $report_path"
echo "A6B status: $status"

[ "$status" = "PASS" ]
