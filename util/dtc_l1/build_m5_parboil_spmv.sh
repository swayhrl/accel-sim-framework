#!/usr/bin/env bash
# Rebuild the source-equivalent CUDA SpMV wrapper used by the DTC-L1 M5
# campaign.  Both roots are explicit so their commits can be recorded rather
# than importing a benchmark tree into the framework repository.
set -euo pipefail

if [[ $# -ne 3 ]]; then
  echo "usage: $0 <spmv-wrapper-source-dir> <parboil-source-root> <output-directory>" >&2
  exit 2
fi

wrapper_dir=$1
parboil_root=$2
output_dir=$3
nvcc=${NVCC:-/usr/local/cuda-11.8/bin/nvcc}
cc=${CC:-gcc}
cxx=${CXX:-g++}

for file in "$wrapper_dir/main.cu" "$wrapper_dir/jds_kernels.cu" \
            "$wrapper_dir/gpu_info.cc" "$wrapper_dir/file.cc" \
            "$wrapper_dir/convert_dataset.c" "$wrapper_dir/mmio.c" \
            "$parboil_root/common/src/parboil_cuda.c" \
            "$parboil_root/common/include/parboil.h"; do
  if [[ ! -f $file ]]; then
    echo "required source is missing: $file" >&2
    exit 2
  fi
done

mkdir -p "$output_dir"
includes=("-I$parboil_root/common/include" "-I/usr/local/cuda-11.8/include" "-I$wrapper_dir")

"$nvcc" -O2 -arch=sm_52 "${includes[@]}" -c "$wrapper_dir/main.cu" -o "$output_dir/main.o"
"$cxx" -O2 "${includes[@]}" -c "$wrapper_dir/file.cc" -o "$output_dir/file.o"
"$cc" -O2 "${includes[@]}" -c "$wrapper_dir/gpu_info.cc" -o "$output_dir/gpu_info.o"
"$nvcc" -O2 -arch=sm_52 "${includes[@]}" -c "$parboil_root/common/src/parboil_cuda.c" -o "$output_dir/parboil_cuda.o"
"$cc" -O2 "${includes[@]}" -c "$wrapper_dir/convert_dataset.c" -o "$output_dir/convert_dataset.o"
"$cc" -O2 "${includes[@]}" -c "$wrapper_dir/mmio.c" -o "$output_dir/mmio.o"
"$nvcc" -cudart shared "$output_dir"/{main,file,gpu_info,parboil_cuda,convert_dataset,mmio}.o -o "$output_dir/spmv" -lm -lstdc++
"$nvcc" -arch=sm_52 -O2 "${includes[@]}" -ptx -o "$output_dir/spmv.1.sm_52.ptx" "$wrapper_dir/main.cu"
