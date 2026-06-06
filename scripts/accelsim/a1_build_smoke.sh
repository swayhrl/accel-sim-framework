#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
log_path=".local_logs/A1_build_${ts}.log"
report_path=".local_reports/A1_build_smoke_${ts}.md"
binary_path="./gpu-simulator/bin/release/accel-sim.out"

status="PASS"
blocker="none"
pip_status="not_run"
make_status="not_run"
cmake_status="not_run"
binary_status="not_checked"
help_status="not_run"
ldd_missing="not_checked"

exec > >(tee "$log_path") 2>&1

run_cmd() {
  echo
  echo "+ $*"
  "$@"
}

echo "A1 build and binary smoke"
echo "Start: $start_iso"
echo "Command: bash scripts/accelsim/a1_build_smoke.sh"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

if [ "$status" != "FAILED" ]; then
  if run_cmd pip3 install -r requirements.txt; then
    pip_status="PASS"
  else
    pip_status="FAILED_CONTINUED"
    echo "pip install failed; checking imports before deciding whether to continue"
    if python3 - <<'PY'
mods = ["yaml", "numpy", "pandas", "matplotlib", "scipy", "plotly", "psutil", "requests", "six"]
for mod in mods:
    __import__(mod)
PY
    then
      echo "required Python imports are already available"
    else
      status="FAILED"
      blocker="pip install failed and required imports are missing"
    fi
  fi
fi

if [ "$status" != "FAILED" ]; then
  if run_cmd make "-j$(nproc)" -C ./gpu-simulator/; then
    make_status="PASS"
  else
    make_status="FAILED"
    echo "Make build failed; trying CMake fallback"
    if run_cmd cmake -S ./gpu-simulator/ -B ./gpu-simulator/build &&
       run_cmd cmake --build ./gpu-simulator/build "-j$(nproc)" &&
       run_cmd cmake --install ./gpu-simulator/build; then
      cmake_status="PASS"
    else
      cmake_status="FAILED"
    fi
  fi
fi

if [ -x "$binary_path" ]; then
  binary_status="EXECUTABLE"
else
  binary_status="MISSING_OR_NOT_EXECUTABLE"
fi

if [ "$binary_status" = "EXECUTABLE" ]; then
  echo
  echo "+ test -x $binary_path"
  test -x "$binary_path"
  echo
  echo "+ file $binary_path"
  file "$binary_path" || true
  echo
  echo "+ ldd $binary_path"
  ldd "$binary_path" || true
  if ldd "$binary_path" 2>/dev/null | grep -q "not found"; then
    ldd_missing="YES"
  else
    ldd_missing="NO"
  fi
  echo
  echo "+ $binary_path --help"
  set +e
  "$binary_path" --help
  help_rc=$?
  set -e
  help_status="rc_${help_rc}"
else
  ldd_missing="unknown_binary_missing"
fi

if [ "$binary_status" = "EXECUTABLE" ]; then
  if [ "$make_status" = "PASS" ] || [ "$cmake_status" = "PASS" ]; then
    status="PASS"
  elif [ "$status" != "FAILED" ]; then
    status="PARTIAL_PASS_BINARY_EXISTS"
    blocker="build failed but existing executable binary is usable"
  fi
else
  status="FAILED"
  blocker="gpu-simulator/bin/release/accel-sim.out is missing or not executable"
fi

end_epoch="$(date +%s)"
end_iso="$(date -Iseconds)"
wall_clock="$((end_epoch - start_epoch))"
binary_mtime="missing"
if [ -e "$binary_path" ]; then
  binary_mtime="$(stat -c '%y' "$binary_path" 2>/dev/null || true)"
fi

cat > "$report_path" <<EOF
# A1 Build And Binary Smoke

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a1_build_smoke.sh\`
- Log: \`$log_path\`
- Blocker: $blocker
- Next action: proceed to A2 pre-trace smoke if binary status is EXECUTABLE.

## Results

- pip install: $pip_status
- make build: $make_status
- cmake fallback: $cmake_status
- binary path: \`$binary_path\`
- binary status: $binary_status
- binary timestamp: \`$binary_mtime\`
- help smoke status: $help_status
- ldd missing libraries: $ldd_missing

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF

echo
echo "A1 report: $report_path"
echo "A1 log: $log_path"
echo "A1 status: $status"

case "$status" in
  PASS|PARTIAL_PASS_BINARY_EXISTS) exit 0 ;;
  *) exit 1 ;;
esac
