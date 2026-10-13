#!/usr/bin/env bash
set -euo pipefail
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r27r3-numeric-attribution-capacity-109-v1
ROOT=/data/c16/awma/r27r3_numeric_attribution_109_v1_20261013
PARENT=/data/c16/awma/r27r2_varied_batch_capacity_109_v1_20261003
PY=/data/c16/awma/cce_zero_init_removal_109_v1_20260930/env/bin/python
cd "$WT"
export PYTHONPATH="$PARENT/source/cce" CCE_AUTOTUNE=0 CCE_DC_FIRST_STORE=1 R26_GPU_LOCK_HELD=1 R26_ALLOW_S2=1 R27R3_GPU_LOCK_HELD=1
export TRITON_CACHE_DIR="$ROOT/cache/triton" HF_HOME="$ROOT/cache/hf" TMPDIR="$ROOT/tmp" PYTHONDONTWRITEBYTECODE=1
{
 date -u +%FT%TZ
 free -h
 df -h /data/c16
 nvidia-smi --query-gpu=name,uuid,driver_version,memory.total,memory.used --format=csv,noheader
 nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader
} > "$ROOT/receipts/PRE_GPU_RESOURCE.txt"
(
 flock -x 9
 date -u +%FT%TZ > "$ROOT/receipts/B0_LOCK_ACQUIRE.txt"
 readlink /proc/$$/fd/9 >> "$ROOT/receipts/B0_LOCK_ACQUIRE.txt" || true
 trap 'date -u +%FT%TZ > "$ROOT/receipts/B0_LOCK_RELEASE_INTENT.txt"' EXIT
 for rid in a b; do
  "$PY" util/vm_tlb/awma/r27r3_numeric_attribution/diagnostics.py --mode repeat --root "$ROOT" --run-id "$rid" --model /data/c16/models/.incoming/Llama-3.2-1B/4e20de362430cd3b72f300e6b0f18e50e7166e08 --bank "$PARENT/input/token_bank/TOKEN_BANK.pt" --common "$PARENT/checkpoints/COMMON_POST_BOOTSTRAP.pt" --legacy "$WT/docs/vm_tlb/assets/c16/ai_workload_inputs/ADOPTED_LLAMA_S0_T128_V1/frozen_token_ids.json" 2>&1 | tee "$ROOT/logs/B0_$rid.log"
 done
) 9>/data/c16/locks/c16_gpu_campaign.lock
date -u +%FT%TZ > "$ROOT/receipts/B0_LOCK_CLOSED.txt"
"$PY" util/vm_tlb/awma/r27r3_numeric_attribution/diagnostics.py --mode compare_repeats --root "$ROOT" 2>&1 | tee "$ROOT/logs/B0_REPEAT_COMPARISON.log"
