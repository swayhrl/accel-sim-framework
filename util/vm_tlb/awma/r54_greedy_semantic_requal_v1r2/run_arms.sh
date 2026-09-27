#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927
R1=/data/c16/awma/r54_fastpath_requal_v1r1_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r54-greedy-semantic-requal-v1r2
export HF_HOME="$R1/hf_home"
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_DISABLE_XET=1
export USE_HUB_KERNELS=YES
export PYTHONUNBUFFERED=1
mkdir -p "$ROOT/logs"
for prefix in S0 PREFIX_HOLDOUT_2048 PREFIX_DISCOVERY_4096; do
  for arm in F H; do
    echo "BEGIN ${prefix} ${arm}"
    flock -x /data/c16/locks/c16_gpu_campaign.lock \
      "$R1/env/bin/python" "$WT/util/vm_tlb/awma/r54_greedy_semantic_requal_v1r2/greedy_arm.py" \
      --prefix "$prefix" --arm "$arm" \
      >"$ROOT/logs/${prefix}_${arm}.log" 2>&1
    tail -1 "$ROOT/logs/${prefix}_${arm}.log"
    echo "END ${prefix} ${arm}"
  done
done
