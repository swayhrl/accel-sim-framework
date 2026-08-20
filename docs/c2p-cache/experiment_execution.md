# C2P experiment execution

Run every core case as a four-mode bundle. The runner creates one
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

`--config-extra` is repeatable. For the paper-table point, append `trace.config`
first, then `configs/c2p-cache/paper-table.config`, and pass
`--strip-mem-addr-mapping`. The overlay fixes 64 SMs as eight clusters of
eight, GTO scheduling, 1.41GHz core/ICNT/L2 clocks, a fixed 64KiB
16-set/32-way/128B L1 with 20-cycle latency, and 20 memory partitions with two
sub-partitions each. Removing the inherited QV100 explicit address map is
necessary because it only supports a power-of-two partition count. The QV100
IPOLY partition hash likewise cannot represent 20 channels; the overlay uses
Accel-Sim's deterministic consecutive map, since the manuscript does not
specify an address hash. Its 128-set L2 likewise uses linear rather than
IPOLY set indexing because the simulator implements the latter only through
64 sets; capacity, associativity, line size, and the configured latency remain
the paper-table values.

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

For a completed core case, add the paper-latency comparison models with:

```bash
scripts/run_c2p_cache_cases.sh ... --modes ata,ccd,ring
```

They are deliberately separate from `--strict`: baseline/oracle/ideal/C2P
remain the correctness and opportunity bundle, while ATA/CCD/RING are
mechanism-shaped comparison models documented in the matching GPGPU-Sim
`docs/c2p-cache/model_contract.md`.
