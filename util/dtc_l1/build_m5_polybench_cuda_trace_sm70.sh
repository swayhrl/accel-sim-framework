#!/usr/bin/env bash
# Dedicated M5.0BT V100 trace-capture build.  It intentionally does not alter
# the sm_52 recovery build or its historical binary/PTX identities.
set -euo pipefail
[[ $# == 2 ]] || { echo "usage: $0 <polybench-source> <output-dir>" >&2; exit 2; }
src=$1 out=$2; nvcc=${NVCC:-/usr/local/cuda-11.8/bin/nvcc}
[[ -x $nvcc && -d $src/CUDA ]] || { echo 'FAIL missing CUDA 11.8 nvcc or PolyBench CUDA source' >&2; exit 2; }
"$nvcc" --version | grep -q 'release 11.8' || { echo 'FAIL requires CUDA 11.8' >&2; exit 2; }
mkdir -p "$out"
build() { "$nvcc" -arch=sm_70 -O2 -cudart shared -o "$out/$1" "$src/CUDA/$2"; }
build bicg BICG/bicg.cu; build atax ATAX/atax.cu; build gemver GEMVER/gemver.cu
build mvt MVT/mvt.cu; build syrk SYRK/syrk.cu; build gesummv GESUMMV/gesummv.cu
build syr2k SYR2K/syr2k.cu; build twomm 2MM/2mm.cu; build twodconv 2DCONV/2DConvolution.cu
