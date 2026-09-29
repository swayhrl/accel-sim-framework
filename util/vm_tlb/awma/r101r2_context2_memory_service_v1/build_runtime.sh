#!/usr/bin/env bash
set -o pipefail

export CUDA_INSTALL_PATH=/root/workspace/accel-sim-framework-awma-174-translation-frontend-pipelining-v1/.awma_runtime/candidate/toolchains/cuda-12.4.131-combined
export GPGPUSIM_ROOT=/root/awma_r101r2_context2_memory_service_174_v1_runtime/src/gpgpu-sim

runtime_root=/root/awma_r101r2_context2_memory_service_174_v1_runtime
durable_root=/root/share/mnt164/huangrulin/awma_r101r2_context2_memory_service_174_v1/runtime
framework=/root/workspace/accel-sim-framework-awma-r101r2-context2-memory-service-174-v1
patch_file="$framework/docs/vm_tlb/review_packs/AWMA_R101R2_CONTEXT2_MEMORY_SERVICE_ORACLE_174_V1/O2_CORE.patch"

source "$GPGPUSIM_ROOT/setup_environment" release
cd "$framework/gpu-simulator"
source ./setup_environment.sh release
set -euo pipefail

mkdir -p "$runtime_root/bin"
make -j4 >"$runtime_root/unified_build.log" 2>&1
cp ./bin/release/accel-sim.out "$runtime_root/bin/unified_accel-sim.out"

mkdir -p "$durable_root/bin"
cp "$runtime_root/bin/unified_accel-sim.out" "$durable_root/bin/unified_accel-sim.out"
cp "$runtime_root/unified_build.log" "$durable_root/unified_build.log"

durable_core="$durable_root/src/gpgpu-sim"
durable_lib="$durable_root/lib/gcc-11.4.0/cuda-12040/release"
mkdir -p "$durable_core/src/gpgpu-sim" "$durable_core/src" "$durable_lib"
cp "$GPGPUSIM_ROOT/src/abstract_hardware_model.cc" "$durable_core/src/"
cp "$GPGPUSIM_ROOT/src/abstract_hardware_model.h" "$durable_core/src/"
cp "$GPGPUSIM_ROOT/src/gpgpu-sim/"{awma_r101r2_o2_service.h,awma_transient_l2_policy.h,gpu-cache.cc,gpu-cache.h,shader.cc,shader.h,gpu-sim.cc,gpu-sim.h,l2cache.cc,l2cache.h,dram.cc,dram.h} "$durable_core/src/gpgpu-sim/"
cp "$GPGPUSIM_ROOT/lib/gcc-11.4.0/cuda-12040/release/libcudart.so" "$durable_lib/"
cp "$patch_file" "$durable_root/O2_CORE.patch"

sha256sum "$runtime_root/bin/unified_accel-sim.out" \
  "$GPGPUSIM_ROOT/lib/gcc-11.4.0/cuda-12040/release/libcudart.so" \
  "$patch_file"
