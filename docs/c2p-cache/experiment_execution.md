# C2P experiment execution

Run every core case as a seven-mode bundle. The runner creates one
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
`--strip-mem-addr-mapping`. The overlay fixes 64 SMs as 64 independent
simulator endpoints, while preserving the paper's eight logical groups of
eight SMs for comparator scope and C2P candidate locality. It also fixes GTO
scheduling, 1.41GHz core/ICNT/L2 clocks, a fixed 64KiB
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

For the canonical paper-oriented campaign, use the manifest wrapper.  It
requires a concrete trace root and always appends the QV100 trace overlay,
the paper-table overlay, and the deterministic 20-partition mapping fix:

```bash
scripts/run_c2p_paper16.sh \
  --trace-root /path/to/hw_run \
  --out-root hw_run/c2p-paper16 \
  --case btree,dwt2d,gaussian,hotspot1,lud,nn,cutcp,mri-q,sgemm,stencil,2DConvolution,3mm,atax,bicg,gemm,gesummv
```

Run a second invocation with `--modes baseline` and
`--config-extra configs/c2p-cache/paper-table-l2-50.config`.  Then aggregate
and render the paper-style figures with:

```bash
/usr/bin/python3 scripts/analyze_c2p_paper16.py \
  --results-root hw_run/c2p-paper16 \
  --l2-fast-root hw_run/c2p-paper16-l2-50 \
  --out-dir hw_run/c2p-paper16-analysis --strict
/usr/bin/python3 scripts/plot_c2p_paper_figures.py \
  --analysis-dir hw_run/c2p-paper16-analysis \
  --out-dir hw_run/c2p-paper16-figures --strict
```

The analyzer rejects missing modes or L2-50 points under `--strict`; it emits
machine-readable IPC/L2-access/classification tables, and the plotter emits
the Figure 10--14-style IPC, L2-access, filter-accuracy, and peer-access
figures.  ATA/CCD/RING remain mechanism-shaped comparison models documented
in the matching GPGPU-Sim `docs/c2p-cache/model_contract.md`.

Figure 13 uses a separate C2P-only parameter campaign.  `--mode-config-extra`
is intentionally appended after `c2p.config`, so its rows/hash overrides are
not silently overwritten by the paper-default configuration:

```bash
scripts/run_c2p_fp_sweep.sh \
  --trace-root /path/to/hw_run \
  --out-root hw_run/c2p-paper16-fp-sweep
/usr/bin/python3 scripts/analyze_c2p_fp_sweep.py \
  --sweep-root hw_run/c2p-paper16-fp-sweep \
  --paper16-analysis hw_run/c2p-paper16-analysis \
  --out-dir hw_run/c2p-paper16-analysis --strict
```

Re-run `plot_c2p_paper_figures.py --strict` after the sweep analysis; it
requires complete primary analysis, CCD TP/FN/FP/TN evidence, Figure-14
percentile/MAX counters, and a populated audited Figure-13 sweep before it
publishes a paper-style figure set. The default `m5120-k4` point is verified
to map identically to the fixed 5,120-row implementation it replaced.

If the primary seven-mode campaign predates the CCD filtering counters, do
not rerun its other six modes. Build the instrumented simulator in an isolated
worktree and collect only the additional CCD evidence:

```bash
scripts/run_c2p_ccd_metrics.sh \
  --trace-root /path/to/hw_run \
  --out-root hw_run/c2p-paper16-ccd-metrics
/usr/bin/python3 scripts/analyze_c2p_paper16.py ... \
  --ccd-metrics-root hw_run/c2p-paper16-ccd-metrics --strict
```

The original v7 CCD cycle/L2 values remain the Figure-10/11 source; the
separate root provides only same-config, provenance-captured Fig.12 counters.

### Parallel replay roots

Long full-trace replays may run in parallel, but never let two runners write a
case/mode directory in the same root.  Give each parallel batch a distinct
result root, then supply it as a supplemental root at analysis time.  The
canonical root is always selected first; a supplemental root fills only a
missing case/mode and its exact directory is recorded in
`paper16_provenance.csv`.

```bash
/usr/bin/python3 scripts/analyze_c2p_paper16.py \
  --results-root hw_run/c2p-paper16-v7 \
  --supplemental-results-root hw_run/c2p-paper16-v7-parallel \
  --l2-fast-root hw_run/c2p-paper16-l2-50 \
  --supplemental-l2-fast-root hw_run/c2p-paper16-l2-50-parallel \
  --ccd-metrics-root hw_run/c2p-paper16-ccd-metrics \
  --supplemental-ccd-metrics-root hw_run/c2p-paper16-ccd-metrics-parallel \
  --out-dir hw_run/c2p-paper16-analysis --strict
```

For a completed campaign, use `finalize_c2p_paper16.sh` with the same three
canonical roots and any supplemental roots.  It runs the strict evidence,
Figure-13, Figure-10--14, and report stages in dependency order; it stops at
the first missing evidence or invariant failure and never publishes a partial
figure set as final evidence.  Pass `--queue-sensitivity-root` when the
separate finite-queue diagnosis is complete to include that strict diagnostic
in the final report.
