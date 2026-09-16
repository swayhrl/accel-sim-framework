# Offline-Sim V1.0 release

Framework release line: `project/offline-sim`; nested GPGPU-Sim: `91880c53383d5a6a6742bfb1be2c5f34e39c7871` on `project/offline-sim`, unmodified. Qualification used CUDA 12.4.131, Bison 3.8.2, Flex 2.6.4, pybind11 2.13.6, GCC 11.4, CMake 3.22.1, and Python 3.10.

Core PASS: clean build; official QV100 BFS SASS; QV100-PTX BFS, Hotspot, Backprop, and Kmeans through local launcher, monitor, and stats; offline Python setup; fresh extraction doctor/setup/build/smoke/quick regression. Full commands and receipt locations are in `docs-local/reports/QUALIFICATION_SUMMARY.tsv`.

The release tar identity is external sidecars in `dist/accel-sim-offline-v1.0.tar.gz.sha256` and `.size`, not a self-referential Git report. The tar excludes every source `.git`; recovery uses selective release bundles. `V1_EXTENDED_PENDING`: broad Rodinia, GPU Microbenchmark, Hopper/TMA.
