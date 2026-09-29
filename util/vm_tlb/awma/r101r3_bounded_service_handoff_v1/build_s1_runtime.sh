#!/usr/bin/env bash
set -o pipefail

source_runtime=/root/awma_r101r2_context2_memory_service_174_v1_runtime
target_runtime=/root/awma_r101r3_bounded_service_handoff_174_v1_runtime
framework=/root/workspace/accel-sim-framework-awma-r101r3-bounded-service-handoff-174-v1
patch_file="$framework/docs/vm_tlb/review_packs/AWMA_R101R3_BOUNDED_SERVICE_HANDOFF_174_V1/S1_CORE.patch"
durable=/root/share/mnt164/huangrulin/awma_r101r3_bounded_service_handoff_174_v1/runtime/S1_frozen
export CUDA_INSTALL_PATH=/root/workspace/accel-sim-framework-awma-174-translation-frontend-pipelining-v1/.awma_runtime/candidate/toolchains/cuda-12.4.131-combined

if [[ "${1:-}" == "--prepare" ]]; then
  if [[ -e "$target_runtime" ]]; then
    echo "target runtime already exists: $target_runtime" >&2
    exit 2
  fi
  cp -a --reflink=auto "$source_runtime" "$target_runtime"
  for target in \
    "$target_runtime/src/gpgpu-sim/build" \
    "$target_runtime/src/gpgpu-sim/lib" \
    "$target_runtime/bin"
  do
    resolved=$(realpath -m "$target")
    case "$resolved" in
      "$target_runtime"/*) ;;
      *) echo "unsafe generated target: $resolved" >&2; exit 3 ;;
    esac
    rm -rf -- "$target"
  done
  rm -f -- "$target_runtime/unified_build.log"
  mkdir -p "$target_runtime/bin"
  (
    cd "$target_runtime/src/gpgpu-sim"
    patch -p1 --batch --forward <"$patch_file"
  )
fi

if [[ ! -d "$target_runtime/src/gpgpu-sim" ]]; then
  echo "prepared runtime is missing: $target_runtime" >&2
  exit 4
fi

export GPGPUSIM_ROOT="$target_runtime/src/gpgpu-sim"
source "$GPGPUSIM_ROOT/setup_environment" release
cd "$framework/gpu-simulator"
source ./setup_environment.sh release
set -euo pipefail
make -j4 >"$target_runtime/unified_build.log" 2>&1
cp ./bin/release/accel-sim.out "$target_runtime/bin/unified_accel-sim.out"

binary_sha=$(sha256sum "$target_runtime/bin/unified_accel-sim.out" | awk '{print $1}')
library_sha=$(sha256sum "$GPGPUSIM_ROOT/lib/gcc-11.4.0/cuda-12040/release/libcudart.so" | awk '{print $1}')
patch_sha=$(sha256sum "$patch_file" | awk '{print $1}')

[[ "$binary_sha" == "ae3a71d8b75bb6e4b019b0f355801d5e529a3178085d9e8c9671dffee4f1cdfc" ]]
[[ "$library_sha" == "2abc6cdc694a245edf0a61606bad7a9ef487e16da07802cbc32f74e29ebc68fd" ]]
[[ "$patch_sha" == "768804050c22cb85168b2e73daa6414fcd6c519b429dd000ceaec84bfdf037a4" ]]

if [[ -d "$durable" ]]; then
  (cd "$durable" && sha256sum -c SHA256SUMS)
fi
printf 'S1_BUILD_PASS binary=%s library=%s patch=%s\n' \
  "$binary_sha" "$library_sha" "$patch_sha"
