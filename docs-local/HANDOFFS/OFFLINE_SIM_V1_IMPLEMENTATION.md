# Offline-Sim V1 implementation handoff

## Status

`BLOCKED_CUDA_TOOLKIT_AND_SYSTEM_DEPS`

The host is Ubuntu 22.04.5 amd64 with GCC/G++ 11.4, CMake 3.22, Make 4.3, Python 3.10 and Git 2.34. Bison and Flex are absent. No CUDA toolkit was discoverable under standard `/usr/local/cuda*` paths, so a real simulator build and CUDA-dependent SASS/PTX regressions cannot be honestly run. No simulator architecture source was modified.

## Exact sources and dependencies

| item | identity | cache / SHA |
|---|---|---|
| Framework | `task/offline-sim/bootstrap-v1` from `d930ad6d02c09bb56867132583735aba0389cff4` | Framework Git |
| GPGPU-Sim | `swayhrl/gpgpu-sim:project/offline-sim` at `91880c53383d5a6a6742bfb1be2c5f34e39c7871` | nested Git, unmodified |
| GPU App Collection | `accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1` | `cache/git/gpu-app-collection.git` |
| pybind11 | `v2.13.6` | `cache/sources/pybind11-v2.13.6.tar.gz`, `e08cb87f4773da97fa7b5f035de8763abc656d87d5773e62f6da0587d1f0ec20` |

## Offline infrastructure

`offline/{doctor,env,setup,build,smoke,regression,package}.sh` and `offline/manifest.lock` are implemented. They deny implicit network, verify vendor inputs, select an existing CUDA through `CUDA_INSTALL_PATH`, and separate package assets from Git. `docs-local/reports/ENVIRONMENT.{json,md}` and `NETWORK_CALLS.tsv` are generated reports; `NETWORK_AUDIT.md` is the policy audit.

## Test matrix

| test | result | reason |
|---|---|---|
| vendor/setup/doctor | PASS | pybind11 hash and environment report generated |
| tiny real SASS smoke | BLOCKED | CUDA toolkit and trace asset absent |
| QV100-SASS + rodinia_2.0-ft | BLOCKED | CUDA/toolchain and cached assets absent |
| GPU App Collection rodinia_2.0-ft | PREPARED | mirror commit cached; build needs CUDA/toolchain |
| GPU_Microbenchmark | BLOCKED | CUDA/toolchain absent |
| QV100-PTX | BLOCKED | CUDA/toolchain absent |
| run_simulations.py -l local / monitor_func_test.py / get_stats.py | PREPARED | require an actual completed local simulation |

## CUDA matrix

CUDA 11.5, any discovered alternate CUDA, and upstream-recommended CUDA are deliberately undecided: no installed toolkit exists. On a target with toolkits, run `offline/build.sh` once per `CUDA_INSTALL_PATH` followed by `offline/smoke.sh` and `offline/regression.sh`; record results without altering system CUDA.

## Assets / next steps

No large binary benchmark asset was committed. Cache location is `/root/workspace/offline-sim-v1/cache/assets/`; future HTTPS downloads must record URL, license, size and SHA256 there. Install/carry Ubuntu dependencies from `OFFLINE_SYSTEM_DEPS_UBUNTU22.04_AMD64.md`, select a compatible installed CUDA toolkit, acquire official QV100 trace and GPU-App-Collection assets into cache, then execute the listed regression matrix. Use Git bundles/patches for offline updates.
