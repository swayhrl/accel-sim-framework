#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"
trace="$bundle/cache/assets/official/rodinia_2.0-ft/rodinia_2.0-ft/9.1/bfs-rodinia-2.0-ft/__data_graph4096_txt___data_graph4096_result_txt/traces/kernelslist.g"
test -x "$repo/gpu-simulator/bin/release/accel-sim.out"; test -f "$trace"
exec "$repo/offline/run-logged.sh" smoke-sass timeout 600 "$repo/gpu-simulator/bin/release/accel-sim.out" -trace "$trace" -config "$repo/gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/gpgpusim.config" -config "$repo/gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config"
