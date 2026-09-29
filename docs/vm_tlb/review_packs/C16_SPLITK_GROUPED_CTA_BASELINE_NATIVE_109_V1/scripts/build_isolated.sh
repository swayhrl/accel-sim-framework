#!/usr/bin/env bash
set -euo pipefail
SOURCE_ROOT=${1:?patched source root required}
BUILD_ROOT=${2:?isolated build root required}
PYTHON=/data/c16/env/c16-awq-v6/bin/python
test -f "$SOURCE_ROOT/setup_grouped_cta.py"
mkdir -p "$BUILD_ROOT/lib" "$BUILD_ROOT/temp"
cd "$SOURCE_ROOT"
CUDA_HOME=/usr/local/cuda-12.6 PATH=/usr/local/cuda-12.6/bin:$PATH MAX_JOBS=8 \
  "$PYTHON" setup_grouped_cta.py build_ext \
  --build-lib "$BUILD_ROOT/lib" --build-temp "$BUILD_ROOT/temp"
