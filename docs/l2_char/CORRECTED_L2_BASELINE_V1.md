# Corrected Conventional Sector-L2 Baseline v1

## Scope

This branch is a conventional, eager-allocation sector-L2 baseline derived
directly from GPGPU-Sim `03c1fe443b1a46de695381662830bb4b9a4b3a00`.  It is not
a Decoupled-L2 implementation.  In particular, it contains no address-only
directory, token allocation, late binding, decoupled lower-read credits,
abstract L2 banks, or dedicated WBQ.

The audited QV100 configuration remains:

```text
-gpgpu_cache:dl2 S:32:128:24,L:B:m:L:P,A:192:4,32:0,32
-gpgpu_cache:dl2_texture_only 0
-gpgpu_dram_partition_queues 64:64:64:64
-gpgpu_l2_rop_latency 160
```

It therefore retains the original sector organization, IPOLY mapping, LRU
replacement, write-back policy, lazy-fetch-on-read writes, and eager line or
sector reservation on a miss.

## Fidelity corrections

1. **Request-aware L2 admission.** A non-mutating preview determines tag,
   MSHR, shared miss/lower-request queue, data-port and immediate-response
   requirements before the existing `access()` commits state.  A full lower
   FIFO no longer blocks a hit, merge, clean miss, or locally absorbed write
   that will not enqueue lower traffic.
2. **Exact MSHR/MissQ accounting.** A merge consumes no new MissQ entry; a
   clean new read miss consumes one; a dirty-victim read miss consumes two.
   MSHR-new and MSHR-merge capacity remain distinct.
3. **Request-aware DRAM issue.** Read-like traffic remains constrained by its
   destination return FIFO.  L1/L2 writeback traffic does not consume it.  A
   per-channel `-gpgpu_l2_wb_progress_credit` (default one) prevents all
   general credits from indefinitely suppressing no-return writeback progress.
4. **Forward progress and accounting fixes.** Dirty-only victim selection
   falls back to the oldest unreserved dirty line; deadlock detection follows
   actual writeback/completion time; sector windowed miss rate no longer
   double-counts sector misses.

## Deliberate non-changes

The frontend remains one input request per subpartition L2 cycle.  Input FIFO
ordering, MSHR retirement timing, return-FIFO head ordering, ROP queue
capacity and DRAM scheduler policy are unchanged.  Their behavior is observed
by statistics, not redesigned in v1.

## Verification boundary

`tests/l2_char/run_synthetic.sh` is the deterministic admission-rule
regression.  Debug builds additionally assert preview/commit agreement for
lower events and the shared MissQ delta.  The review pack records its exact
build and test output.  No full workload characterization is part of this
baseline closeout.
