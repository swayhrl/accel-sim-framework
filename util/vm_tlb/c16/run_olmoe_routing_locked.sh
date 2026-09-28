#!/usr/bin/env bash
set -euo pipefail

ROOT=/data/c16/olmoe_routing_provenance_multiround_v1
RUN_ID=$(cat "$ROOT/ACTIVE_RUN_ID")
RUN="$ROOT/raw/$RUN_ID"
LOCK=/data/c16/locks/c16_gpu_campaign.lock
PY=/data/c16/env/c16-olmoe-v34-runtime-v1/bin/python
REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-olmoe-routing-provenance-multiround-109-v1
RUNNER=$REPO/util/vm_tlb/c16/olmoe_routing_provenance_runner.py

exec 9>"$LOCK"
if ! flock -n 9; then
  echo "GPU lock is held; refusing partial execution" >&2
  exit 75
fi

date -u +%FT%TZ > "$RUN/GPU_LOCK_START_UTC.txt"
nvidia-smi -q > "$RUN/NVIDIA_SMI_PRE.txt"
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader > "$RUN/GPU_IDENTITY.txt"
cd "$REPO"
"$PY" "$RUNNER" 2>&1 | tee "$RUN/GPU_RUN.log"
nvidia-smi -q > "$RUN/NVIDIA_SMI_POST.txt"
date -u +%FT%TZ > "$RUN/GPU_LOCK_END_UTC.txt"
printf 'PASS\n' > "$RUN/GPU_LOCK_RELEASED"
