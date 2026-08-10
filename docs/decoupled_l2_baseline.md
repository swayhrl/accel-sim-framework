# Decoupled-L2 native Accel-Sim baseline

This branch intentionally uses one external GPGPU-Sim worktree.  Accel-Sim is
the trace/workload harness; the C++ L2 backend is built in that worktree.

## Pinned starting point

| Component | Remote branch | Commit |
|---|---|---|
| Accel-Sim framework | `upstream/dev` | `3016c658f810bdae9a14bf4534ee99e9945eedae` |
| GPGPU-Sim distribution | `origin/dev` | `73774727e25fadf89df6f30ef5cf014091115db7` |

The two repositories are separate worktrees and have separate branches.  Do
not edit this repository's ignored `gpu-simulator/gpgpu-sim` checkout for this
experiment.

## One-root setup

```bash
export CUDA_INSTALL_PATH=/usr/local/cuda-11.8
export DECOUPLED_L2_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-decoupled-l2
source scripts/setup_decoupled_l2_env.sh release
make -C gpu-simulator -j"$(nproc)"
```

The setup script rejects a conflicting `GPGPUSIM_ROOT`, sources the selected
core first, then sources Accel-Sim.  Thus the executable and the backend
always use the same core checkout.

## Native smoke record

Before any backend change, the following completed on 2026-08-10:

- trace: Rodinia 2.0-ft `lud`, argument `_v__b__i___data_64_dat`;
- config: the existing QV100-SASS generated `gpgpusim.config`;
- result: `GPGPU-Sim: *** exit detected ***`;
- final totals: `gpu_tot_sim_cycle = 136216`,
  `gpu_tot_sim_insn = 420900`.

The trace is an external input, not committed here.  To rerun, place its
directory at `traces/` in a disposable run directory, copy the matching
`gpgpusim.config` and its `.xml`/`.icnt` files there, then run:

```bash
"$ACCELSIM_ROOT/gpu-simulator/bin/release/accel-sim.out" \
  -config ./gpgpusim.config -trace ./traces/kernelslist.g
```

Subsequent decoupled-L2 smoke runs use this same command and record backend
configuration alongside their results; their timing is not expected to match
this native-baseline value.
