#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$root/.." && pwd)}"
mkdir -p "$bundle/cache/wheelhouse" "$bundle/cache/assets" "$bundle/cache/debs" "$bundle/logs" "$root/docs-local/reports" "$root/gpu-simulator/extern"
src="$bundle/cache/sources/pybind11-v2.13.6.tar.gz"; test -f "$src"
test "$(sha256sum "$src" | awk '{print $1}')" = "e08cb87f4773da97fa7b5f035de8763abc656d87d5773e62f6da0587d1f0ec20"
rm -rf "$root/gpu-simulator/extern/pybind11" "$bundle/toolchain/pybind11-2.13.6"; tar -xzf "$src" -C "$bundle/toolchain"; mv "$bundle/toolchain/pybind11-2.13.6" "$root/gpu-simulator/extern/pybind11"
python3 -m venv "$bundle/toolchain/venv"; "$bundle/toolchain/venv/bin/pip" install --no-index --find-links "$bundle/cache/wheelhouse" -r "$root/requirements.txt"
OFFLINE_BUNDLE_ROOT="$bundle" "$root/offline/doctor.sh"
