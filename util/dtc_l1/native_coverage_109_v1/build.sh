#!/usr/bin/env bash
# Exact commands used before measurement; do not replace sealed measured binaries.
set -euo pipefail
REPO=$(cd "$(dirname "$0")/../../.." && pwd)
ROOT=${DTC_NATIVE_ROOT:-/data/c16/dtc_native_coverage_109_v1}
SRC=$ROOT/assets/parboil
BUILD=$ROOT/assets/spmv_build
if [[ -f "$ROOT/raw/NATIVE_CAMPAIGN_COMPLETE" ]]; then
  echo 'Sealed campaign exists; use a fresh DTC_NATIVE_ROOT to reproduce builds.' >&2
  exit 2
fi
mkdir -p "$ROOT/assets" "$ROOT/bin" "$ROOT/raw"
if [[ ! -d "$SRC/.git" ]]; then
  git clone --filter=blob:none --no-checkout https://github.com/palmer-dabbelt/parboil.git "$SRC"
  git -C "$SRC" sparse-checkout init --cone
  git -C "$SRC" sparse-checkout set benchmarks/spmv datasets/spmv common
  git -C "$SRC" checkout --detach 4e0fc54866546efa44fe93af57c9cef62f6c8eb9
fi
[[ $(git -C "$SRC" rev-parse HEAD) == 4e0fc54866546efa44fe93af57c9cef62f6c8eb9 ]]
export DTC_NATIVE_ROOT=$ROOT
python3 "$REPO/util/dtc_l1/native_coverage_109_v1/prepare_spmv.py"
for NAME in convert_dataset mmio; do
  gcc -O3 -I"$SRC/benchmarks/spmv/common_src/convert-dataset" -c "$SRC/benchmarks/spmv/common_src/convert-dataset/$NAME.c" -o "$BUILD/$NAME.o"
done
gcc -O3 -I"$SRC/common/include" -c "$SRC/common/src/parboil.c" -o "$BUILD/parboil.o"
NVCC=/usr/local/cuda-12.8/bin/nvcc
"$NVCC" -O3 -lineinfo -arch=sm_89 --use_fast_math -I"$SRC/common/include" -I"$SRC/benchmarks/spmv/common_src/convert-dataset" "$BUILD/main.cu" "$BUILD/file.cc" "$BUILD/gpu_info.cc" "$BUILD/convert_dataset.o" "$BUILD/mmio.o" "$BUILD/parboil.o" -o "$ROOT/bin/spmv"
"$NVCC" -std=c++17 -O3 -lineinfo -arch=sm_89 -Xptxas=-v "$REPO/util/dtc_l1/native_coverage_109_v1/diagnostic.cu" -o "$ROOT/bin/diagnostic"
for NAME in spmv diagnostic; do /usr/local/cuda-12.8/bin/cuobjdump --dump-sass "$ROOT/bin/$NAME" > "$ROOT/raw/$NAME.sass"; done
sha256sum "$ROOT/bin/spmv" "$ROOT/bin/diagnostic"
