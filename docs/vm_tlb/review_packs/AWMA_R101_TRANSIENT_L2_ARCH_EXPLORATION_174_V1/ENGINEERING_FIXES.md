# Engineering fixes during formal admission

These were ordinary solve-and-continue issues, not scientific arms.

## Producer lifetime bridge

The producer publishes after-kernel states. A completion-only consumer would
misclassify a newly written generation as dead during its producer kernel.
The formal bridge therefore applies bounded PRE producer activations before any
CTA/L2 access and real POST deaths only after completion. The admitted event
budget is 16 PRE and 15 POST; PRE cannot invoke an O1 scan.

## Kernel UID namespace

The first formal B0 launch aborted before simulated work because capture kernel
ID 3577 is not the simulator runtime UID (1). Exact trace header/name/order had
already been admitted. The runtime check was corrected to validate exact ordered
names, unique runtime UIDs, and matching completion UIDs. The candidate was
rebuilt and all four exact T2 smokes re-passed before formal B0 restarted.

## Toolchain archive link

The accepted CUDA 12.4.131 combined include tree contained absolute links to a
runtime that had been migrated to node164. A symlink restored that exact archived
toolchain path; no compiler/toolkit version changed.

## Rejected host-only optimization

A lossless 16.2 GiB decompressed trace stage was generated and byte-verified.
Profiling showed the simulator/parser at about 99% CPU while `xz -dc` used only
about 0.3%, so the stage would not materially shorten replay. It was deleted;
all formal arms consume the accepted compressed traceg members directly.

## Per-kernel coverage and runner hardening

The original diagnostic selected runtime UID 1 and therefore could not prove
coverage for the remaining 17 kernels. The selector now supports `all`, resets
bounded UID sets after every kernel, and emits 18 independently checked records.
The formal summarizer requires ordered runtime UIDs 1-18 and exact
translated/admission and unique-UID equalities for every record.

The runner also pins the summarizer SHA before and after each long run, verifies
the actual consumer symlinks, rejects non-B0 arms until durable B0 is fully
qualified, isolates failures, and publishes to node164 only through a
hash-checked temporary directory and atomic rename.

## Full terminal drain

The first complete all-kernel B0 used a writeback-only drain. Although it
closed writeback and DRAM-latency counters, review found that it did not
directly prove general memory-partition/interconnect inactivity. That run is
preserved under `raw/engineering/B0_WB_ONLY_DRAIN_20260928` and excluded from
the formal matrix.

The final opt-in drain advances the ordinary simulator while either
`gpgpu_sim::active()` or the independently tracked L2-writeback count is
nonzero. It fails closed on max limits, deadlock or a finite drain bound and
prints/gates GPU active, L2-writeback active, max-limit and deadlock fields.
Four T2 smokes and all directed/regression tests re-passed before the final B0.

## Host storage recovery

Root-overlay pressure was handled without stopping simulations or modifying
another lane's worktree. The R101 generated build cache, three old unopened
`/tmp` artifacts, six worktree `.orig` backups, and one immutable unopened
shared Git pack were copied to explicit node164 recovery paths and content-hash
verified before local removal/replacement. The Git pack retains transparent
