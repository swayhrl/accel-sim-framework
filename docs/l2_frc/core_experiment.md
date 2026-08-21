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

Run one complete trace with:

```bash
scripts/run_l2_frc_core_sweep.sh --trace <kernelslist.g> \
  --config "$LATEBIND_L2_GPGPUSIM_ROOT/configs/tested-cfgs/SM7_QV100/gpgpusim.config" \
  --trace-config gpu-simulator/configs/tested-cfgs/SM7_QV100/trace.config \
  --run-root <result-dir>
```

## Required reporting

For every variant report total cycles, instructions, instructions/cycle,
L2 accesses/misses, FRC allocations/lower reads/swaps and FRC fallbacks.  The
paper additionally reports OPC, MPKO and L2 miss delay excluding DRAM time;
the current port does not claim those metrics until their precise QV100
definitions and accounting points are implemented.

## First complete workload result and limit

The complete CUDA SDK `fastWalshTransform` trace
`_logK_11__logD_19` was run with `baseline24` and `frc32-paper` after the
partition-local-sector correction.  Both complete at 180,944,896 instructions
and 172,297 cycles.  `frc32-paper` is active (467,526 allocations, lower
reads and swaps; 1,301,946 set-full fallbacks), but every conventional L2 bank
reports zero reservation failures.  The same negative control holds for the
complete `BlackScholes` trace: baseline and FRC32 both take 9,032 cycles;
FRC32 has 21,190 allocations while L2 reservation failures remain zero.

These negative-control measurements predate the independent FRC transaction
store and are retained only as a baseline record.  The paper-style model now
uses the finite FRC-owned request/waiter store defined in the Phase-3
contract, so all performance figures must be regenerated with its new core
commit.  QV100 still differs materially from the paper (64 sector-L2 slices
and CUDA traces rather than two 16-way AMD banks and OpenCL SDK 2.5), so any
new speedup remains a causal reproduction under this stated configuration,
not an absolute match to paper OPC.
