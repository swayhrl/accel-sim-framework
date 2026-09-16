#!/usr/bin/env bash
set -euo pipefail
export PATH=/usr/local/cuda-12.8/bin:$PATH
root=/home/huangrulin/workspace/worktrees/accel-sim-awma-terminal-v2
src="$root/util/tracer_nvbit/route_b_1771"
nvbit=/data/c16/env/nvbit-1.7.7.1/core
out=/data/c16/awma/simcompat-v2/route_b/bin
mkdir -p "$out"
cd "$src"
nvcc -dc -c -std=c++17 -I"$nvbit" -Xptxas -cloning=no -Xcompiler -Wall -arch=sm_89 -O3 -Xcompiler -fPIC route_b_tracer.cu -o route_b_live.o
nvcc -I"$nvbit" -Xptxas -astoolspatch --keep-device-functions -arch=sm_89 -Xcompiler -Wall -Xcompiler -fPIC -c accelsim_instrument_inst.cu -o route_b_live_inject.o
nvcc -arch=sm_89 -O3 route_b_live.o route_b_live_inject.o -L"$nvbit" -lnvbit -L/usr/local/cuda-12.8/lib64 -lcuda -lcudart_static -shared -o "$out/route_b_live_raw.so"
nvcc -std=c++17 -I"$src" -arch=sm_89 -O2 route_b_formatter_selftest.cc -o "$out/route_b_formatter_selftest"
sha256sum "$out/route_b_live_raw.so" "$out/route_b_formatter_selftest" "$src/route_b_tracer.cu" "$src/route_b_raw_formatter.hpp"
