#!/bin/bash
set -euo pipefail
/usr/local/cuda-12.6/bin/nvcc --cubin -arch=sm_89 --threads 4 tools/ai_workload_research/a16r1_greencontext_canary/tiny_kernel.cu -o "$TASK_DATA/build/tiny_kernel.cubin"
g++ -std=c++17 -O0 -I/usr/local/cuda-12.6/include tools/ai_workload_research/a16r1_greencontext_canary/driver_probe.cpp -L/usr/lib/x86_64-linux-gnu -lcuda -o "$TASK_DATA/build/driver_probe"
