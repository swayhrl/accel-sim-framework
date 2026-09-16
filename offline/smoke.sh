#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$root/.." && pwd)}"; source "$root/offline/env.sh"; mkdir -p "$bundle/logs"
test -x "$root/gpu-simulator/bin/release/accel-sim.out"
echo "tiny real-SASS smoke requires cache/assets/traces/tiny-sass; no network fallback" | tee "$bundle/logs/smoke-$(date -u +%Y%m%dT%H%M%SZ).log"
