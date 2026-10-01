# R20R1 execution contract and source/runtime commands

All work ran on node109. Pinned runtime and scene were reused read-only from `/data/c16/awma/r20_active_world_native_v1`; new raw/cache/tmp were isolated under `/data/c16/awma/r20r1_solver_entry_local_contract_20261001`. MuJoCo Warp source stayed at `3d537ea6b45eb88ce2ebeb97c57b8e9a220eb1c5`, with the original solver blob `090061796792f4d11408eaa69b4ef3c44465c705`. Every CUDA initialization/JIT/capture/replay was invoked in a single process that held `/data/c16/locks/c16_gpu_campaign.lock` until exit. Scripts assert `R20R1_GPU_LOCK_HELD=1`.

The exact GPU launcher prefix was:

```sh
flock -x -w 3600 /data/c16/locks/c16_gpu_campaign.lock env R20R1_GPU_LOCK_HELD=1 PYTHONPATH=/data/c16/awma/r20_active_world_native_v1/source/mujoco_warp TMPDIR=/data/c16/awma/r20r1_solver_entry_local_contract_20261001/tmp PYTHONUNBUFFERED=1 /data/c16/awma/r20_active_world_native_v1/env/bin/python
```

Each invocation appended one of these script arguments from the R20R1 execution worktree's `util/vm_tlb/awma/r20r1_solver_entry/`, redirecting stdout/stderr to the same-named node109 `raw/*.log` retained on node164:

```text
capture_t128_solver_entry.py         original full-step graph plus real pre/post solver GPU snapshots
b0_repeatability_t128.py             two wrapper-error runs without B0 samples, then five B0 + one fresh-graph run
context_residual_audit.py            initial three B0 context probes, then one source-relation/raw-array completion
capture_discovery_entrances.py       one new continuous original B0 t128..152 lineage, all four predeclared entries
qualify_four_entries.py              one t128-only receipt-serialization attempt with raw preserved, then four-entry B0 qualification
```

Parent `DISCOVERY_ENTRY_FULL_DATA.npz` SHA256 was checked before each lineage capture. `LOCAL_NUMERICAL_CONTRACT.md` hash `456ca1fa3cbca9aa8d4a6c1cae14ea85a176f23660c9d0c8754a141eb70af66d` was fixed before the new continuous lineage or any candidate. CPU-only analyzers/negative controls used the same isolated R20 Python environment; they did not create CUDA contexts. The t152 stop-bit diagnosis was offline over already saved B0 arrays. There was no S1 implementation, formal timing, NSYS, NCU or holdout command.
