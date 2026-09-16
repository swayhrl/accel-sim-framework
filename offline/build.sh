#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$root/.." && pwd)}"; source "$root/offline/env.sh"
: "${CUDA_INSTALL_PATH:?Set CUDA_INSTALL_PATH to an installed compatible toolkit}"
test -x "$CUDA_INSTALL_PATH/bin/nvcc"
source "$root/gpu-simulator/setup_environment.sh"
log="$bundle/logs/build-$(date -u +%Y%m%dT%H%M%SZ).log"; rc="${log%.log}.rc"
set +e
{ cmake -S "$root/gpu-simulator" -B "$root/gpu-simulator/build/release" -DCMAKE_BUILD_TYPE=Release; cmake --build "$root/gpu-simulator/build/release" -j"${JOBS:-$(nproc)}"; cmake --install "$root/gpu-simulator/build/release"; } >"$log" 2>&1
status=$?
set -e
echo "$status" >"$rc"; exit "$status"
