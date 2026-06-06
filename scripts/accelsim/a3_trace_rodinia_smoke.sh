#!/usr/bin/env bash
set -u

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/../.." && pwd)"
cd "$repo_root" || exit 1

mkdir -p .local_reports .local_logs .local_runs hw_run

ts="$(date +%Y%m%d_%H%M%S)"
start_epoch="$(date +%s)"
start_iso="$(date -Iseconds)"
log_path=".local_logs/A3_trace_rodinia_${ts}.log"
report_path=".local_reports/A3_trace_rodinia_${ts}.md"
stats_path=".local_reports/A3_trace_rodinia_${ts}_stats.csv"
run_name="A3_generated_trace_smoke_${ts}"
gpu_device="${ACCELSIM_GPU_DEVICE:-0}"
gpu_apps_root="$repo_root/.local_runs/gpu-app-collection"

status="PASS"
blocker="none"
gpu_status="not_checked"
tracer_build_status="not_run"
app_build_status="not_run"
trace_status="not_run"
sim_status="not_run"
generated_trace_root=""

exec > >(tee "$log_path") 2>&1

run_cmd() {
  echo
  echo "+ $*"
  "$@"
}

write_report() {
  local end_epoch end_iso wall_clock
  end_epoch="$(date +%s)"
  end_iso="$(date -Iseconds)"
  wall_clock="$((end_epoch - start_epoch))"
  cat > "$report_path" <<EOF
# A3 NVBit Tracer Flow

- Status: $status
- Start time: $start_iso
- End time: $end_iso
- Wall clock seconds: $wall_clock
- Command: \`bash scripts/accelsim/a3_trace_rodinia_smoke.sh\`
- Log: \`$log_path\`
- Stats CSV: \`$stats_path\`
- Blocker: $blocker
- Next action: proceed to A4 smoke-suite scripting.

## Results

- GPU status: $gpu_status
- GPU device: \`$gpu_device\`
- NVBit tracer build: $tracer_build_status
- gpu-app-collection build: $app_build_status
- trace generation: $trace_status
- generated trace root: \`${generated_trace_root:-}\`
- generated-trace simulation: $sim_status

## GPU Detection

\`\`\`
$(if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi 2>&1; else echo "nvidia-smi: not found"; fi)
$(ls -l /dev/nvidia* 2>&1 || true)
\`\`\`

## Generated Kernels

\`\`\`
$(find hw_run/traces -type f -name kernelslist.g 2>/dev/null | sort | sed -n '1,80p')
\`\`\`

## Git Status

\`\`\`
$(git status --short)
\`\`\`
EOF
  echo
  echo "A3 report: $report_path"
  echo "A3 log: $log_path"
  echo "A3 stats: $stats_path"
  echo "A3 status: $status"
}

echo "A3 NVBit tracer flow"
echo "Start: $start_iso"
echo "Command: bash scripts/accelsim/a3_trace_rodinia_smoke.sh"

# shellcheck source=/dev/null
if ! source "$repo_root/scripts/accelsim/accelsim_env.sh"; then
  status="FAILED"
  blocker="failed to source scripts/accelsim/accelsim_env.sh"
fi

echo
echo "+ nvidia-smi"
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi; then
  nvidia_smi_ok=1
else
  nvidia_smi_ok=0
fi

echo
echo "+ ls -l /dev/nvidia*"
ls -l /dev/nvidia* 2>/dev/null || true

if [ "$status" != "FAILED" ]; then
  if [ "$nvidia_smi_ok" -ne 1 ] || ! ls /dev/nvidia* >/dev/null 2>&1; then
    status="BLOCKED_NO_GPU"
    blocker="no visible NVIDIA GPU: nvidia-smi unavailable or /dev/nvidia* missing"
    gpu_status="BLOCKED_NO_GPU"
    write_report
    exit 0
  fi
  gpu_status="PASS"
fi

if [ "$status" = "PASS" ]; then
  if run_cmd ./util/tracer_nvbit/install_nvbit.sh &&
     run_cmd make "-j$(nproc)" -C ./util/tracer_nvbit/; then
    tracer_build_status="PASS"
  else
    status="BLOCKED_TRACER_BUILD"
    blocker="NVBit install or tracer build failed"
    tracer_build_status="FAILED"
  fi
fi

if [ "$status" = "PASS" ]; then
  if [ -d "$gpu_apps_root/.git" ]; then
    run_cmd git -C "$gpu_apps_root" status --short || true
  elif [ -e "$gpu_apps_root" ]; then
    status="BLOCKED_APP_BUILD"
    blocker="$gpu_apps_root exists but is not a git clone"
  else
    if ! run_cmd git clone https://github.com/accel-sim/gpu-app-collection.git "$gpu_apps_root"; then
      status="BLOCKED_NETWORK"
      blocker="failed to clone gpu-app-collection"
    fi
  fi
fi

if [ "$status" = "PASS" ]; then
  # shellcheck source=/dev/null
  if source "$gpu_apps_root/src/setup_environment" &&
     run_cmd make "-j$(nproc)" -C "$gpu_apps_root/src" rodinia_2.0-ft &&
     run_cmd make -C "$gpu_apps_root/src" data; then
    app_build_status="PASS"
  else
    status="BLOCKED_APP_BUILD"
    blocker="gpu-app-collection rodinia_2.0-ft build or data setup failed"
    app_build_status="FAILED"
  fi
fi

if [ "$status" = "PASS" ]; then
  if run_cmd ./util/tracer_nvbit/run_hw_trace.py -B rodinia_2.0-ft -D "$gpu_device" -l 1 -t; then
    if find ./hw_run/traces -type f -name kernelslist.g | grep -q .; then
      trace_status="PASS"
      generated_trace_root="$(find "$repo_root/hw_run/traces" -type f -name kernelslist.g | head -1 | python3 -c 'import os,sys; p=sys.stdin.read().strip(); [print(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(p))))))] if p else None')"
    else
      status="BLOCKED_TRACE_RUNTIME"
      blocker="run_hw_trace.py completed but no kernelslist.g was found"
      trace_status="FAILED_NO_KERNELSLIST"
    fi
  else
    status="BLOCKED_TRACE_RUNTIME"
    blocker="run_hw_trace.py failed"
    trace_status="FAILED"
  fi
fi

if [ "$status" = "PASS" ]; then
  if ACCELSIM_TRACE_ROOT="$generated_trace_root" ACCELSIM_RUN_NAME="$run_name" ACCELSIM_A2_LAUNCH_MODE=direct bash scripts/accelsim/a2_pretrace_smoke.sh; then
    sim_status="PASS"
    latest_a2_stats="$(ls -t .local_reports/A2_pretrace_smoke_*_stats.csv 2>/dev/null | head -1 || true)"
    if [ -n "$latest_a2_stats" ]; then
      cp "$latest_a2_stats" "$stats_path"
    fi
  else
    sim_status="FAILED"
    status="BLOCKED_TRACE_RUNTIME"
    blocker="generated trace simulation failed"
  fi
fi

write_report

case "$status" in
  PASS|BLOCKED_NO_GPU|BLOCKED_NETWORK|BLOCKED_TRACER_BUILD|BLOCKED_APP_BUILD|BLOCKED_TRACE_RUNTIME) exit 0 ;;
  *) exit 1 ;;
esac
