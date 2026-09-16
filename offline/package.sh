#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$root/.." && pwd)}"; out="${1:-$bundle/dist/accel-sim-offline-v1.tar.gz}"
mkdir -p "$(dirname "$out")"
mkdir -p "$bundle/cache/git"
git -C "$root" bundle create "$bundle/cache/git/framework-full.bundle" --all
git -C "$root/gpu-simulator/gpgpu-sim" bundle create "$bundle/cache/git/gpgpu-sim-full.bundle" --all
sha256sum "$bundle/cache/git/framework-full.bundle" "$bundle/cache/git/gpgpu-sim-full.bundle" > "$bundle/cache/git/BUNDLES.SHA256"
tmp="${out}.partial"; rm -f "$tmp"
tar --warning=no-file-changed --exclude='accel-sim-framework/gpu-simulator/build' --exclude='logs/*' -czf "$tmp" -C "$bundle" "accel-sim-framework" cache toolchain
mv "$tmp" "$out"
sha256sum "$out"
