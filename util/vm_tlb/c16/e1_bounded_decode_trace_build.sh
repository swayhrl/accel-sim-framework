#!/usr/bin/env bash
set -euo pipefail
export PATH=/usr/local/cuda-12.8/bin:$PATH
repo=/home/huangrulin/workspace/worktrees/accel-sim-c16-e1-bounded-decode-trace-109-v1
src="$repo/util/tracer_nvbit/q05_prefix_route_b_v1"
nvbit=/data/c16/env/nvbit-1.7.7.1/core
out=/data/c16/e1_bounded_decode_trace_v1/bin
mkdir -p "$out"
cd "$src"
nvcc -dc -c -std=c++17 -I"$nvbit" -Xptxas -cloning=no -Xcompiler -Wall -arch=sm_89 -O3 -Xcompiler -fPIC route_b_tracer.cu -o "$out/route_b_trace.o"
nvcc -I"$nvbit" -Xptxas -astoolspatch --keep-device-functions -arch=sm_89 -Xcompiler -Wall -Xcompiler -fPIC -c accelsim_instrument_inst.cu -o "$out/route_b_inject.o"
nvcc -arch=sm_89 -O3 "$out/route_b_trace.o" "$out/route_b_inject.o" -L"$nvbit" -lnvbit -L/usr/local/cuda-12.8/lib64 -lcuda -lcudart_static -shared -o "$out/route_b_bounded_decode.so"
sha256sum "$out/route_b_bounded_decode.so" "$src/route_b_tracer.cu" "$src/route_b_raw_formatter.hpp" "$src/accelsim_instrument_inst.cu" > "$out/SHA256SUMS"
cat "$out/SHA256SUMS"
