#!/usr/bin/env bash
# Rebuild the canonical PolyBench/GPU CUDA executables and matching PTX used by
# the DTC-L1 M5 compute campaign.  The source root is intentionally explicit:
# provenance is recorded in the M5 workload manifest, rather than vendoring a
# second benchmark suite into this repository.
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "usage: $0 <polybench-gpu-source-root> <output-directory>" >&2
  exit 2
fi

source_root=$1
output_dir=$2
nvcc=${NVCC:-/usr/local/cuda-11.8/bin/nvcc}

if [[ ! -x $nvcc ]]; then
  echo "nvcc is not executable: $nvcc" >&2
  exit 2
fi
if [[ ! -d $source_root/CUDA ]]; then
  echo "not a PolyBench/GPU CUDA source root: $source_root" >&2
  exit 2
fi

mkdir -p "$output_dir"

build_one() {
  local name=$1
  local source=$2
  "$nvcc" -arch=sm_52 -O2 -cudart shared -o "$output_dir/$name" "$source_root/CUDA/$source"
  "$nvcc" -arch=sm_52 -O2 -ptx -o "$output_dir/$name.1.sm_52.ptx" "$source_root/CUDA/$source"
}

build_one bicg BICG/bicg.cu
build_one atax ATAX/atax.cu
build_one gemver GEMVER/gemver.cu
build_one mvt MVT/mvt.cu
build_one syrk SYRK/syrk.cu
build_one gesummv GESUMMV/gesummv.cu
build_one syr2k SYR2K/syr2k.cu
build_one twomm 2MM/2mm.cu
build_one twodconv 2DCONV/2DConvolution.cu
