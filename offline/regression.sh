#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"
py="$bundle/toolchain/venv/bin/python"
test -x "$py"
export CUDA_INSTALL_PATH="$bundle/toolchain/cuda-12.4"
export PATH="$(dirname "$py"):$CUDA_INSTALL_PATH/bin:$PATH"
[[ "${1:-}" == "--quick" ]] || exit 2
run_name="offline-v1-quick-ptx-$(date -u +%Y%m%dT%H%M%SZ)-$$"
OFFLINE_BUNDLE_ROOT="$bundle" "$repo/offline/smoke.sh"
"$repo/offline/run-logged.sh" ptx-fast bash -lc "source '$bundle/cache/apps/gpu-app-collection/src/setup_environment'; source '$repo/gpu-simulator/setup_environment.sh'; export ACCELSIM_ROOT='$repo'; \"$py\" '$repo/util/job_launching/run_simulations.py' -l local -B offline-v1-bfs-smoke -C QV100-PTX -N '$run_name'"
launch_log="$(find "$repo/util/job_launching/logfiles" -maxdepth 1 -type f -name "sim_log.${run_name}.*" -print -quit)"
test -n "$launch_log"
job_id="$(awk 'NR == 1 {print $2; exit}' "$launch_log")"
test -n "$job_id"
ptx_stdout=""
for _ in $(seq 1 120); do
  ptx_stdout="$(find "$repo/sim_run_12.4" -type f -name "*..o${job_id}" -newer "$launch_log" -print -quit)"
  if test -n "$ptx_stdout" && grep -Fq "PASSED" "$ptx_stdout" && grep -Fq "GPGPU-Sim: *** exit detected ***" "$ptx_stdout"; then
    break
  fi
  sleep 1
done
test -n "$ptx_stdout"
grep -Fq "PASSED" "$ptx_stdout"
grep -Fq "GPGPU-Sim: *** exit detected ***" "$ptx_stdout"
"$repo/offline/run-logged.sh" stats-quick bash -lc "\"$py\" '$repo/util/job_launching/get_stats.py' -N '$run_name' > '$bundle/logs/get_stats-quick.csv'"
test -s "$bundle/logs/get_stats-quick.csv"
