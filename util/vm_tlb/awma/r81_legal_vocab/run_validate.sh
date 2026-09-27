#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r81_legal_vocab_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r81-legal-vocab-v1
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
flock -x /data/c16/locks/c16_gpu_campaign.lock \
  "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/r81_legal_vocab/validate_legal_logits.py"
