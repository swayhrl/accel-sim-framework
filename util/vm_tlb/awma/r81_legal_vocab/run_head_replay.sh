#!/usr/bin/env bash
set -euo pipefail
cohort="$1"
phase="$2"
ROOT=/data/c16/awma/r81_legal_vocab_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r81-legal-vocab-v1
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
export PYTHONUNBUFFERED=1
mkdir -p "$ROOT/raw/head_replay/$cohort" "$ROOT/logs"
flock -x /data/c16/locks/c16_gpu_campaign.lock \
  "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/r81_legal_vocab/head_replay.py" \
  --cohort "$cohort" --phase "$phase" \
  >"$ROOT/logs/head_replay_${cohort}_${phase}.stdout.log" \
  2>"$ROOT/logs/head_replay_${cohort}_${phase}.stderr.log"
tail -5 "$ROOT/logs/head_replay_${cohort}_${phase}.stdout.log"
