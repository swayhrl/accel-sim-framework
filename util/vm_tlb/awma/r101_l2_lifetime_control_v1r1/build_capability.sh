#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101_l2_lifetime_control_v1r1_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-l2-lifetime-control-v1r1
nvcc=/usr/local/cuda-12.8/bin/nvcc
cuobjdump=/usr/local/cuda-12.8/bin/cuobjdump
src="$worktree/util/vm_tlb/awma/r101_l2_lifetime_control_v1r1/discard.cu"
mkdir -p "$root/build" "$root/raw" "$root/logs"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
"$nvcc" --version > "$root/build/nvcc_version.txt"
"$nvcc" -std=c++17 -O3 -arch=sm_89 -ptx "$src" -o "$root/build/discard.ptx"
"$nvcc" -std=c++17 -O3 -arch=sm_89 -cubin "$src" -o "$root/build/discard.cubin"
"$nvcc" -std=c++17 -O3 -arch=sm_89 -shared -Xcompiler -fPIC "$src" -o "$root/build/libdiscard.so"
"$nvcc" -std=c++17 -O3 -arch=sm_89 -DR101R1_CAPABILITY_MAIN "$src" -o "$root/build/capability"
"$cuobjdump" --dump-sass "$root/build/discard.cubin" > "$root/build/discard.sass.txt"
"$root/build/capability" > "$root/R101R1_DEVICE_CAPABILITY_RAW.json"
sha256sum "$src" "$root/build/discard.ptx" "$root/build/discard.cubin" \
    "$root/build/libdiscard.so" "$root/build/capability" > "$root/build/SHA256SUMS"
grep -n 'discard.global.L2' "$root/build/discard.ptx"
grep -niE 'CCTL|DISCARD' "$root/build/discard.sass.txt" || true
cat "$root/R101R1_DEVICE_CAPABILITY_RAW.json"
