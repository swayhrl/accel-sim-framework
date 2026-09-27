#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/c16/awma/r54_greedy_semantic_requal_v1r2_20260927
R1=/data/c16/awma/r54_fastpath_requal_v1r1_20260927
WT=/home/huangrulin/workspace/worktrees/accel-sim-awma-r54-greedy-semantic-requal-v1r2
export HF_HOME="$R1/hf_home"
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_DISABLE_XET=1
export USE_HUB_KERNELS=YES
for arm in P0 P1_D512 P2_D512 P1_D2048 P2_D2048; do
  dir="$ROOT/raw/production_profile/$arm"
  mkdir -p "$dir"
  flock -x /data/c16/locks/c16_gpu_campaign.lock \
    /usr/local/bin/nsys profile \
      --trace=cuda,nvtx,osrt,cublas --sample=none --cpuctxsw=none \
      --force-overwrite=true --output="$dir/$arm" \
      "$R1/env/bin/python" "$WT/util/vm_tlb/awma/r54_greedy_semantic_requal_v1r2/production.py" \
      --mode profile --arm "$arm" \
      >"$dir/profile.stdout.log" 2>"$dir/profile.stderr.log"
  tail -1 "$dir/profile.stdout.log"
  /usr/local/bin/nsys export --type sqlite --force-overwrite=true \
    --output="$dir/$arm.sqlite" "$dir/$arm.nsys-rep" >/dev/null 2>&1
  echo "NSYS_PROFILE_COMPLETE $arm"
done
