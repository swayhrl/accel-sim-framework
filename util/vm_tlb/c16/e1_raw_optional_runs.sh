#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-natural-reuse-residency-109-v1
OUT=/data/c16/e1_natural_reuse_residency_v1/raw_optional
NCU=/usr/local/cuda-12.8/bin/ncu
PYTHON=/data/c16/env/c16-awq-v6/bin/python
METRICS=l1tex__t_bytes.sum,lts__t_bytes.sum,dram__bytes.sum

exec 9>/data/c16/locks/c16_gpu_campaign.lock
if ! flock -n 9; then
  echo "GPU lock is held; refusing optional RAW control" >&2
  exit 75
fi

mkdir -p "$OUT/native" "$OUT/ncu"
cd "$REPO"
for run_index in 0 1 2 3 4 5 6; do
  "$PYTHON" util/vm_tlb/c16/e1_raw_natural_decode.py \
    --run-index "$run_index" --output "$OUT/native/run${run_index}.json" \
    > "$OUT/native/run${run_index}.stdout.log" 2>&1
done

"$NCU" --nvtx --nvtx-include "C16_E1_RAW_NAT_L0_UP_D0/" \
  --target-processes application-only --replay-mode application --cache-control none \
  --metrics "$METRICS" --force-overwrite -o "$OUT/ncu/RAW_NAT_L0_UP_D0" \
  "$PYTHON" util/vm_tlb/c16/e1_raw_natural_decode.py --run-index 100 \
  > "$OUT/ncu/RAW_NAT_L0_UP_D0.log" 2>&1

"$NCU" --import "$OUT/ncu/RAW_NAT_L0_UP_D0.ncu-rep" --csv --page raw --print-units base > "$OUT/ncu/RAW_NAT_L0_UP_D0.base.csv"
"$NCU" --import "$OUT/ncu/RAW_NAT_L0_UP_D0.ncu-rep" --csv --page session > "$OUT/ncu/RAW_NAT_L0_UP_D0.session.csv"
printf 'PASS\n' > "$OUT/COMPLETE"
