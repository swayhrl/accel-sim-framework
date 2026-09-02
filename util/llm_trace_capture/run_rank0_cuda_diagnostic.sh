#!/usr/bin/env bash
# P4-only real four-rank diagnostic; no Llama weights and no formal trace.
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ "${M4A_PHASE:-}" =~ ^(smoke|trace)$ ]] || { echo "M4A_PHASE must be smoke or trace" >&2; exit 2; }
[[ "${M4A_PHASE:-}" != trace || -n "${M4A_NVBIT_PATH:-}" ]] || { echo "M4A_NVBIT_PATH required in trace mode" >&2; exit 2; }
unset CUDA_INJECTION64_PATH
exec torchrun --standalone --nproc_per_node=4 --no-python "$script_dir/rank0_nvbit_exec.sh" \
  python3 "$script_dir/rank0_cuda_diagnostic.py"
