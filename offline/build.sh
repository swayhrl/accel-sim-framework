#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"
bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$root/.." && pwd)}"
mkdir -p "$bundle/logs"
printf 'repo=%s\nbundle=%s\n' "$root" "$bundle" > "$bundle/logs/build-bootstrap.log"
log="$bundle/logs/build-$(date -u +%Y%m%dT%H%M%SZ).log"
rc="${log%.log}.rc"
set +e
( 
  source "$root/offline/env.sh"
  : "${CUDA_INSTALL_PATH:?Set CUDA_INSTALL_PATH to an installed compatible toolkit}"
  test -x "$CUDA_INSTALL_PATH/bin/nvcc"
  set +u
  source "$root/gpu-simulator/setup_environment.sh"
  set -u
  cmake -S "$root/gpu-simulator" -B "$root/gpu-simulator/build/release" -DCMAKE_BUILD_TYPE=Release
  cmake --build "$root/gpu-simulator/build/release" -j"${JOBS:-4}"
  cmake --install "$root/gpu-simulator/build/release"
) >"$log" 2>&1
status=$?
set -e
printf '%s\n' "$status" >"$rc"
cp "$log" "$bundle/logs/build-latest.log"
cp "$rc" "$bundle/logs/build-latest.rc"
printf 'BUILD_LOG=%s\nBUILD_RC=%s\n' "$log" "$status"
exit "$status"
