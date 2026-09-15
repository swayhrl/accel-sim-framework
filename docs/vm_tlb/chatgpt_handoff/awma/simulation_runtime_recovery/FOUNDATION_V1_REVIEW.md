# Simulation Foundation V1 — Review Decision

## Decision

Accepted as:

`AWMA_SIMULATION_FOUNDATION_PASS_RUNTIME_BLOCKED`

The non-runtime foundation is sufficient to proceed.

## Accepted evidence

The foundation established and regression-tested:

- deterministic simulation-side identities;
- fail-closed simulator input admission;
- explicit rejection of current `C16WARP1` / `MREF_SHARDED_COMPLETE_SET` as lossless simulator input;
- historical C12/C13/C14/M4B/M4C backfill with original scientific status preserved;
- simulation telemetry normalization and namespace checks;
- immutable/idempotent simulation catalog behavior with same-ID conflict rejection;
- node164 simulation snapshots;
- machine-checkable `SIM_COMPAT_CAPTURE_V1` consumer-side admission skeleton.

Historical status boundaries remain unchanged:

- C12 Prefill/Decode F0: FORMAL historical reference;
- C13/C14/M4B/M4C: DIAGNOSTIC / reference-only as originally qualified;
- C12 pre-fix scan: PRE_FIX / archaeology only.

## Runtime blocker

`NEW_SIM_BASELINE_V1` is not yet qualified because the foundation worktree did not have a usable CUDA/nvcc toolchain, exact historical Core/binary are unavailable, and the existing EP-L2 binary is not a VM/TLB baseline.

This does not invalidate the non-runtime foundation.

## Small issues folded into the next stage

These are not separate-round blockers and must be repaired inline during runtime recovery:

1. The prose consumer contract requires synchronization/control semantics, but the current `instruction_semantics` validator requires only PC/opcode/access/memory-space/width/warp/CTA/mask/addresses/order. Add an explicit control/synchronization requirement or an explicit semantically valid `NONE`/not-applicable representation; do not silently omit it.
2. Current trace admission proves hash closure and xz readability, but only minimally checks trace payload grammar. When a real/historical traceg parser is available in the runtime stage, strengthen admission with a bounded grammar/parser smoke and a malformed-record negative fixture.

These repairs do not change accepted Native evidence and do not justify a standalone cleanup stage.

## Git identity note

The user's local execution commit was reported as `6b78ad98...`, while the remote branch was advanced through the Git Database API to commit `11990917cbae60f99ab629bfdf24265ad6e9cb64`. The remote commit tree is `09cc2f029022c660a3f827af9abded0fb34bdb41`, matching the reported local tree. Future work should anchor to the remote commit/tree rather than assuming commit-object equality.
