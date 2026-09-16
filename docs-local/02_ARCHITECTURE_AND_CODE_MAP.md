# Architecture and code map

Framework orchestrates traces and jobs; nested GPGPU-Sim is a distinct repository implementing model behavior. SASS uses `trace-driven/`, `trace-parser/`, `util/tracer_nvbit/`, and `util/job_launching/`. PTX uses `gpgpu-sim/src/cuda-sim/`, `libcuda/`, and the same launcher. Timing flows shader (`src/gpgpu-sim/shader.cc`) to L1/cache (`gpu-cache.cc`), interconnect (`src/intersim2/`), L2 (`l2cache.cc`), DRAM (`dram.cc`), then response. Do not modify these paths for offline packaging.
