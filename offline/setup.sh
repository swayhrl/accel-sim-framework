#!/usr/bin/env bash
set -euo pipefail
repo="$(cd "$(dirname "$0")/.." && pwd)"; bundle="${OFFLINE_BUNDLE_ROOT:-$(cd "$repo/.." && pwd)}"; src="$bundle/cache/sources/pybind11-v2.13.6.tar.gz"
mkdir -p "$bundle/toolchain" "$bundle/logs" "$repo/gpu-simulator/extern"
test "$(sha256sum "$src"|awk '{print $1}')" = "e08cb87f4773da97fa7b5f035de8763abc656d87d5773e62f6da0587d1f0ec20"
rm -rf "$bundle/toolchain/venv" "$repo/gpu-simulator/extern/pybind11" "$bundle/toolchain/pybind11-2.13.6"; tar -xzf "$src" -C "$bundle/toolchain"; mv "$bundle/toolchain/pybind11-2.13.6" "$repo/gpu-simulator/extern/pybind11"
python3 -m venv "$bundle/toolchain/venv"; "$bundle/toolchain/venv/bin/pip" install --no-index --find-links "$bundle/cache/wheelhouse" -r "$repo/offline/python-requirements.lock"
"$bundle/toolchain/venv/bin/python" -c "import yaml,pandas,plotly,kaleido,psutil,tqdm"
OFFLINE_BUNDLE_ROOT="$bundle" "$repo/offline/doctor.sh"
