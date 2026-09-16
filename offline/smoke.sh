#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; source "$root/offline/env.sh"
test -x "$root/gpu-simulator/bin/release/accel-sim.out"
echo "tiny real-SASS smoke requires cache/assets/traces/tiny-sass; no network fallback"
