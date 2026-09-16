# Build, runtime configuration, and rebuild rules

Three independent things are often confused: the Release simulator binary, a benchmark/application binary, and runtime architecture configuration. The current qualified framework is `721eb62aefd548b2fbe37c29e4cdf719806dfab0`; nested GPGPU-Sim is `91880c53383d5a6a6742bfb1be2c5f34e39c7871`. Qualification used CUDA 12.4.131, GCC 11.4, CMake 3.22.1, Bison 3.8.2, Flex 2.6.4, pybind11 2.13.6, and Python 3.10.

`accel-sim.out` is not QV100-specific. QV100-SASS uses `SM7_QV100/gpgpusim.config` plus `SM7_QV100/trace.config`; QV100-PTX uses the same GPGPU config with the PTX execution-driven frontend. Official `define-standard-cfgs.yml` also names QV100, A100, H100, H200, RTX3070, and others; these are not all V1-qualified.

| Change | Rebuild simulator | Rebuild app | Re-capture SASS trace |
|---|---|---|---|
| gpgpusim.config only | No | No | No |
| trace.config only | No | No | No |
| simulator C/C++ architecture | Yes | No | No |
| benchmark CUDA source | No* | Yes | Yes, for changed SASS workload |
| benchmark input only | No | No | Usually no |
| app CUDA compile flags | No | Yes | Yes for SASS |

*No simulator rebuild is needed when the benchmark change does not touch simulator sources. For examples: change L1 128KB to 256KB or scheduler LRR to GTO in config without rebuilding; add a cache policy or TLB implementation in C++ and run `make rebuild`; change a CUDA kernel and rebuild the app plus retrace its SASS workload. Configuration files live under `gpu-simulator/gpgpu-sim/configs/tested-cfgs/`, `gpu-simulator/configs/tested-cfgs/`, and `util/job_launching/configs/define-standard-cfgs.yml`. See `docs-local/02_ARCHITECTURE_AND_CODE_MAP.md` for source structure.
