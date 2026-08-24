# CUTLASS WMMA 1/40 replay plan

This is the initial tensor-core complement to the existing scalar PolyBench
`gemm` and Parboil `sgemm` replays.  It uses the existing trimmed trace:

`decoupled-l2-trace-fraction/cutlass-all-1of40-trim-v1/.../m_2560___n_64___k_2560.../traces/kernelslist.g`

The trace lists seven `WmmaGemmConfig` kernels.  All seven kernel files are
present (about 54 MiB total) and contain Volta `HMMA.884.F32.F32` instructions.
It is therefore a genuine tensor-core test, not a scalar GEMM relabeling.

## Ordered protocol

The runner is prepared but has not been invoked.  After approval, use the
following independently resumable stages; each records copied binary/config
hashes and host time/RSS in the standard replay directory.

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-addr-observe
scripts/run_c2p_cutlass_wmma_1of40.sh --out-root hw_run/c2p-cutlass-wmma-1of40-v1 \
  --stage smoke --build
scripts/run_c2p_cutlass_wmma_1of40.sh --out-root hw_run/c2p-cutlass-wmma-1of40-v1 \
  --stage core --skip-complete
scripts/run_c2p_cutlass_wmma_1of40.sh --out-root hw_run/c2p-cutlass-wmma-1of40-v1 \
  --stage classify --skip-complete
```

Only if `smoke` exits normally and `oracle` reports nonzero peer opportunity,
run the two C2P+ confirmation-policy points:

```bash
scripts/run_c2p_cutlass_wmma_1of40.sh --out-root hw_run/c2p-cutlass-wmma-1of40-v1 \
  --stage c2pplus-control --skip-complete
scripts/run_c2p_cutlass_wmma_1of40.sh --out-root hw_run/c2p-cutlass-wmma-1of40-v1 \
  --stage c2pplus-addr --skip-complete
```

The paired C2P+ control has the same four-probe cap and separate target tag
port as the address/topology policy.  Thus the policy comparison changes only
the confirmation decision, not the target-port topology or hard cap.

## Gates

- `baseline` and `oracle` must both terminate normally; their cycles must be
  identical because oracle only records opportunity.
- `c2p_remote_hits == c2p_l2_requests_avoided` for every sharing mechanism
  run.  `gpu_tot_sim_insn` is identical among replay modes of this trace.
- The 50-cycle point is solely for the local R/S classification.  It must not
  be substituted into the primary 200-cycle performance comparison.
- No ATA/CCD/RING run is scheduled here.  This initial test establishes that
  the tensor execution path and C2P baseline are trustworthy before spending
  time on broader comparisons.
