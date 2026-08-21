# FRC core experiment protocol

This is a mechanism-port experiment on the QV100 Accel-Sim configuration.  It
does not reproduce the paper's absolute AMD HD7770/Multi2Sim OPC values: the
paper uses OpenCL SDK 2.5, two 16-way 128-KiB L2 banks and 64-byte blocks;
this experiment uses CUDA SDK traces, 64 QV100 L2 subpartitions and 128-byte
sector lines.  It can reproduce the paper's causal experiment: varying FRC
entry count versus conventional and capacity-matched L2 controls under one
unchanged simulator configuration.

## Workload selection

The primary set is the locally retained CUDA SDK analogues of paper workloads:
`fastWalshTransform`, `BlackScholes`, `scan`, `transpose`, and
`convolutionSeparable`.  Results must name the exact trace input and whether
it is complete or a documented deterministic trace fraction.  A workload is
considered FRC-relevant only if its FRC variants show nonzero FRC allocations
and at least one of a changed cycle count, a changed L2 miss count, or a
nonzero set-full/ordinary fallback pressure.  A no-activity workload remains
a useful negative control, not evidence of FRC speedup.

## Variants and fairness

Each L2 subpartition starts at 32 sets x 24 ways x 128 bytes (`baseline24`).
The QV100 address mapping routes a 32-byte sector, rather than an entire
128-byte L2 line, to one subpartition.  The entry sensitivity points are FRC
4, 8, 16, 32, and 64 partition-local sectors in paper timing mode.  FRC
payload is not free capacity:

| Comparison | Equal payload capacity |
|---|---|
| `frc128-paper` | `baseline25` |
| `frc256-paper` | `baseline26` |

The FRC variants retain the 24-way L2.  128 or 256 FRC sectors contribute
exactly one or two 32-set L2 ways of payload, while `baseline25` and
`baseline26` add that storage to conventional L2.  Metadata/ports remain an
explicit implementation cost, as specified in the Phase-3 contract.

