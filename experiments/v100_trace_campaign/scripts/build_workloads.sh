#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: build_workloads.sh --work-root DIR [--cuda-home DIR] [--jobs N]

Fetches exact source revisions named in inputs.json and builds only the six TLS
and eight C2P missing applications for Volta sm_70. Build artefacts are placed
under WORK_ROOT/{src,build,bin}; source trees outside WORK_ROOT are untouched.
EOF
}

work_root=""
cuda_home="${CUDA_HOME:-/usr/local/cuda}"
jobs="$(nproc)"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --work-root) work_root="$2"; shift 2 ;;
    --cuda-home) cuda_home="$2"; shift 2 ;;
    --jobs) jobs="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "error: unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done
[[ -n "$work_root" ]] || { echo "error: --work-root is required" >&2; exit 2; }
[[ -x "$cuda_home/bin/nvcc" ]] || { echo "error: no nvcc at $cuda_home/bin/nvcc" >&2; exit 1; }
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || { echo "error: --jobs must be positive" >&2; exit 2; }
# AutoDL's CUDA path is initialized only by interactive shell profile files.
# Autotools configure probes use PATH rather than CUDA_HOME, so make it
# explicit for tmux/non-interactive campaign execution.
export CUDA_HOME="$cuda_home"
export PATH="$cuda_home/bin:$PATH"
work_root="$(mkdir -p "$work_root" && cd "$work_root" && pwd)"
src_root="$work_root/src"
build_root="$work_root/build"
bin_root="$work_root/bin"
mkdir -p "$src_root" "$build_root" "$bin_root/shoc" "$bin_root/mars" "$bin_root/gpuapps"

checkout_commit() {
  local url="$1" dir="$2" commit="$3"
  if [[ ! -d "$dir/.git" ]]; then
    git clone --filter=blob:none "$url" "$dir"
  fi
  # A local seed may have been rsynced to a cloud host whose GitHub egress is
  # slow or unavailable.  Do not contact origin when the required immutable
  # commit is already present in that seed.
  if ! git -C "$dir" cat-file -e "${commit}^{commit}" 2>/dev/null; then
    git -C "$dir" fetch --tags origin "$commit"
  fi
  git -C "$dir" checkout --detach "$commit"
  [[ "$(git -C "$dir" rev-parse HEAD)" == "$commit" ]] || {
    echo "error: source revision mismatch for $dir" >&2; exit 1;
  }
}

shoc_src="$src_root/shoc"
checkout_commit https://github.com/vetter/shoc.git "$shoc_src" 00b25e2751dde4f1d7c595cadbb7fdb0873257b0
shoc_build="$build_root/shoc-sm70"
if [[ ! -f "$shoc_build/config.status" ]]; then
  # Git checkout timestamps can make this 2014 Autotools release incorrectly
  # try to regenerate itself with aclocal-1.11/automake-1.11.  We use its
  # shipped configure/Makefile.in files, so normalize source timestamps before
  # configuring instead of requiring obsolete Autotools on the cloud host.
  find "$shoc_src" -type f -exec touch -t 202001010000 {} +
  mkdir -p "$shoc_build"
  (
    cd "$shoc_build"
    "$shoc_src/configure" --with-cuda --without-opencl --without-mpi --disable-stability \
      CUDA_CPPFLAGS='-gencode=arch=compute_70,code=sm_70'
  )
fi
make -C "$shoc_build/src/common" -j"$jobs"
shoc_cuda_libs="$shoc_build/src/common/libSHOCCommon.a -L$cuda_home/lib64 -lcudart"
for app in fft sort gemm stencil2d reduction; do
  make -C "$shoc_build/src/cuda/level1/$app" -j"$jobs" CUDA_LIBS="$shoc_cuda_libs"
done
install -m 0755 "$shoc_build/src/cuda/level1/fft/FFT" "$bin_root/shoc/FFT"
install -m 0755 "$shoc_build/src/cuda/level1/sort/Sort" "$bin_root/shoc/Sort"
install -m 0755 "$shoc_build/src/cuda/level1/gemm/GEMM" "$bin_root/shoc/GEMM"
install -m 0755 "$shoc_build/src/cuda/level1/stencil2d/Stencil2D" "$bin_root/shoc/Stencil2D"
install -m 0755 "$shoc_build/src/cuda/level1/reduction/Reduction" "$bin_root/shoc/Reduction"

mars_zip="$src_root/Mars.zip"
mars_src="$src_root/Mars"
if [[ ! -d "$mars_src" ]]; then
  curl --fail --location --retry 4 --output "$mars_zip" \
    https://cse.hkust.edu.hk/catalac/users/wenbin/mars/Mars.zip
  unzip -q "$mars_zip" -d "$src_root"
