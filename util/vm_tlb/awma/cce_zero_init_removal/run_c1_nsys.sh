#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/cce_zero_init_removal_109_v1_20260930
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-exact-loss-cce-zero-init-removal-109-v1
LOCK=/data/c16/locks/c16_gpu_campaign.lock
OUT="$ROOT/raw/nsys/C1_ZERO_INIT_REMOVED"
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
export CCE_AUTOTUNE=0
export PYTHONUNBUFFERED=1
mkdir -p "$ROOT/raw/nsys" "$ROOT/logs"
exec 9>"$LOCK"
RECEIPT="$ROOT/logs/nsys_c1_GPU_LOCK_RECEIPT.txt"
printf 'arm=C1\nlock_wait_start_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$RECEIPT"
flock -x 9
printf 'lock_acquired_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RECEIPT"
set +e
timeout --signal=TERM --kill-after=30s 600s   nsys profile --force-overwrite=true --trace=cuda,nvtx,osrt --capture-range=cudaProfilerApi --capture-range-end=stop -o "$OUT"   "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/cce_zero_init_removal/profile_c1_nsys.py" --root "$ROOT"   >"$ROOT/logs/nsys_c1.stdout.log" 2>"$ROOT/logs/nsys_c1.stderr.log"
rc=$?
set -e
printf 'exit_code=%s\ncuda_synchronized_before_profiler_stop=true\nlock_release_utc=%s\n' "$rc" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$RECEIPT"
flock -u 9
exec 9>&-
exit "$rc"
