#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$root/.." && pwd)}"; out="${1:-$bundle/dist/accel-sim-offline-v1.tar.gz}"
mkdir -p "$(dirname "$out")"
tar --exclude-vcs --exclude='accel-sim-framework/gpu-simulator/build' --exclude='logs/*' -czf "$out" -C "$bundle" "accel-sim-framework" cache toolchain
sha256sum "$out"
