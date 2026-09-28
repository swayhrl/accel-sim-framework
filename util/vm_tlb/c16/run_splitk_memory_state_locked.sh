#!/usr/bin/env bash
set -euo pipefail

ROOT=/data/c16/splitk_memory_state_interaction_v1
RUN_ID=$(cat "$ROOT/ACTIVE_RUN_ID")
RUN="$ROOT/$RUN_ID"
RAW="$RUN/raw"
LOCK=/data/c16/locks/c16_gpu_campaign.lock
PY=/data/c16/env/c16-awq-v6/bin/python
REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-splitk-memory-state-interaction-109-v1
RUNNER=$REPO/util/vm_tlb/c16/splitk_memory_state_runner.py
VALIDATE=$REPO/util/vm_tlb/c16/splitk_memory_state_validate_launch.py
NCU=/opt/nvidia/nsight-compute/2025.1.1/target/linux-desktop-glibc_2_11_3-x64/ncu
METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum

mkdir -p "$RAW"
exec 9>"$LOCK"
if ! flock -n 9; then
  echo "GPU lock is held; refusing partial campaign" >&2
  exit 75
fi

date -u +%FT%TZ > "$RAW/GPU_LOCK_START_UTC.txt"
nvidia-smi -q > "$RAW/NVIDIA_SMI_PRE.txt"
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap --format=csv,noheader > "$RAW/GPU_IDENTITY.txt"

cd "$REPO"
nsys profile --trace=cuda,nvtx --sample=none --capture-range=cudaProfilerApi --capture-range-end=stop \
  --force-overwrite=true -o "$RAW/launch_audit" \
  "$PY" "$RUNNER" qualify 2>&1 | tee "$RAW/qualification.log"
nsys export --type sqlite --force-overwrite=true --output "$RAW/launch_audit.sqlite" "$RAW/launch_audit.nsys-rep" \
  2>&1 | tee "$RAW/launch_audit_export.log"
"$PY" "$VALIDATE" --sqlite "$RAW/launch_audit.sqlite" --output "$RAW/launch_audit.json" \
  2>&1 | tee "$RAW/launch_audit_validate.log"

"$PY" "$RUNNER" timing 2>&1 | tee "$RAW/timing.log"

for OP in up_proj down_proj; do
  for CELL in A_W B_W A_E B_E; do
    RANGE=C16_SPLITK_STATE_${OP}_${CELL}
    STEM=ncu_${OP}_${CELL}
    "$NCU" --nvtx --nvtx-include "${RANGE}/" --target-processes application-only \
      --replay-mode application --cache-control none --metrics "$METRICS" --force-overwrite \
      -o "$RAW/$STEM" "$PY" "$RUNNER" profile --operator "$OP" --cell "$CELL" \
      2>&1 | tee "$RAW/${STEM}.log"
    "$NCU" --import "$RAW/${STEM}.ncu-rep" --csv --page raw --print-units base \
      > "$RAW/${STEM}.csv" 2> "$RAW/${STEM}_export.log"
  done
done

nvidia-smi -q > "$RAW/NVIDIA_SMI_POST.txt"
date -u +%FT%TZ > "$RAW/GPU_LOCK_END_UTC.txt"
printf 'PASS\n' > "$RAW/LOCKED_CAMPAIGN_COMPLETE"
