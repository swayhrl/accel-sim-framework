#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: build_common_workloads.sh --base-work-root DIR --work-root DIR [--cuda-home DIR] [--jobs N]

Builds the three GPU-only common-memory-stream cases from the source and SHOC
build tree already pinned by the TLS/C2P V100 campaign.  It never modifies the
source checkout.  WORK_ROOT receives only fresh binaries and provenance.
EOF
}

base_work_root=""
work_root=""
cuda_home="${CUDA_HOME:-/usr/local/cuda}"
jobs="$(nproc)"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-work-root) base_work_root="$2"; shift 2 ;;
    --work-root) work_root="$2"; shift 2 ;;
    --cuda-home) cuda_home="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$base_work_root" && -n "$work_root" ]] || { usage >&2; exit 2; }
[[ -x "$cuda_home/bin/nvcc" ]] || { echo "error: no nvcc at $cuda_home/bin/nvcc" >&2; exit 1; }
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: --jobs must be positive" >&2; exit 2; }

base_work_root="$(cd "$base_work_root" && pwd)"
work_root="$(mkdir -p "$work_root" && cd "$work_root" && pwd)"
gpuapps="$base_work_root/src/gpu-app-collection"
shoc_build="$base_work_root/build/shoc-sm70"
[[ -d "$gpuapps/.git" && -d "$shoc_build" ]] || {
  echo "error: missing pinned GPU-app source or SHOC build under $base_work_root" >&2; exit 1;
}
[[ "$(git -C "$gpuapps" rev-parse HEAD)" == "dad09cb0487845edc7524ded814c6cde9f0ef6a1" ]] || {
  echo "error: unexpected gpu-app-collection revision" >&2; exit 1;
}

export CUDA_HOME="$cuda_home"
export PATH="$cuda_home/bin:$PATH"
mkdir -p "$work_root/bin/shoc" "$work_root/bin/cuda"
shoc_cuda_libs="$shoc_build/src/common/libSHOCCommon.a -L$cuda_home/lib64 -lcudart"
for app in spmv triad; do
  make -C "$shoc_build/src/cuda/level1/$app" -j"$jobs" CUDA_LIBS="$shoc_cuda_libs"
done
install -m 0755 "$shoc_build/src/cuda/level1/spmv/Spmv" "$work_root/bin/shoc/Spmv"
install -m 0755 "$shoc_build/src/cuda/level1/triad/Triad" "$work_root/bin/shoc/Triad"

# The vendor Makefile emits only PTX for this old sample.  Build an explicit
# sm_70 cubin so that the V100 tracer observes Volta SASS rather than a
# driver-JIT-dependent image.
tensor_src="$gpuapps/src/cuda/NVIDIA_CUDA-11.0_Samples/cudaTensorCoreGemm"
(
  cd "$tensor_src"
  "$cuda_home/bin/nvcc" -std=c++14 -O3 -maxrregcount=255 \
    -I../common/inc -I"$cuda_home/include" \
    -gencode=arch=compute_70,code=sm_70 \
    cudaTensorCoreGemm.cu -L"$cuda_home/lib64" -lcudart \
    -o "$work_root/bin/cuda/cudaTensorCoreGemm"
)

for binary in "$work_root/bin/shoc/Spmv" "$work_root/bin/shoc/Triad" "$work_root/bin/cuda/cudaTensorCoreGemm"; do
  [[ -x "$binary" ]] || { echo "error: expected binary missing: $binary" >&2; exit 1; }
done
{
  printf 'timestamp_utc=%s\n' "$(date -u +%FT%TZ)"
  printf 'gpu_app_collection_commit=%s\n' "$(git -C "$gpuapps" rev-parse HEAD)"
  printf 'shoc_build=%s\n' "$shoc_build"
  "$cuda_home/bin/nvcc" --version
  sha256sum "$work_root/bin/shoc/Spmv" "$work_root/bin/shoc/Triad" "$work_root/bin/cuda/cudaTensorCoreGemm"
} > "$work_root/build-provenance.txt"
printf 'PASS binaries=3 provenance=%s\n' "$work_root/build-provenance.txt"
