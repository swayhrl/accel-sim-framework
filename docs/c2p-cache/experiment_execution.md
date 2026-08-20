# C2P experiment execution

Run every reported case as a four-mode bundle. The runner creates one
self-contained directory per mode: copied simulator binary, resolved config,
trace symlink, SHA-256 provenance, full `run.out`, and a compact
`summary.txt`.

```bash
export C2P_GPGPUSIM_ROOT=/workspace/worktrees/gpgpu-sim-c2p-cache
scripts/run_c2p_cache_cases.sh \
  --trace /absolute/path/to/traces/kernelslist.g \
  --config "$C2P_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config" \
  --config-extra gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config \
  --out-dir hw_run/c2p-cache-results/<case>
```

The runner sources the selected GPGPU-Sim environment in each mode's process.
This is intentional: the executable and `libcudart.so` must come from the
same C2P worktree, not from the host CUDA installation.

`--config-extra` is repeatable. For example, append `trace.config` first and
then `configs/c2p-cache/paper-64sm-l1-16sets.config` for the paper-shaped L1
capacity point.

After a directory of completed case bundles exists, produce the review table
and machine-readable data with:

```bash
python3 scripts/summarize_c2p_cache_results.py \
  --root hw_run/c2p-cache-results \
  --csv hw_run/c2p-cache-results/summary.csv \
  --markdown hw_run/c2p-cache-results/summary.md \
  --strict
```

`--strict` checks two invariants for every case: oracle-only does not alter
baseline cycles, and each remote hit avoids exactly one L2 request. The
summary also carries Snapshot TP/TN/FP/FN, update-queue bypasses, rebuild
transport volume, and the separate fallback reasons so performance changes
remain attributable.