The core sweep also includes `baseline48-paper_capacity` and
`baseline96-paper_capacity`: these retain the paper's 2x and 4x conventional
L2-capacity ratios (the paper's 128KB-to-256KB and 128KB-to-512KB controls).
They are intentionally reported separately from `baseline25/26`, because
they are much larger than the exact FRC payload matches.

The complementary low-associativity sensitivity uses `baseline1-pressure`,
`frc128-pressure`, and `baseline2-pressure`.  Here FRC128 contributes exactly
one 32-set x 128-byte conventional L2 way per sector-L2 slice, so the latter
is the payload-capacity match.  This is an intentional transient-replacement
stress point, not a claim that one way represents QV100 or the paper's
16-way HD7770 bank.

Run one complete trace with:

```bash
scripts/run_l2_frc_core_sweep.sh --trace <kernelslist.g> \
  --config "$LATEBIND_L2_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config" \
  --trace-config gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config \
  --run-root <result-dir>
```

## Required reporting

For every variant report total cycles, scalar thread instructions,
`scalar_opc = instructions / cycles`, L2 accesses/misses and
`l2_mpko = 1000 * L2 misses / scalar thread instructions`, plus FRC
allocations/lower reads/swaps and fallbacks.  `scalar_opc` and `l2_mpko`
preserve the paper's relative metric definitions within one QV100 experiment;
they are not numerically comparable with the paper's HD7770 OPC/MPKO because
the architecture, trace accounting and cache geometry differ.  The optional
`-gpgpu_l2_latebind_stats 1` observation point measures each *unique primary*
lower read: `pre-memory = L2 acceptance -> lower issue`,
`lower-memory = lower issue -> lower return`, and
`post-memory = lower return -> upper reply`.  Pre plus post is the L2 miss
management delay excluding the measured lower-memory interval.  Merged
waiters do not add another sample; an FRC sector fetch is charged back to the
primary request that allocated it.  Use an `*-observe.config` and
`scripts/collect_l2_frc_delay_metrics.sh` to collect it.  For a multi-kernel
trace, the runner takes the final cumulative occurrence of each simulator
statistic; intermediate per-kernel reports are not experiment totals.

The collector also reports `first-offer = first L2 offer -> lower issue`.
Unlike acceptance-based pre-memory, it retains time spent retrying a request
after a `RESERVATION_FAIL`.  It distinguishes retry delay from an accepted
miss waiting in the ordinary miss/replacement path; neither metric should be
used as a substitute for the other.  Existing observation logs produced
before this counter report `NA` for this column rather than silently treating
it as zero.

## Causal replacement-pressure gate

`scripts/check_l2_frc_replacement_pressure.sh` is deliberately not a paper
workload.  It is a deterministic two-read trace with a one-way L2: both reads
map to one L2 slice/set, while `frc4-pressure` gives that slice four
partition-local FRC sectors.  It proves the mechanism's causal distinction:
the control reports 136 L2 reservation failures and takes 5,470 cycles;
FRC4 accepts two independent FRC allocations and completes in 5,337 cycles
(2.43% faster).  This is a correctness/performance gate only, not a general
workload result or a capacity-fair comparison.

The observation-enabled rerun identifies the source of this directed benefit:
both primary lower reads have `first-offer -> lower issue = 1` cycle, while
the baseline has `accept -> lower issue = 69` cycles/read and FRC4 has 1.
The lower-memory averages are 136.0 and 137.5 cycles/read, respectively, so
the 133-cycle application-level difference is explained by the conventional
accepted-miss path, not a faster lower memory.  The baseline's 136 reservation
failures remain a useful pressure fingerprint, but they are not silently
attributed to the two completed primary-read samples.

## Completed full-trace results with the independent transaction store

All values below use the core behavior from `ab3b4cdf` (FRC-local
request/waiter store, delayed-swap receipt and fair lower-request
arbitration), the unmodified SM7 QV100 configuration and complete CUDA SDK
traces.  Rows that quote observation metrics use `aa3f5b07`, which adds only
the timestamp accounting point.

| Trace | Compared variants | Cycles | Observation |
|---|---|---:|---|
| `fastWalshTransform/_logK_11__logD_19` | `baseline24`, `frc32-paper`; exact-payload `baseline25`, `frc128-paper` | 172,297 / 172,297; 172,297 / 172,297 | FRC is active (467,526 allocations, lower reads and swaps; 1,301,946 set-full fallbacks), but the conventional control has zero L2 reservation failures.  The exact-payload pair also has 131,072 unique lower reads and 2-cycle non-DRAM management delay in both variants. |
| `BlackScholes/NO_ARGS` | all 12 matrix points | 9,032 each | Every FRC point is active; FRC allocations rise from 3,554 (`frc4`) to 37,500 (`frc256`), and set-full fallbacks fall from 33,946 to zero.  Exact-payload (`baseline25/26`) and paper-ratio (`baseline48/96`) conventional controls are also 9,032 cycles. |
| `BlackScholes/NO_ARGS`, observation | `baseline24`, `frc32-paper` | 9,032 / 9,032 | Both complete 37,500 unique lower reads at 1-cycle pre-memory + 1-cycle post-memory = 2-cycle management delay.  FRC changes neither the delay nor total cycles at this no-pressure point. |
| `convolutionSeparable/__size_3072` | mechanism `baseline24`, `frc32-paper`; exact-payload `baseline25`, `frc128-paper` | 418,556 / 390,216; 414,644 / 423,482 | FRC32 is 6.77% faster than its no-extra-payload baseline, but that is not a fair capacity comparison.  The exact-payload FRC128 point is 2.13% slower than baseline25 despite moving 2,281,345 reads into the FRC store and cutting conventional `mshr_new` from 2,390,218 to 110,355.  Its management delay is also slightly higher (2.017787 vs 2.006770 cycles) and it has 32,309 more L2 misses. |
| `transpose/dimX512_dimY512` | `baseline24`, `frc32-paper`; exact-payload `baseline25`, `frc128-paper` | 201,054 / 201,054; 201,054 / 201,054 | FRC is active (374,568 allocations, lower reads and swaps; 411,864 set-full fallbacks), but the control again has zero L2 reservation failures.  The exact-payload pair also has 32,768 unique lower reads and 2-cycle non-DRAM management delay in both variants. |

The complete convolution entry sweep provides the required FRC-capacity
fingerprint.  `FRC-served share` below is the completed FRC allocation share
of all reported L2 misses; every listed allocation produces one lower read and
one completed swap.  It rises monotonically with entry count while set-full
fallback falls, whereas performance is non-monotonic as expected when the
additional early fetches alter lower-memory contention.

| Variant | Cycles | Relative to baseline24 | FRC-served share | Set-full fallback |
|---|---:|---:|---:|---:|
| `frc4-paper` | 426,441 | -1.88% | 5.60% | 2,161,711 |
| `frc8-paper` | 427,066 | -2.03% | 12.21% | 1,843,478 |
| `frc16-paper` | 406,197 | +2.95% | 20.78% | 1,430,682 |
| `frc32-paper` | 390,216 | +6.77% | 32.49% | 863,972 |
| `frc64-paper` | 410,158 | +2.01% | 41.67% | 411,963 |
| `frc128-paper` | 423,482 | -1.18% | 47.71% | 113,571 |
| `frc256-paper` | 420,691 | -0.51% | 49.67% | 12,060 |

The exact payload controls are `baseline25=414,644` versus
`frc128=423,482` (FRC 2.13% slower) and `baseline26=389,237` versus
`frc256=420,691` (FRC 8.08% slower).  `baseline48=462,798` and
`baseline96=394,780` are retained as the paper-ratio controls, not as payload
matches.  Thus the FRC capacity/served-share trend is reproduced, but this
QV100 configuration does not reproduce the paper's capacity-fair performance
advantage.

The low-associativity BlackScholes sensitivity makes the causal condition
observable with real trace traffic: `baseline1` completes in 12,396 cycles
with 186,478 reservation failures; `frc128` completes in 9,658 cycles with
668 failures (22.1% faster than `baseline1`); the equal-payload `baseline2`
completes in 9,441 cycles with 3,658 failures.  Thus FRC fixes the transient
replacement bottleneck, but in this QV100 port it is still 2.3% behind an
equal-payload conventional second way.  The result is a truthful mechanism
comparison, not evidence that this configuration matches the paper's claim
that FRC usually outperforms capacity expansion.

The independent transaction store is therefore exercised, but the completed
capacity-fair controls do **not** reproduce a FRC speedup: FWT and transpose
tie, while convolution favors equal-payload conventional capacity.  The
deterministic replacement-pressure gate above proves the causal mechanism
under such pressure; it must not be generalized to these workloads.  Complete
`scan` pairs remain in progress.  QV100 also differs materially from the paper
(64 sector-L2 slices and CUDA traces
rather than two 16-way AMD banks and OpenCL SDK 2.5), so this remains a causal
reproduction under a stated configuration, not an absolute match to paper
OPC.
