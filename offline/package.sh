#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; out="${1:-$root/dist/accel-sim-offline-v1.tar.gz}"
mkdir -p "$(dirname "$out")"
tar --exclude-vcs --exclude='cache/assets/*' --exclude='gpu-simulator/build' -czf "$out" -C "$(dirname "$root")" "$(basename "$root")"
sha256sum "$out"
