# AWMA RTX4080/V1 ideal-translation control V1

Status: `COMPLETE_INVALID_DIAGNOSTIC_SEMANTIC_GATE_FAILED`.

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

## V1 closeout

T0/T1/T2 full-kernel points completed but are all
`INVALID_DIAGNOSTIC`. V1 disabled the frozen prelaunch scan and thereby changed
V1 frontend scheduling. Its results must not be used for scientific conclusions
or as accepted ideal controls. V2 supersedes the investigation with the original
prelaunch policy restored and a new UID-set semantic gate.
