# Executed historical production-source checks

Core source: 1fc248aa89abefbd1b417f7f4053cd2bf56d7a1e in
`/workspace/worktrees/gpgpu-sim-ep-l2-m0a-m1-int`. Its tracked working tree was
clean before compiling. These historical tests do not qualify the new B16 model.

Dispatcher acquired Registry.build_lease('lane5', cpu=1, memory=4*1024**3)
and released that exact lease in finally. Executed sequentially:

```text
bash CORE/tests/ep_l2/run_payload_store.sh
bash CORE/tests/ep_l2/run_payload_banked.sh
bash CORE/tests/ep_l2/run_descriptor_mshr.sh
```

Each cwd/TMPDIR was its own directory below
`/workspace/results/ep_l2_ft20261016/validation_r1/`.
Explicit environment: CUDA_INSTALL_PATH=/usr/local/cuda-11.8,
GPGPUSIM_ROOT=CORE, OMP_NUM_THREADS=1, MAKEFLAGS=-j1; scripts source that frozen
Core's setup_environment and use g++ with -std=c++11 -O2, function/data sections
and linker gc-sections. Outputs are private test executables, not production
accel-sim.out. Logs, return codes, elapsed time and content hashes are in
HISTORICAL_DIRECTED.json and RAW_LOG_INDEX.csv. All three return codes are 0.
