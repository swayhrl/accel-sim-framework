# G2-4 — real stall/replay correctness

Status: `PASS`\
Core: `e7999554200760b31b4efe16d98e050370e1ea71`\
Framework source: `4012be3606c300d11e7b34826ee1cb22b0852b93`

The prior apparent allocation failure was closed by M2-D as a stale
cross-repository C++ layout build artifact.  A Framework dependency-generation
repair forces recompilation when Core headers change.  The Core follow-up only
classifies an early replay stall for existing statistics accounting; it does
not change frozen VM resources or translation semantics.  Full diagnosis and
before/after evidence are in `../M2_RUNTIME_MEMORY_DIAG/`.

## Directed replay proof

`vm_m2_g2_4_test PASS` covers pending translation, walker completion, repeated
same-UID replay, exactly-one modeled store side effect, exactly-one modeled
atomic side effect, and the approved cross-page boundary behavior.  The M1 and
G2-1/G2-2/G2-3 directed regressions all passed after the repair.

## Real cache-path replay

After a cold rebuild, the existing one-kernel RTX3070 trace reaches normal end
statistics in functional mode under the same 10 GiB virtual-memory bound used
for the disabled/ideal/functionality control:

- 85 translation access attempts; 79 completions;
- one MSHR allocation, one walk start/completion, one waiter registration and
  wakeup; zero active MSHRs, PWQ entries, and walkers at end;
- no MSHR-full or PWQ-full event in this small trace;
- normal program termination (not timeout/kill).

The full LUD and BFS functional replays in
[INTEGRATED_VALIDATION.md](INTEGRATED_VALIDATION.md) independently finish with
the same quiescence relations.  This is the first accepted real-path replay
evidence; the earlier pre-M2-D abnormal runs remain diagnostic history only.
