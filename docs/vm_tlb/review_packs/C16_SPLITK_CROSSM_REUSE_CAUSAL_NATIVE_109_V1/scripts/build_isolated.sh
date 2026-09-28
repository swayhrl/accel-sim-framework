#!/usr/bin/env bash
set -euo pipefail

# PRE-GATE STATUS: recorded recipe only.  Do not execute until EARLY_GATE binds
# the exact patched source SHA and decision READY_FOR_NATIVE_CAUSAL_SCREEN.
SOURCE_ROOT=${1:?patched source root required}
BUILD_ROOT=${2:?isolated build root required}
PYTHON=/data/c16/env/c16-awq-v6/bin/python

test -f "$SOURCE_ROOT/setup_crossm_replica.py"
mkdir -p "$BUILD_ROOT/lib" "$BUILD_ROOT/temp"
cd "$SOURCE_ROOT"
CUDA_HOME=/usr/local/cuda-12.6 \
PATH=/usr/local/cuda-12.6/bin:$PATH \
MAX_JOBS=8 \
"$PYTHON" setup_crossm_replica.py build_ext \
  --build-lib "$BUILD_ROOT/lib" \
  --build-temp "$BUILD_ROOT/temp"

