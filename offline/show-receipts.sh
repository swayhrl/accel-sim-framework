#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"
for receipt in "$bundle"/logs/*.rc; do
  [[ -f "$receipt" ]] || continue
  echo "$(basename "$receipt")=$(<"$receipt")"
done
find "$repo/gpu-simulator" -type f -name accel-sim.out -printf 'ACCEL_SIM_BINARY=%p %s\n' || true
