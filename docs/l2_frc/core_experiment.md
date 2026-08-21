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
the architecture, trace accounting and cache geometry differ.  Average L2
miss delay excluding DRAM time still needs a dedicated QV100 accounting point.

## Causal replacement-pressure gate

`scripts/check_l2_frc_replacement_pressure.sh` is deliberately not a paper
workload.  It is a deterministic two-read trace with a one-way L2: both reads
map to one L2 slice/set, while `frc4-pressure` gives that slice four
partition-local FRC sectors.  It proves the mechanism's causal distinction:
the control reports 136 L2 reservation failures and takes 5,470 cycles;
FRC4 accepts two independent FRC allocations and completes in 5,337 cycles
(2.43% faster).  This is a correctness/performance gate only, not a general
workload result or a capacity-fair comparison.

## Complete workload results with the independent transaction store

All values below use core commit `a3901230` (FRC-local request/waiter store),
the unmodified SM7 QV100 configuration and complete CUDA SDK traces.

| Trace | Compared variants | Cycles | Observation |
|---|---|---:|---|
| `fastWalshTransform/_logK_11__logD_19` | `baseline24`, `frc32-paper` | 172,297 / 172,297 | FRC is active (467,526 allocations, lower reads and swaps; 1,301,946 set-full fallbacks), but the conventional control has zero L2 reservation failures. |
| `BlackScholes/NO_ARGS` | all 10 matrix points | 9,032 each | Every FRC point is active; FRC allocations rise from 3,554 (`frc4`) to 37,500 (`frc256`), and set-full fallbacks fall from 33,946 to zero.  `baseline25`/`baseline26` and their capacity-matched FRC points are also 9,032 cycles. |

The low-associativity BlackScholes sensitivity makes the causal condition
observable with real trace traffic: `baseline1` completes in 12,396 cycles
with 186,478 reservation failures; `frc128` completes in 9,658 cycles with
668 failures (22.1% faster than `baseline1`); the equal-payload `baseline2`
completes in 9,441 cycles with 3,658 failures.  Thus FRC fixes the transient
replacement bottleneck, but in this QV100 port it is still 2.3% behind an
equal-payload conventional second way.  The result is a truthful mechanism
comparison, not evidence that this configuration matches the paper's claim
that FRC usually outperforms capacity expansion.

The independent transaction store is therefore exercised and the capacity
matrix is complete, but these two complete QV100 workloads do **not**
reproduce a speedup: their conventional controls have no transient L2
replacement pressure to remove.  The deterministic replacement-pressure gate
above proves the causal mechanism under such pressure; it must not be
generalized to these workloads.  QV100 also differs materially from the paper
(64 sector-L2 slices and CUDA traces rather than two 16-way AMD banks and
OpenCL SDK 2.5), so this remains a causal reproduction under a stated
configuration, not an absolute match to paper OPC.
