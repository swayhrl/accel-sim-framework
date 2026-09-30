#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/exact_loss_cce_liger_109_v1_20260930
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-cce-liger-exact-loss-boundary-109-v1
LOCK=/data/c16/locks/c16_gpu_campaign.lock
export HF_HOME="$ROOT/cache/hf"
export TRITON_CACHE_DIR="$ROOT/cache/triton"
export CUDA_CACHE_PATH="$ROOT/cache/cuda"
export TORCHINDUCTOR_CACHE_DIR="$ROOT/cache/inductor"
export XDG_CACHE_HOME="$ROOT/cache/xdg"
export TMPDIR="$ROOT/tmp"
unset LIGER_KERNEL_IMPL || true
export AWMA_GPU_LOCK_HELD=1
export PYTHONUNBUFFERED=1
mkdir -p "$HF_HOME" "$TRITON_CACHE_DIR" "$CUDA_CACHE_PATH" "$TORCHINDUCTOR_CACHE_DIR" "$XDG_CACHE_HOME" "$TMPDIR" "$ROOT/logs" "$ROOT/raw"
exec 9>"$LOCK"
printf 'lock_wait_start_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" > "$ROOT/logs/GPU_LOCK_RECEIPT.txt"
flock -x 9
printf 'lock_acquired_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$ROOT/logs/GPU_LOCK_RECEIPT.txt"
set +e
"$ROOT/env/bin/python" "$WT/util/vm_tlb/awma/exact_loss_cce_liger/run_exact_loss.py" \
  --root "$ROOT" \
  --model-root /data/c16/models/.incoming/qwen2p5_0p5b_instruct/7ae557604adf67be50417f59c2c2f167def9a775 \
  --r101-root /data/c16/awma/r101_fixed_ns_intermediate_lifecycle_20260927 \
  >"$ROOT/logs/gpu_campaign.stdout.log" \
  2>"$ROOT/logs/gpu_campaign.stderr.log"
rc=$?
set -e
printf 'campaign_exit_code=%s\n' "$rc" >> "$ROOT/logs/GPU_LOCK_RECEIPT.txt"
printf 'cuda_work_synchronized_by_campaign_finally=true\n' >> "$ROOT/logs/GPU_LOCK_RECEIPT.txt"
printf 'lock_release_utc=%s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$ROOT/logs/GPU_LOCK_RECEIPT.txt"
flock -u 9
exec 9>&-
exit "$rc"
