#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export OFFLINE_BUNDLE_ROOT="${OFFLINE_BUNDLE_ROOT:-$(cd "$REPO_ROOT/.." && pwd)}"
export ACCELSIM_ROOT="$REPO_ROOT"
export OFFLINE_SIM=1
export PIP_NO_INDEX=1
export PIP_FIND_LINKS="$OFFLINE_BUNDLE_ROOT/cache/wheelhouse"
export GIT_CONFIG_NOSYSTEM=1
if [[ -z "${CUDA_INSTALL_PATH:-}" && -x "$OFFLINE_BUNDLE_ROOT/toolchain/cuda-12.4/bin/nvcc" ]]; then export CUDA_INSTALL_PATH="$OFFLINE_BUNDLE_ROOT/toolchain/cuda-12.4"; fi
if [[ -z "${BISON:-}" && -x "$OFFLINE_BUNDLE_ROOT/toolchain/bison-3.8.2/bin/bison" ]]; then export BISON="$OFFLINE_BUNDLE_ROOT/toolchain/bison-3.8.2/bin/bison"; fi
if [[ -z "${FLEX:-}" && -x "$OFFLINE_BUNDLE_ROOT/toolchain/flex-2.6.4/bin/flex" ]]; then export FLEX="$OFFLINE_BUNDLE_ROOT/toolchain/flex-2.6.4/bin/flex"; fi
export PATH="$(dirname "$BISON"):${FLEX%/*}:$CUDA_INSTALL_PATH/bin:$PATH"
