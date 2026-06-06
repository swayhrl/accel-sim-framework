#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs .local_runs .local_traces review_packs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
log_path=".local_reports/A0_env_check_${ts}.log"
report_path=".local_reports/A0_env_check_${ts}.md"

status="PASS"
blocker="none"

exec > >(tee "$log_path") 2>&1

(
  echo "A0 env check"
  echo "Start: $start_iso"
  echo "Command: bash scripts/accelsim/a0_env_check.sh"
  echo
)

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAIL"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

{
  echo "date: $(date -Iseconds)"
  echo "hostname: $(hostname)"
  echo "pwd: $(pwd)"
  echo "git branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || true)"
  echo "git commit: $(git rev-parse HEAD 2>/dev/null || true)"
  echo "CUDA_INSTALL_PATH=${CUDA_INSTALL_PATH:-}"
  echo "CUDA_HOME=${CUDA_HOME:-}"
  echo "CUDA_PATH=${CUDA_PATH:-}"
  echo "ACCELSIM_REPO=${ACCELSIM_REPO:-}"
  echo "ACCELSIM_ROOT=${ACCELSIM_ROOT:-}"
  echo "GPGPUSIM_ROOT=${GPGPUSIM_ROOT:-}"
  echo "GPUWATTCH_ROOT=${GPUWATTCH_ROOT:-}"
  echo
  echo "nvcc --version:"
  nvcc --version || true
  echo
  echo "gcc --version:"
  gcc --version | sed -n '1,2p' || true
  echo
  echo "g++ --version:"
  g++ --version | sed -n '1,2p' || true
  echo
  echo "cmake --version:"
  cmake --version | sed -n '1,2p' || true
  echo
  echo "python3 --version:"
  python3 --version || true
  echo
  echo "pip3 --version:"
  pip3 --version || true
  echo
  echo "python import check:"
  python3 - <<'PY'
mods = ["yaml", "numpy", "pandas", "matplotlib", "scipy", "plotly", "psutil", "requests", "six"]
ok = True
for mod in mods:
    try:
        __import__(mod)
        print(f"{mod}: OK")
    except Exception as exc:
        ok = False
        print(f"{mod}: FAIL: {exc}")
raise SystemExit(0 if ok else 1)
PY
  py_import_rc=$?
  if [ "$py_import_rc" -ne 0 ]; then
    status="FAIL"
    blocker="one or more required Python imports failed"
  fi

  echo
  echo "git status --short:"
  git status --short || true
}

for required_dir in "${CUDA_INSTALL_PATH:-}" "${CUDA_HOME:-}" "${CUDA_PATH:-}" "${ACCELSIM_ROOT:-}" "${GPGPUSIM_ROOT:-}" "${GPUWATTCH_ROOT:-}"; do
  if [ -z "$required_dir" ] || [ ! -d "$required_dir" ]; then
    status="FAIL"
    blocker="required env path missing: ${required_dir:-<empty>}"
  fi
done

dirty_unexpected="$(git status --short | awk '
  $0 ~ /^(\?\?| M|M |A |AM|MM) docs\/accelsim_bringup\// { next }
  $0 ~ /^(\?\?| M|M |A |AM|MM) scripts\/$/ { next }
  $0 ~ /^(\?\?| M|M |A |AM|MM) scripts\/accelsim\// { next }
  { print }
')"
if [ -n "$dirty_unexpected" ]; then
  status="FAIL"
  blocker="unexpected git status entries"
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"

cat > "$report_path" <<EOF
# A0 Environment Check

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a0_env_check.sh\`
- Log: \`$log_path\`
- Blocker: $blocker
- Next action: proceed to A1 build smoke if status is PASS.

## Key Environment

- CUDA_INSTALL_PATH: \`${CUDA_INSTALL_PATH:-}\`
- CUDA_HOME: \`${CUDA_HOME:-}\`
- CUDA_PATH: \`${CUDA_PATH:-}\`
- ACCELSIM_ROOT: \`${ACCELSIM_ROOT:-}\`
- GPGPUSIM_ROOT: \`${GPGPUSIM_ROOT:-}\`
- GPUWATTCH_ROOT: \`${GPUWATTCH_ROOT:-}\`

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

echo "A0 report: $report_path"
echo "A0 log: $log_path"
echo "A0 status: $status"

if [ "$status" = "PASS" ]; then
  exit 0
fi
exit 1
