# Engineering fixes

These are solve-and-continue engineering events, not scientific arms.

## CONTEXT2 index basis

The Goal's original launch indices 3-8 are zero-based. They map to accepted
sidecar ordinals 4-9 and members 3580-3585. The derivation receipt encodes both
bases so normalization member 3579 cannot be included accidentally.

## LDGSTS qualification

A simple ATOMIC/RED regex initially missed that measured transient traffic
contains many `LDGSTS.E.BYPASS.LTC128B.128` records. Full authoritative trace
decode found the issue before formal execution.

Source audit established that Accel-Sim maps OP_LDGSTS to a global memory load,
sets `m_is_ldgsts`, and completes it through pending-LDGSTS/DEPBAR bookkeeping.
O2 therefore supports LDGSTS explicitly as READ and tests the existing client3,
pending decrement and final depbar release path. ATOMIC/RED and every other
unsupported measured transient semantic remain fail-closed. The final decode
has zero unsupported records.

## Build cache permission

The first cold build placed generated objects on node164. That mount forces
mode 777, while the GPGPU-Sim Makefile requires a chmod to 0555; the build
stopped before producing a binary. The 3.9 MiB partial cache is retained as
`workspace_cache/gpgpu-sim-build_nfs_permission_failed`.

Only reproducible build objects were moved to an isolated local build
directory. Large immutable traces and all raw results remained on node164.
The subsequent cold build passed.

## Formal summarizer recovery

Both B0 and O2 simulators completed rc=0, stderr=0 and 6/6 coverage. The
formal-at-run summarizer failed before creating RUN_SUMMARY because it inferred
the arm from an atomic in-flight directory name rather than `command.json`.
Review also removed an extra, non-preregistered requirement that O2 ROI L1D
accesses must increase; legal O2 bypasses all targeted L1D traffic while normal
non-oracle L2/DRAM activity remains.

Recovery changed only postprocessing:

- arm identity comes from the immutable command receipt;
- non-oracle hierarchy activity requires measured L2 activity, not L1D growth;
- formal-at-run runner/summarizer hashes and current recovery-tool hashes are
  separately recorded.

Before/after SHA and size for command, log, stderr and rc are identical in each
`ORCHESTRATION_RECOVERY.json`. Fixed summaries pass every gate and were
atomically promoted. No simulator was rerun and no scientific input, binary,
config or raw counter changed.
