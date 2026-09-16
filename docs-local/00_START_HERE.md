# Accel-Sim Offline-Sim V1

Start with `offline/doctor.sh`, then `offline/setup.sh`. Set an already-installed CUDA toolkit in `CUDA_INSTALL_PATH`, source `offline/env.sh`, and invoke `offline/build.sh`. The normal paths are SASS trace-driven replay and PTX execution-driven simulation; neither offline script downloads assets.


## Quick command entry

The root `Makefile` is the preferred command entry. Start with:

```bash
cd <bundle-root>/accel-sim-framework
export OFFLINE_BUNDLE_ROOT="$(cd .. && pwd)"
make doctor
make setup
make build
make quick
```

Detailed commands are in `docs-local/06_COMMANDS.md`; build/config/rebuild rules are in `docs-local/07_BUILD_CONFIG_AND_REBUILD.md`; the code map is `docs-local/02_ARCHITECTURE_AND_CODE_MAP.md`. Low-level scripts remain available for advanced/manual use.
Framework and `gpu-simulator/gpgpu-sim` are independent Git repositories. This V1 bundle preserves the simulator architecture and does not carry historic Cache/L2/TLB/AI patches.
