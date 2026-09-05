#!/usr/bin/env bash
# Dedicated M5.0BT V100 trace-capture build; recovery sm_52 artifacts remain immutable history.
set -euo pipefail
[[ $# == 3 ]] || { echo "usage: $0 <wrapper> <parboil> <output-dir>" >&2; exit 2; }
wrapper=$1; parboil=$2; out=$3; nvcc=${NVCC:-/usr/local/cuda-11.8/bin/nvcc}; cc=${CC:-gcc}; cxx=${CXX:-g++}
[[ -x $nvcc ]] || { echo 'FAIL CUDA 11.8 nvcc unavailable' >&2; exit 2; }; "$nvcc" --version | grep -q 'release 11.8' || { echo 'FAIL requires CUDA 11.8' >&2; exit 2; }
for f in "$wrapper"/{main.cu,jds_kernels.cu,gpu_info.cc,file.cc,convert_dataset.c,mmio.c} "$parboil"/common/{src/parboil_cuda.c,include/parboil.h}; do [[ -f $f ]] || { echo "FAIL missing $f" >&2; exit 2; }; done
mkdir -p "$out"; inc=("-I$parboil/common/include" "-I/usr/local/cuda-11.8/include" "-I$wrapper")
"$nvcc" -O2 -arch=sm_70 "${inc[@]}" -c "$wrapper/main.cu" -o "$out/main.o"
"$cxx" -O2 "${inc[@]}" -c "$wrapper/file.cc" -o "$out/file.o"; "$cc" -O2 "${inc[@]}" -c "$wrapper/gpu_info.cc" -o "$out/gpu_info.o"
"$nvcc" -O2 -arch=sm_70 "${inc[@]}" -c "$parboil/common/src/parboil_cuda.c" -o "$out/parboil_cuda.o"; "$cc" -O2 "${inc[@]}" -c "$wrapper/convert_dataset.c" -o "$out/convert_dataset.o"; "$cc" -O2 "${inc[@]}" -c "$wrapper/mmio.c" -o "$out/mmio.o"
"$nvcc" -arch=sm_70 -cudart shared "$out"/{main,file,gpu_info,parboil_cuda,convert_dataset,mmio}.o -o "$out/spmv" -lm -lstdc++
