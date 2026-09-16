# Offline-Sim V1 command quick reference

Prefer the root Makefile entry point:

```bash
cd <bundle-root>/accel-sim-framework
make doctor
make setup
make build
make smoke-sass
make quick
make receipts
```

After simulator architecture changes, use `make rebuild JOBS=8`. Launch PTX with `make ptx` or `make ptx BENCH=rodinia_2.0-ft:bfs-rodinia-2.0-ft CONFIG=QV100-PTX NAME=my-ptx`. Run a SASS trace with `make sass TRACE=/path/to/kernelslist.g`; override `GPU_CONFIG` and `TRACE_CONFIG` when needed. Collect results with `make stats NAME=my-ptx`.

Release commands are `make package` and `make verify-package`. Packaging is intentionally restricted to the formal release branch/tag state. Advanced upstream tools remain in `util/job_launching/`: `run_simulations.py`, `get_stats.py`, `monitor_func_test.py`, and `job_status.py`; see its `README.md`. `monitor_func_test.py` remains available, but local-procman output-name matching is a known V1 limitation.

Useful locations: simulator binary `gpu-simulator/bin/release/accel-sim.out`; QV100 configs under `gpu-simulator/gpgpu-sim/configs/tested-cfgs/SM7_QV100/` and `gpu-simulator/configs/tested-cfgs/SM7_QV100/`; GPU App binaries under `../cache/apps/gpu-app-collection/bin/12.4/release/`; official SASS asset under `../cache/assets/official/`; logs under `../logs/`; and local documentation under `docs-local/`.
