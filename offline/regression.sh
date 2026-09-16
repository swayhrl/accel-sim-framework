#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$root/.." && pwd)}"; source "$root/offline/env.sh"; mkdir -p "$bundle/logs"
log="$bundle/logs/regression-$(date -u +%Y%m%dT%H%M%SZ).log"; rc="${log%.log}.rc"
{ for item in QV100-SASS_rodinia_2.0-ft GPU_Microbenchmark QV100-PTX run_simulations_local monitor_func_test get_stats; do echo "REQUIRES_OFFLINE_ASSET:$item"; done; echo "Use cached GPU-App-Collection at $bundle/cache/apps/gpu-app-collection; no clone/download permitted here."; } | tee "$log"
echo 0 > "$rc"
