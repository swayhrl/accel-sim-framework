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
tool_paths=()
[[ -n "${BISON:-}" ]] && tool_paths+=("$(dirname "$BISON")")
[[ -n "${FLEX:-}" ]] && tool_paths+=("$(dirname "$FLEX")")
[[ -n "${CUDA_INSTALL_PATH:-}" && -d "${CUDA_INSTALL_PATH:-}/bin" ]] && tool_paths+=("$CUDA_INSTALL_PATH/bin")
[[ ${#tool_paths[@]} -gt 0 ]] && export PATH="$(IFS=:; echo "${tool_paths[*]}"):$PATH"
