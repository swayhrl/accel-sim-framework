#!/usr/bin/env bash
# torchrun invokes this once per rank.  Only rank 0 receives NVBit injection.
set -euo pipefail
[[ $# -gt 0 ]] || { echo "usage: rank0_nvbit_exec.sh COMMAND ..." >&2; exit 2; }
if [[ "${M4A_PHASE:-}" == trace && "${RANK:?torchrun must set RANK}" == 0 ]]; then
  export CUDA_INJECTION64_PATH="${M4A_NVBIT_PATH:?missing M4A_NVBIT_PATH}"
  exec "$@"
fi
unset CUDA_INJECTION64_PATH
exec "$@"
