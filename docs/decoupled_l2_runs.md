# Decoupled-L2 smoke runs

The experimental L2 is in the external GPGPU-Sim worktree; this repository
only provides the environment guard and trace runner.  Use a generated
Accel-Sim config whose neighbouring XML/interconnect files match the trace.

```bash
export CUDA_INSTALL_PATH=/usr/local/cuda-11.8
export DECOUPLED_L2_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-decoupled-l2

scripts/run_decoupled_l2_smoke.sh --build \
  --backend decoupled \
  --trace /path/to/traces/kernelslist.g \
  --config /path/to/QV100-SASS/gpgpusim.config
```

The runner creates a disposable directory, copies only configuration assets,
symlinks the input trace, appends the backend selection, and requires the
normal `*** exit detected ***` marker.  It also requires decoupled statistics
when the selected backend is `fixed` or `decoupled`.

## Backend modes

- `baseline`: existing GPGPU-Sim `l2_cache`, unchanged default.
- `fixed`: accepts each request and returns it after
  `-gpgpu_decoupled_l2_fixed_latency`; no tag allocation or lower traffic.
- `decoupled`: token table, tag queue, full-line AAD/OTF merge, dirty metadata,
  WBQ, abstract bank arbitration, and lower-read/write requests.

## Statistics and assertions

Each memory sub-partition emits a `decoupled_l2[...]` line at normal simulator
state reporting.  The useful counters are:

| Field | Meaning |
|---|---|
| `access`, `hit`, `miss` | model admissions and tag outcomes |
| `aad_merge`, `otf` | same-line requests merged and lower reads issued |
| `write`, `wb` | dirty writes accepted and eviction writebacks issued |
| `atomic` | atomic requests completed through GPGPU-Sim's normal callback |
| `token_stall`, `aad_stall`, `bank_stall` | finite-resource backpressure |
| `banks` | per-bank abstract operation counts |

Debug assertions check token ownership, one AAD chain per line, one token per
AAD chain, and the correspondence between an issued lower read and its OTF
record.  A failing assertion invalidates the run.

## Minimum validation matrix

1. Run `baseline` on a trace and compare its final cycle count with the pinned
   native baseline when using the same generated config.
2. Run `fixed`; require clean exit and zero `otf`/`wb` counters.
3. Run `decoupled`; require clean exit and nonzero OTF/AAD counters on a
   memory-bearing trace.
4. For WBQ coverage, append a one-line L2 config such as
   `-gpgpu_cache:dl2 S:1:128:1,L:B:m:L:P,A:192:4,32:0,32`; require nonzero
   `wb` and an empty final `wbq`.

This is an experiment model, so cycle counts are not expected to equal the
baseline.  Functional atomic effects are still applied by
`memory_sub_partition::pop()` and are intentionally not reimplemented here.

## Executed validation record (2026-08-10)

All runs used the pinned QV100-SASS generated configuration and external
Rodinia 2.0-ft pretraces.  They were executed through
`run_decoupled_l2_smoke.sh` after rebuilding the external core worktree.

| Case | Backend/config | Result |
|---|---|---|
| Native preservation | LUD, `baseline` | clean exit; final total `136216` cycles, matching the pinned baseline |
| Empty pipeline | LUD, `fixed` | clean exit; nonzero accesses, zero OTF and WBQ writebacks |
| Core decoupling | LUD, `decoupled` | clean exit; nonzero AAD merge, OTF, writes, and bank stalls |
| Dirty eviction | LUD, `decoupled` with one L2 line | clean exit; nonzero `wb`, final `wbq=0` |
| Development workload | Hotspot, `decoupled` | clean exit; nonzero AAD merge, OTF, and bank usage |
