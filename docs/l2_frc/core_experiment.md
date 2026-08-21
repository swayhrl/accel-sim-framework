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
The entry sensitivity points are FRC 4, 8, 16, 32, and 64 entries in paper
timing mode.  FRC payload is not free capacity:

| Comparison | Equal payload capacity |
|---|---|
| `frc32-paper` | `baseline25` |
| `frc64-paper` | `baseline26` |

The FRC variants retain the 24-way L2 and add respectively 32 or 64 FRC
lines, exactly one or two 32-set L2 ways.  `baseline25` and `baseline26`
instead add that storage to conventional L2.  Metadata/ports remain an
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
