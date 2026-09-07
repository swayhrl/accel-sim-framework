# Static validation record

Executed after the source edits, without compiling, linking or running a
simulator:

```text
git -C gpgpu-sim-vm-m4b-speculative diff --check
python3 accel-sim-vm-m4b-speculative/util/vm_tlb/validate_c10a2_static_closure.py
git -C accel-sim-vm-m4b-speculative diff --check
```

Observed validator result:

```text
C10A2 static closure PASS: transaction/lifecycle/generation pure models plus access/fair-arm source contracts
```

The validator checks:

- all F0--F9/H0 manifest rows, F5/H0 rejection, G96=6 and G32=2 sets, and
  F7/F8 N=8/x35/5|10|20 contract;
- atomic staging/swap and all named semantic-rejection statuses;
- a pure no-build admission model for capacity, overlap, unsorted, ASID/epoch,
  rights, class and extent failures with zero live state;
- a pure lifecycle model proving partial install/revoke is not active and that
  epoch wrap needs explicit quiesce;
- a pure ASID and global generation race model proving stale completion is
  refused;
- source assertions for inactive local replica construction, lifecycle APIs,
  explicit production READ/WRITE/ATOMIC forwarding, absence of an
  `OBJECT_WEIGHT` eligibility comparison, captured generation and stale-fill
  guards, retained `HIT_FIRST / MISS_JOIN` lower-launch suppression tokens,
  and runtime F5/H0 selector rejection.

This is static evidence only. The added C++ directed test source was not
compiled or run; no statement here establishes C++ correctness, standard-mode
preservation, timing correctness, telemetry output, or performance.