fi
mars_app="$mars_src/sample_apps/SimilarityScore"
[[ -d "$mars_app" ]] || { echo "error: Mars SimilarityScore not found after extraction" >&2; exit 1; }
gpuapps_src="$src_root/gpu-app-collection"
checkout_commit https://github.com/accel-sim/gpu-app-collection.git "$gpuapps_src" dad09cb0487845edc7524ded814c6cde9f0ef6a1
sdk_root="$gpuapps_src/4.2"
if [[ ! -f "$sdk_root/C/lib/libcutil_x86_64.a" ]]; then
  # The app collection intentionally omits NVIDIA SDK 4.2 from git.  Several
  # retained ISPASS/Pannotia/Mars programs use its cutil compatibility library.
  sdk_installer="$gpuapps_src/gpucomputingsdk_4.2.9_linux.run"
  if [[ ! -f "$sdk_installer" ]]; then
    curl --fail --location --retry 4 --output "$sdk_installer" \
      http://developer.download.nvidia.com/compute/cuda/4_2/rel/sdk/gpucomputingsdk_4.2.9_linux.run
  fi
  chmod u+x "$sdk_installer"
  "$sdk_installer" -- --prefix="$sdk_root" --cudaprefix="$cuda_home"
  make -C "$sdk_root/C/common" -j"$jobs"
fi
cutil_inc="$gpuapps_src/src/cuda/common/inc"
cutil_lib="$gpuapps_src/src/cuda/common/lib/libcutil_x86_64.a"
if [[ ! -f "$cutil_lib" ]]; then
  cutil_inc="$sdk_root/C/common/inc"
  cutil_lib="$sdk_root/C/lib/libcutil_x86_64.a"
fi
[[ -f "$cutil_inc/cutil.h" && -f "$cutil_lib" ]] || { echo "error: missing GPU-app-collection cutil compatibility files" >&2; exit 1; }
(
  cd "$mars_app"
  "$cuda_home/bin/nvcc" -std=c++11 -arch=sm_70 -I"$cutil_inc" \
    main.cu MarsScan.cu MarsSort.cu MarsLib.cu MarsUtils.cpp "$cutil_lib" \
    -o "$bin_root/mars/SimilarityScore"
)

# Build C2P's eight missing applications using the maintained GPU-app-collection.
# The old Makefiles list obsolete gencode targets, so clear them and inject sm_70.
export CUDA_INSTALL_PATH="$cuda_home"
export NVIDIA_COMPUTE_SDK_LOCATION="$sdk_root"
export BINDIR="$bin_root"
export BINSUBDIR="gpuapps"
export GENCODE_ARCH='-gencode=arch=compute_70,code=sm_70'
export GENCODE_SM10= GENCODE_SM13= GENCODE_SM20= GENCODE_SM30= GENCODE_SM35= GENCODE_SM50= GENCODE_SM60= GENCODE_SM62=
export NVCC="$cuda_home/bin/nvcc"
for app_dir in BFS LIB LPS RAY; do
  make -C "$gpuapps_src/src/cuda/ispass-2009/$app_dir" -j"$jobs"
done
for app in ispass-2009-BFS ispass-2009-LIB ispass-2009-LPS ispass-2009-RAY; do
  install -m 0755 "$bin_root/release/$app" "$bin_root/gpuapps/$app"
done
VARIANT=MAX make -C "$gpuapps_src/src/cuda/pannotia/color" -j"$jobs"
VARIANT=BLOCK make -C "$gpuapps_src/src/cuda/pannotia/fw" -j"$jobs"
make -C "$gpuapps_src/src/cuda/pannotia/mis" -j"$jobs"
VARIANT=DEFAULT make -C "$gpuapps_src/src/cuda/pannotia/pagerank" -j"$jobs"

required_bins=(
  "$bin_root/mars/SimilarityScore"
  "$bin_root/shoc/FFT" "$bin_root/shoc/Sort" "$bin_root/shoc/GEMM" "$bin_root/shoc/Stencil2D" "$bin_root/shoc/Reduction"
  "$bin_root/gpuapps/ispass-2009-BFS" "$bin_root/gpuapps/ispass-2009-LIB" "$bin_root/gpuapps/ispass-2009-LPS" "$bin_root/gpuapps/ispass-2009-RAY"
  "$bin_root/gpuapps/color_max" "$bin_root/gpuapps/fw_block" "$bin_root/gpuapps/mis" "$bin_root/gpuapps/pagerank"
)
for binary in "${required_bins[@]}"; do
  [[ -x "$binary" ]] || { echo "error: expected binary missing: $binary" >&2; exit 1; }
done

{
  printf 'timestamp_utc=%s\n' "$(date -u +%FT%TZ)"
  printf 'cuda_home=%s\n' "$cuda_home"
  "$cuda_home/bin/nvcc" --version
  git -C "$shoc_src" rev-parse HEAD
  git -C "$gpuapps_src" rev-parse HEAD
  sha256sum "$mars_zip"
  sha256sum "${required_bins[@]}"
} > "$work_root/build-provenance.txt"
printf 'PASS binaries=%s provenance=%s\n' "${#required_bins[@]}" "$work_root/build-provenance.txt"
