#!/usr/bin/env bash
# Concrete Route-E candidate: real TP=4, with NVBit injected only into rank 0.
set -euo pipefail
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ "${M4A_REQUIRED_GPU_COUNT:-}" == 4 ]] || { echo "error: Route E requires --required-gpu-count 4" >&2; exit 2; }
[[ "${M4A_MODEL_REVISION:-}" =~ ^[0-9a-f]{40}$ ]] || { echo "error: set M4A_MODEL_REVISION to an immutable 40-hex model commit" >&2; exit 2; }
[[ "${M4A_PHASE:-}" =~ ^(smoke|trace)$ ]] || { echo "error: M4A_PHASE must be smoke or trace" >&2; exit 2; }
[[ "${M4A_TRACE_REGION:-}" =~ ^(prefill|decode1|decode_reuse)$ ]] || { echo "error: M4A_TRACE_REGION must be prefill, decode1, or decode_reuse" >&2; exit 2; }
# Route E must never pass a parent's injection setting into torchrun.
unset CUDA_INJECTION64_PATH
exec torchrun --standalone --nproc_per_node=4 --no-python "$script_dir/rank0_nvbit_exec.sh" \
  python3 "$script_dir/llama_tp_workload.py" --route real-tp4-rank0 --region "$M4A_TRACE_REGION"
