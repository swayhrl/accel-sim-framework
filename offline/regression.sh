#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; source "$root/offline/env.sh"
for item in QV100-SASS_rodinia_2.0-ft GPU_Microbenchmark QV100-PTX run_simulations_local monitor_func_test get_stats; do echo "REQUIRES_OFFLINE_ASSET:$item"; done
echo "Use cached GPU-App-Collection at $root/cache/git/gpu-app-collection.git; no clone/download permitted here."
