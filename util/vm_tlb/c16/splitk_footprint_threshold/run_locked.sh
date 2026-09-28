#!/usr/bin/env bash
set -euo pipefail
REPO=${C16_THRESHOLD_REPO:?set exact producer worktree}
ROOT=${C16_THRESHOLD_ROOT:-/data/c16/splitk_footprint_threshold_native_v1}
PY=${C16_THRESHOLD_PYTHON:-/data/c16/env/c16-awq-v6/bin/python}
NCU=${C16_THRESHOLD_NCU:-/opt/nvidia/nsight-compute/2025.1.1/target/linux-desktop-glibc_2_11_3-x64/ncu}
LOCK=/data/c16/locks/c16_gpu_campaign.lock;RUN_ID=$(cat "$ROOT/ACTIVE_RUN_ID");RAW="$ROOT/$RUN_ID/raw";DIR="$REPO/util/vm_tlb/c16/splitk_footprint_threshold";RUNNER="$DIR/runner.py";VALIDATOR="$DIR/validate_launch.py";ANALYZER="$DIR/analyze.py";RESEAL="$DIR/reseal.py";PACK="$REPO/docs/vm_tlb/review_packs/C16_SPLITK_FOOTPRINT_THRESHOLD_NATIVE_109_V1";METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum,gpu__time_duration.sum
mkdir -p "$RAW";SOURCE_COMMIT=$(git -C "$REPO" rev-parse HEAD);git -C "$REPO" diff --quiet;git -C "$REPO" diff --cached --quiet;printf '%s\n' "$SOURCE_COMMIT" > "$RAW/PRODUCER_SOURCE_COMMIT.txt"
exec 9>"$LOCK";if ! flock -n 9;then echo 'GPU lock held' >&2;exit 75;fi;export C16_GPU_LOCK_HELD=1 C16_GPU_LOCK_FD=9;date -u +%FT%TZ > "$RAW/GPU_LOCK_START_UTC.txt";nvidia-smi -q > "$RAW/NVIDIA_SMI_PRE.txt";nvidia-smi --query-gpu=name,uuid,driver_version,compute_cap,memory.total --format=csv,noheader > "$RAW/GPU_IDENTITY.txt"
cd "$REPO"
nsys profile --trace=cuda,nvtx --sample=none --capture-range=cudaProfilerApi --capture-range-end=stop --force-overwrite=true -o "$RAW/launch_audit" "$PY" "$RUNNER" qualify --repo "$REPO" --raw "$RAW" 2>&1 | tee "$RAW/qualification.log"
nsys export --type sqlite --force-overwrite=true --output "$RAW/launch_audit.sqlite" "$RAW/launch_audit.nsys-rep" 2> "$RAW/launch_audit_export.log"
"$PY" "$VALIDATOR" --sqlite "$RAW/launch_audit.sqlite" --output "$RAW/launch_audit.json" 2>&1 | tee "$RAW/launch_audit_validate.log"
"$PY" "$RUNNER" timing --repo "$REPO" --raw "$RAW" 2>&1 | tee "$RAW/timing.log"
for K in 2048 2560 3072 4096;do for ARM in A B;do RANGE=C16_SPLITK_THRESHOLD_NCU_K${K}_${ARM};STEM=ncu_K${K}_${ARM};"$NCU" --nvtx --nvtx-include "${RANGE}/" --target-processes application-only --replay-mode application --cache-control none --metrics "$METRICS" --force-overwrite -o "$RAW/$STEM" "$PY" "$RUNNER" profile --repo "$REPO" --raw "$RAW" --K "$K" --arm "$ARM" 2>&1 | tee "$RAW/${STEM}.log";"$NCU" --import "$RAW/${STEM}.ncu-rep" --csv --page raw --print-units base > "$RAW/${STEM}.csv" 2> "$RAW/${STEM}_export.log";done;done
nvidia-smi -q > "$RAW/NVIDIA_SMI_POST.txt";date -u +%FT%TZ > "$RAW/GPU_LOCK_END_UTC.txt";printf 'PASS\n' > "$RAW/LOCKED_CAMPAIGN_COMPLETE";exec 9>&-;unset C16_GPU_LOCK_HELD C16_GPU_LOCK_FD
"$PY" "$ANALYZER" --repo "$REPO" --raw "$RAW" --out "$PACK";"$PY" "$RESEAL" --raw "$RAW" --pack "$PACK"
