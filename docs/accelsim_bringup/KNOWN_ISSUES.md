# Known Issues

## Observed

- No NVIDIA GPU is visible in this environment. `nvidia-smi` is not found and `/dev/nvidia*` is absent, so A3 is `BLOCKED_NO_GPU`.
- `gpu-simulator/setup_environment.sh` assumes nounset is disabled. `scripts/accelsim/accelsim_env.sh` temporarily disables `set -u` while sourcing it.
- `get-accel-sim-traces.py` mishandles relative `--download_dir` during summary parsing. The bringup scripts pass an absolute download directory.
- `monitor_func_test.py` does not expose a run-directory argument and expects `sim_run_<cuda-version>`. The scripts create an ignored compatibility symlink when needed.
- Local procman jobs remained in `WAITING_TO_RUN` during A2. A2/A4 therefore use direct smoke mode: `run_simulations.py -n`, one generated `justrun.sh`, then `get_stats.py -r`.
- `accel-sim.out --help` returns nonzero with an unknown option message, but prints the Accel-Sim/GPGPU-Sim banner. This is recorded as a usable binary smoke, not a help-interface pass.
- The Make build warns that OpenCL support is not enabled. The SASS trace-driven smoke path did not require OpenCL.

## Future Risks

- NVBit version, CUDA toolkit, and driver compatibility may block A3 on GPU machines.
- Full Rodinia suite simulation can be much longer than the direct smoke used here.
- Trace-root layout must match Accel-Sim's expected `<bench>/<args>/traces/kernelslist.g` structure.
