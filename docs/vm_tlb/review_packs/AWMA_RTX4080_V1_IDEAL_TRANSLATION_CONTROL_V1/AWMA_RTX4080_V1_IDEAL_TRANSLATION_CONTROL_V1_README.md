# AWMA RTX4080/V1 ideal-translation control V1

Status: `IN_PROGRESS_NO_FULL_KERNEL_RESULTS`.

This pack records only the RTX4080/V1 ideal-translation control authorized by
`PARALLEL_REPRESENTATIVE_SUITE_V1.md`. It does not reuse historical R0/I0
numbers and it does not alter the frozen RTX4080 platform, 10/80 parameters,
V1 semantics, V2R1, or Lane B.

## Source and binary

- coordination head: `b5a366fcda31ee0ba18f235288eed51b998e4589`;
- comparator authority: `AWMA_RTX4080_SIM_BASELINE_V1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`;
- execution commit: `c01435f1e72e3e350e1430def95a9cfb7611b101`;
- ideal binary SHA-256: `2b84282e1e284cbe3f7a26c413e46c73a999656e80d4e2e1b70a7b11471045a4`.

The opt-in environment switch is `GPGPUSIM_VM_IDEAL_TRANSLATION_CONTROL=1`.
It resolves the current V1 page-table mapping at head admission, preserves
SimVA and the resulting downstream SimPA, and creates no modeled translation
lookup, TLB fill, MSHR, PTW, PWC, PTE, queue, or walker state. The V1
prelaunch scan is disabled while the switch is on, so queued later accesses
are not resolved early. Default is off.

## Validation completed

- the core patch dry-runs cleanly against the frozen V1 runtime source;
- the isolated core and Accel-Sim binary builds returned zero;
- OFF empty-trace startup returned zero for the frozen baseline and the new
  binary, with empty stderr and identical stdout after the binary build line;
- ON empty-trace startup returned zero with empty stderr;
- the ideal-only T0/T1/T2 runner passes Python compilation.

## Still required

No full-kernel point has been started. Before closing this stage, run T0/T1/T2
only when host resources are safe, then prove instruction/CTA/UID/coverage,
untranslated=0, unobserved=0, duplicate=0, terminal quiescence, and OFF V1
scientific-signature identity. Reuse only accepted exact-identity 10/80 and
0/80 comparator rows, then report `C_10_80`, `C_0_80`, `C_ideal`, `S_L1`, and
`S_ALL`; do not call `S_ALL-S_L1` a PTW time fraction.
