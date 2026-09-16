#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"
bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"
out="${1:-$bundle/dist/accel-sim-offline-v1.0.tar.gz}"
gpu_app_collection="cache/apps/gpu-app-collection"
mkdir -p "$bundle/dist" "$bundle/cache/git"
test "$(git -C "$repo" branch --show-current)" = project/offline-sim
test "$(git -C "$repo" rev-parse offline-sim-v1.0^{})" = "$(git -C "$repo" rev-parse HEAD)"
test -f "$bundle/$gpu_app_collection/src/setup_environment"
test -d "$bundle/$gpu_app_collection/4.2"
git -C "$repo" bundle create "$bundle/cache/git/framework-offline-sim-v1.0.bundle" project/offline-sim offline-sim-v1.0
git -C "$repo/gpu-simulator/gpgpu-sim" bundle create "$bundle/cache/git/gpgpu-sim-project-offline-sim.bundle" project/offline-sim
sha256sum "$bundle/cache/git/framework-offline-sim-v1.0.bundle" "$bundle/cache/git/gpgpu-sim-project-offline-sim.bundle" > "$bundle/cache/git/RELEASE_BUNDLES.SHA256"
tmp="$out.partial"; rm -f "$tmp"
tar --warning=no-file-changed \
  --exclude='accel-sim-framework/.git' \
  --exclude='accel-sim-framework/gpu-simulator/gpgpu-sim/.git' \
  --exclude='cache/apps/gpu-app-collection/.git' \
  --exclude='cache/git/gpu-app-collection.git' \
  --exclude='accel-sim-framework/gpu-simulator/build' \
  --exclude='logs/*' \
  -czf "$tmp" -C "$bundle" \
  accel-sim-framework \
  cache/apt \
  cache/assets \
  cache/cuda \
  cache/debs \
  cache/git \
  cache/sources \
  cache/traces \
  cache/wheelhouse \
  cache/wheels \
  "$gpu_app_collection" \
  toolchain
mv "$tmp" "$out"
sha256sum "$out" > "$out.sha256"
du -h "$out" > "$out.size"
