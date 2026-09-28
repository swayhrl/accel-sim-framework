#!/usr/bin/env bash
set -euo pipefail

REPO=${C16_GPT3_REPO:?set C16_GPT3_REPO to the exact producer worktree}
ROOT=${C16_GPT3_ROOT:-/data/c16/gpt3_public_shape_scale_transfer_v1}
PY=${C16_GPT3_PYTHON:-/data/c16/env/c16-awq-v6/bin/python}
NCU=${C16_GPT3_NCU:-/opt/nvidia/nsight-compute/2025.1.1/target/linux-desktop-glibc_2_11_3-x64/ncu}
LOCK=/data/c16/locks/c16_gpu_campaign.lock
RUN_ID=$(cat "$ROOT/ACTIVE_RUN_ID")
RAW="$ROOT/$RUN_ID/raw"
RUNNER="$REPO/util/vm_tlb/c16/gpt3_public_shape_prep/runner.py"
VALIDATOR="$REPO/util/vm_tlb/c16/gpt3_public_shape_prep/validate_launch.py"
ANALYZER="$REPO/util/vm_tlb/c16/gpt3_public_shape_prep/analyze.py"
RESEAL="$REPO/util/vm_tlb/c16/gpt3_public_shape_prep/reseal.py"
PACK="$REPO/docs/vm_tlb/review_packs/C16_GPT3_PUBLIC_SHAPE_SCALE_TRANSFER_109_V1"
METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum,gpu__time_duration.sum

mkdir -p "$RAW"
exec 9>"$LOCK"
if ! flock -n 9; then echo "GPU lock held; refusing partial campaign" >&2; exit 75; fi
export C16_GPU_LOCK_HELD=1 C16_GPU_LOCK_FD=9
date -u +%FT%TZ > "$RAW/GPU_LOCK_START_UTC.txt"
nvidia-smi -q > "$RAW/NVIDIA_SMI_PRE.txt"
nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total --format=csv,noheader > "$RAW/GPU_IDENTITY.txt"

cd "$REPO"
nsys profile --trace=cuda,nvtx --sample=none --force-overwrite=true -o "$RAW/launch_audit" \
  "$PY" "$RUNNER" qualify --repo "$REPO" --raw "$RAW" 2>&1 | tee "$RAW/qualification.log"
nsys export --type sqlite --force-overwrite=true --output "$RAW/launch_audit.sqlite" "$RAW/launch_audit.nsys-rep"
"$PY" "$VALIDATOR" --sqlite "$RAW/launch_audit.sqlite" --output "$RAW/launch_audit.json"
"$PY" "$RUNNER" timing --repo "$REPO" --raw "$RAW" 2>&1 | tee "$RAW/timing.log"

for POINT in EXPAND_M256 CONTRACT_M256; do
  RANGE=C16_GPT3_NCU_DENSE_${POINT}; STEM=ncu_dense_${POINT}
  "$NCU" --nvtx --nvtx-include "${RANGE}/" --target-processes application-only --replay-mode application --cache-control none --metrics "$METRICS" --force-overwrite -o "$RAW/$STEM" \
    "$PY" "$RUNNER" profile_dense --repo "$REPO" --raw "$RAW" --point "$POINT" 2>&1 | tee "$RAW/${STEM}.log"
  "$NCU" --import "$RAW/${STEM}.ncu-rep" --csv --page raw --print-units base > "$RAW/${STEM}.csv"
done
for POINT in EXPAND_M256 CONTRACT_M256; do
  for CELL in A_W B_W A_E B_E; do
    RANGE=C16_GPT3_NCU_W4_${POINT}_${CELL}; STEM=ncu_w4_${POINT}_${CELL}
    "$NCU" --nvtx --nvtx-include "${RANGE}/" --target-processes application-only --replay-mode application --cache-control none --metrics "$METRICS" --force-overwrite -o "$RAW/$STEM" \
      "$PY" "$RUNNER" profile_w4 --repo "$REPO" --raw "$RAW" --point "$POINT" --cell "$CELL" 2>&1 | tee "$RAW/${STEM}.log"
    "$NCU" --import "$RAW/${STEM}.ncu-rep" --csv --page raw --print-units base > "$RAW/${STEM}.csv"
  done
done
nvidia-smi -q > "$RAW/NVIDIA_SMI_POST.txt"
date -u +%FT%TZ > "$RAW/GPU_LOCK_END_UTC.txt"
printf 'PASS\n' > "$RAW/LOCKED_CAMPAIGN_COMPLETE"
exec 9>&-
unset C16_GPU_LOCK_HELD C16_GPU_LOCK_FD

"$PY" "$ANALYZER" --raw "$RAW" --out "$PACK"
"$PY" "$RESEAL" --raw "$RAW" --pack "$PACK"
