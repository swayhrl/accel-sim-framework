#!/usr/bin/env bash
set -euo pipefail
OFFLINE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export ACCELSIM_ROOT="$OFFLINE_ROOT"
export OFFLINE_SIM=1
export PIP_NO_INDEX=1
export PIP_FIND_LINKS="$OFFLINE_ROOT/cache/wheelhouse"
export GIT_CONFIG_NOSYSTEM=1
if [[ -n "${CUDA_INSTALL_PATH:-}" ]] && [[ -d "$CUDA_INSTALL_PATH" ]]; then export PATH="$CUDA_INSTALL_PATH/bin:$PATH"; fi
