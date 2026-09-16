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
"$repo/offline/run-logged.sh" ptx-fast bash -lc "source '$bundle/cache/apps/gpu-app-collection/src/setup_environment'; source '$repo/gpu-simulator/setup_environment.sh'; \"$py\" '$repo/util/job_launching/run_simulations.py' -l local -B rodinia_2.0-ft:bfs-rodinia-2.0-ft -C QV100-PTX -N '$run_name'"
"$repo/offline/run-logged.sh" monitor-quick "$py" "$repo/util/job_launching/monitor_func_test.py" -v -N "$run_name"
"$repo/offline/run-logged.sh" stats-quick bash -lc "\"$py\" '$repo/util/job_launching/get_stats.py' -N '$run_name' > '$bundle/logs/get_stats-quick.csv'"
