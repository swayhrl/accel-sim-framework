#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"
[[ "${1:-}" == "--quick" ]] || exit 2
OFFLINE_BUNDLE_ROOT="$bundle" "$repo/offline/smoke.sh"
"$repo/offline/run-logged.sh" ptx-fast bash -lc "export CUDA_INSTALL_PATH='$bundle/toolchain/cuda-12.4'; source '$bundle/cache/apps/gpu-app-collection/src/setup_environment'; source '$repo/gpu-simulator/setup_environment.sh'; python3 '$repo/util/job_launching/run_simulations.py' -l local -B rodinia_2.0-ft -C QV100-PTX -N offline-v1-quick-ptx"
"$repo/offline/run-logged.sh" monitor-quick python3 "$repo/util/job_launching/monitor_func_test.py" -v -N offline-v1-quick-ptx
"$repo/offline/run-logged.sh" stats-quick bash -lc "python3 '$repo/util/job_launching/get_stats.py' -N offline-v1-quick-ptx > '$bundle/logs/get_stats-quick.csv'"
