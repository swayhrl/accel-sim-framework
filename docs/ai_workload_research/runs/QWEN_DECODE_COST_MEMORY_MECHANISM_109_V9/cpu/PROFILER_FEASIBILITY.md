# CPU-only profiler feasibility

Installed help and official local documentation verified. No GPU lock, CUDA/NVML initialization, metric query, profiling, installation or model execution occurred. Runtime CUDA13 compatibility remains untested.

- NCU 2025.1.1 wrapper: `/opt/nvidia/nsight-compute/2025.1.1/ncu`; real ELF: `target/linux-desktop-glibc_2_11_3-x64/ncu`. Secondary 2024.3.2 installed.
- NSYS 2024.6.2: `/usr/local/bin/nsys` points at `/opt/nvidia/nsight-systems/2024.6.2/target-linux-x64/nsys`. `/usr/local/bin/nsys2024.6.2` does not exist. Secondary 2024.5.1 installed.
- Native CURVE first. Use independent warmed real BF16 compiled PROFILER workers for NSYS and NCU. Keep B1/B2 output32 plus output1 numerical controls. Output1 may legitimately have no decode graph. Never merge profiler time into native formal timing.
- NCU: `--graph-profiling node --replay-mode kernel --nvtx --nvtx-include 'decodeGraph/' --launch-count 1 --kill no --clock-control none --cache-control none`, with one owner-observed dense-kernel regex and a small owner-queried explicit metric list. Do not use set full.
- Push/pop single NVTX range requires trailing slash. `--profile-from-start no` also requires worker cudaProfilerStart/Stop. An NVTX-only worker should use yes. launch-count and launch-skip count matching kernels only.
- Metric categories only: node-local DRAM read/write sum, L2 traffic/hits, SM/tensor pipe activity, occupancy and duration. Legal names and pass count remain owner responsibility under the GPU lock.
- NSYS: `--trace=cuda,nvtx --capture-range=cudaProfilerApi --capture-range-end=stop --cuda-graph-trace=node --sample=none --python-sampling=false --cpuctxsw=none --gpu-metrics-devices=none --kill=none`. CPU sampling uses none, not false. NVTX-capture alternative needs `--capture-range=nvtx --nvtx-capture=decodeGraph`; unregistered strings require `NSYS_NVTX_PROFILER_REGISTER_ONLY=0`.
- Node replay still backs up memory and serializes kernels. Disabling flushing does not restore caches across passes. Selected-node traffic is not whole-graph traffic. Both profiler versions predate CUDA13; a profiler failure must not invalidate native numerical evidence.

JSON contains full help/version receipts, official local source hashes, unexecuted argv templates, required owner substitutions and interpretation limits.
