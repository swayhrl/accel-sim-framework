#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/cce_zero_init_removal_109_v1_20260930
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-exact-loss-cce-zero-init-removal-109-v1
LOCK=/data/c16/locks/c16_gpu_campaign.lock
PHASE="$1"
case "$PHASE" in
  directed) SCRIPT=run_directed.py; TIMEOUT_SECONDS=600 ;;
  real) SCRIPT=run_real.py; TIMEOUT_SECONDS=900 ;;
  *) echo "unknown phase: $PHASE" >&2; exit 2 ;;
esac
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
export CCE_AUTOTUNE=0
export PYTHONUNBUFFERED=1
mkdir -p "$HF_HOME" "$TRITON_CACHE_DIR" "$CUDA_CACHE_PATH" "$TORCHINDUCTOR_CACHE_DIR" "$XDG_CACHE_HOME" "$TMPDIR" "$ROOT/logs" "$ROOT/raw"
exec 9>"$LOCK"
RECEIPT="$ROOT/logs/$PHASE""_GPU_LOCK_RECEIPT.txt"
printf 'phase=%s\nlock_wait_start_utc=%s\n' "$PHASE" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RECEIPT"
flock -x 9
printf 'lock_acquired_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RECEIPT"
set +e
timeout --signal=TERM --kill-after=30s "$TIMEOUT_SECONDS""s"   "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/cce_zero_init_removal/$SCRIPT" --root "$ROOT"   >"$ROOT/logs/$PHASE.stdout.log" 2>"$ROOT/logs/$PHASE.stderr.log"
rc=$?
set -e
printf 'exit_code=%s\ncuda_synchronized_by_script_finally=true\nlock_release_utc=%s\n' "$rc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RECEIPT"
flock -u 9
exec 9>&-
exit "$rc"
