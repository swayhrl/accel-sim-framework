# Build and run

```bash
cd <bundle-root>/accel-sim-framework
export OFFLINE_BUNDLE_ROOT="$(cd .. && pwd)"
make doctor
make setup
make build
make quick
```

The Makefile is the normal entry point. For manual use, the equivalent build path is `./offline/doctor.sh`, `./offline/setup.sh`, then `CUDA_INSTALL_PATH="$OFFLINE_BUNDLE_ROOT/toolchain/cuda-12.4" JOBS=4 ./offline/build.sh`.

Run direct SASS replay using an official `kernelslist.g` plus QV100 `gpgpusim.config` and `trace.config`. Use `offline/run-logged.sh <name> ...` for a 600-second receipt. PTX execution-driven runs use `run_simulations.py -l local -C QV100-PTX`; invoke monitor and stats on the same run name.
