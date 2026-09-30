#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/exact_loss_cce_liger_109_v1_20260930
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-cce-liger-exact-loss-boundary-109-v1
LOCK=/data/c16/locks/c16_gpu_campaign.lock
OUT="$ROOT/raw/nsys/B1_CCE_EXACT"
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
unset LIGER_KERNEL_IMPL || true
export PYTHONUNBUFFERED=1
mkdir -p "$ROOT/raw/nsys" "$ROOT/logs"
exec 9>"$LOCK"
printf 'lock_wait_start_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$ROOT/logs/NSYS_GPU_LOCK_RECEIPT.txt"
flock -x 9
printf 'lock_acquired_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$ROOT/logs/NSYS_GPU_LOCK_RECEIPT.txt"
set +e
nsys profile --force-overwrite=true --trace=cuda,nvtx,osrt --capture-range=cudaProfilerApi --capture-range-end=stop -o "$OUT" \
  "$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/exact_loss_cce_liger/profile_b1_nsys.py" \
  --root "$ROOT" \
  --model-root /data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775 \
  >"$ROOT/logs/nsys_b1.stdout.log" \
  2>"$ROOT/logs/nsys_b1.stderr.log"
rc=$?
set -e
printf 'nsys_exit_code=%s\n' "$rc" >> "$ROOT/logs/NSYS_GPU_LOCK_RECEIPT.txt"
printf 'cuda_work_synchronized_before_profiler_stop=true\n' >> "$ROOT/logs/NSYS_GPU_LOCK_RECEIPT.txt"
printf 'lock_release_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$ROOT/logs/NSYS_GPU_LOCK_RECEIPT.txt"
flock -u 9
exec 9>&-
exit "$rc"
