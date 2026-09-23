#!/usr/bin/env bash
set -euo pipefail

REPO=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-l2-persistence-intervention-109-v1
OUT=/data/c16/e1_l2_persistence_intervention_v1/build
CUDA_ROOT=/usr/local/cuda-12.8

mkdir -p "$OUT"
g++ -std=c++17 -O2 -fPIC -shared \
  "$REPO/util/vm_tlb/c16/e1_cuda_persistence_helper.cpp" \
  -I"$CUDA_ROOT/include" -L"$CUDA_ROOT/lib64" -Wl,-rpath,"$CUDA_ROOT/lib64" \
  -lcudart -o "$OUT/libc16_cuda_persistence.so"

sha256sum "$REPO/util/vm_tlb/c16/e1_cuda_persistence_helper.cpp" "$OUT/libc16_cuda_persistence.so" \
  > "$OUT/BUILD_SHA256SUMS"
