#!/usr/bin/env bash
set -euo pipefail
root=/data/c16/awma/r101_transient_l2_sim_capture_20260927
worktree=/home/huangrulin/workspace/worktrees/accel-sim-awma-r101-transient-l2-sim-capture-109-v1
src="$worktree/util/tracer_nvbit/route_b_1771"
nvbit=/data/c16/env/nvbit-1.7.7.1/core
nvcc=/usr/local/cuda-12.8/bin/nvcc
mkdir -p "$root/bin" "$root/build" "$root/logs" "$root/raw" "$root/cache" "$root/tmp"
exec 9>/data/c16/locks/c16_gpu_campaign.lock
flock -x 9
cd "$src"
"$nvcc" -dc -c -std=c++17 -I"$nvbit" -Xptxas -cloning=no \
    -Xcompiler -Wall -arch=sm_89 -O3 -Xcompiler -fPIC \
    route_b_tracer.cu -o "$root/build/route_b_multi.o"
"$nvcc" -I"$nvbit" -Xptxas -astoolspatch --keep-device-functions \
    -arch=sm_89 -Xcompiler -Wall -Xcompiler -fPIC -c \
    accelsim_instrument_inst.cu -o "$root/build/inject.o"
"$nvcc" -arch=sm_89 -O3 "$root/build/route_b_multi.o" "$root/build/inject.o" \
    -L"$nvbit" -lnvbit -L/usr/local/cuda-12.8/lib64 -lcuda -lcudart_static \
    -shared -o "$root/bin/route_b_r101_multi.so"
"$nvcc" -std=c++17 -I"$src" -arch=sm_89 -O2 \
    route_b_formatter_selftest.cc -o "$root/bin/route_b_formatter_selftest"
"$root/bin/route_b_formatter_selftest" > "$root/logs/formatter_selftest.stdout.log"
sha256sum "$src/route_b_tracer.cu" "$src/route_b_raw_formatter.hpp" \
    "$src/accelsim_instrument_inst.cu" "$root/bin/route_b_r101_multi.so" \
    "$root/bin/route_b_formatter_selftest" \
    /data/c16/awma/storage_sidelane_v1/producer_5143/bin/post-traces-processing_5143 \
    /data/c16/awma/simcompat-v2/q05_routeb_basedelta_canary_20260916T154104Z/hotfix_fb5d0b_admission/traceg_grammar_smoke_fb5d0b \
    > "$root/build/PRODUCER_SHA256SUMS"
cat "$root/logs/formatter_selftest.stdout.log"
