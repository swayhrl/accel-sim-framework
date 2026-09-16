# Offline-Sim V1.0 release

Framework release line: `project/offline-sim`; nested GPGPU-Sim: `91880c53383d5a6a6742bfb1be2c5f34e39c7871` on `project/offline-sim`, unmodified. Qualification used CUDA 12.4.131, Bison 3.8.2, Flex 2.6.4, pybind11 2.13.6, GCC 11.4, CMake 3.22.1, and Python 3.10.

Current fresh release gate: doctor PASS; setup PASS; clean build PASS; official QV100 BFS SASS PASS; tiny BFS QV100-PTX child execution PASS; get_stats PASS. `monitor_func_test.py` is a KNOWN_LIMITATION for local procman output-name matching. Four PTX examples remain pre-release development qualification evidence, not a claim that all passed monitor.

The release tar identity is external sidecars in `dist/accel-sim-offline-v1.0.tar.gz.sha256` and `.size`, not a self-referential Git report. The tar excludes every source `.git`; recovery uses selective release bundles. `V1_EXTENDED_PENDING`: broad Rodinia, GPU Microbenchmark, Hopper/TMA.
