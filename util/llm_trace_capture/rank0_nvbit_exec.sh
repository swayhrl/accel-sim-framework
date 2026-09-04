#!/usr/bin/env bash
# torchrun invokes this once per rank.  Only rank 0 receives NVBit injection.
set -euo pipefail
[[ $# -gt 0 ]] || { echo "usage: rank0_nvbit_exec.sh COMMAND ..." >&2; exit 2; }
[[ -n "${RANK+x}" ]] || { echo "error: torchrun must set RANK" >&2; exit 2; }
[[ "$RANK" =~ ^[0-3]$ ]] || { echo "error: Route E requires RANK in 0..3, got '$RANK'" >&2; exit 2; }

# Deliberately clear inherited injection before making the one permitted
# rank-0 decision.  This protects against a contaminated login shell and is
# also why the parent Route-E driver never exports CUDA_INJECTION64_PATH.
unset CUDA_INJECTION64_PATH
if [[ "${M4A_PHASE:-}" == trace && "$RANK" == 0 ]]; then
  export CUDA_INJECTION64_PATH="${M4A_NVBIT_PATH:?missing M4A_NVBIT_PATH}"
fi
exec "$@"
