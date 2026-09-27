#!/usr/bin/env bash
set -o pipefail

export CUDA_INSTALL_PATH=/root/workspace/accel-sim-framework-awma-174-translation-frontend-pipelining-v1/.awma_runtime/candidate/toolchains/cuda-12.4.131-combined
export GPGPUSIM_ROOT=/root/awma_r101_transient_l2_arch_174_v1_runtime/src/gpgpu-sim
runtime_root=/root/awma_r101_transient_l2_arch_174_v1_runtime
durable_root=/root/share/mnt164/huangrulin/awma_r101_transient_l2_arch_174_v1/runtime
framework=/root/workspace/accel-sim-framework-awma-r101-transient-l2-arch-174-v1

source "$GPGPUSIM_ROOT/setup_environment" release
cd "$framework/gpu-simulator"
source ./setup_environment.sh release
set -euo pipefail
mkdir -p "$runtime_root/bin"
make -j2 >"$runtime_root/unified_build.log" 2>&1
cp ./bin/release/accel-sim.out "$runtime_root/bin/unified_accel-sim.out"
mkdir -p "$durable_root/bin"
cp "$runtime_root/bin/unified_accel-sim.out" "$durable_root/bin/unified_accel-sim.out"
cp "$runtime_root/unified_build.log" "$durable_root/unified_build.log"
sha256sum "$runtime_root/bin/unified_accel-sim.out"
