#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-l2-lifetime-control-v1r1
src="$worktree/util/vm_tlb/awma/r101_l2_lifetime_control_v1r1/persist.cu"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
/usr/local/cuda-12.8/bin/nvcc -std=c++17 -O3 -arch=sm_89 -shared \
    -Xcompiler -fPIC "$src" -o "$root/build/libpersist.so"
sha256sum "$src" "$root/build/libpersist.so" > "$root/build/PERSIST_SHA256SUMS"
