# Build and run

```bash
export OFFLINE_BUNDLE_ROOT=<bundle-root>
./offline/doctor.sh
./offline/setup.sh
CUDA_INSTALL_PATH="$OFFLINE_BUNDLE_ROOT/toolchain/cuda-12.4" JOBS=1 ./offline/build.sh
```

Run direct SASS replay using an official `kernelslist.g` plus QV100 `gpgpusim.config` and `trace.config`. Use `offline/run-logged.sh <name> ...` for a 600-second receipt. PTX execution-driven runs use `run_simulations.py -l local -C QV100-PTX`; invoke monitor and stats on the same run name.
