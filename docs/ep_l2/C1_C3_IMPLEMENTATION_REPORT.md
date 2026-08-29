# EP-L2 Target Baseline: C1–C3 implementation report

Status: C1/C2/C3/C3b complete and stopped at the authorized C3 boundary.

## Implemented scope

* **C1 configuration:** `tests/ep_l2/b0_legacy_850.config` freezes
  `S:64:128:16` L2 tags, 128 line-MSHR entries, 256 global descriptors,
  32 descriptors/line, boundary queues `64:128:64:64`, FR-FCFS 128,
  ReturnQ 192, and 850 MHz. `b0_legacy_1ghz.config` changes only the DRAM
  clock to 1 GHz.
* **C2 L1:** target overlay selects 4 × 128 × 128-B, four banks and 20 cycles
  while retaining the QV100 MSHR/MissQ/write-policy parameters. The Core adds
  an init-time target-geometry assertion and a kernel-time no-reassociation
  assertion.
* **C3 shared descriptor MSHR:** Core implements an opt-in 128-B line MSHR
  key, global free-list pool of 256 long-lived descriptors, 32/line cap,
  per-line sector pending/issued/ready masks, and explicit blocker reasons.
  It preserves the existing `m_miss_queue` as the separate 128-entry lower
  issue queue. A descriptor is released by `commit_next_access()` only after
  the L2→ICNT queue push succeeds.
  `mshr_entry::m_list<mem_fetch*>` remains only as the existing
  request-ownership/compatibility mirror. The fixed-size descriptor pool and
  its per-entry descriptor-ID list are the target accounting authority; the
  list is not a physical EP-L2 descriptor store.
* **Response identity carrier:** `mem_fetch` now carries an initially-invalid
  `payload_id + generation` pair. Payload allocation and use remain deferred
  to C5.

## Directed verification

`/workspace/worktrees/gpgpu-sim-ep-l2/tests/ep_l2/run_descriptor_mshr.sh`
passes all mandatory C3 cases:

1. 128 distinct MSHR lines accept; the 129th blocks as `LINE_MSHR_FULL`.
2. 256 global descriptors accept; the 257th blocks as
   `DESCRIPTOR_POOL_FULL`.
3. 32 requesters to one line accept; the 33rd blocks as `PER_ADDRESS_CAP`.
4. A descriptor remains live through ready/peek and frees only on committed
   L2→ICNT response delivery.
5. Two sectors of one 128-B line share one line MSHR, preserve masks
   `pending/issued/ready`, and generate exactly one requester response each.

The full Core CMake Release build also passes. `git diff --check` passes.

## C3b production-path closeout

`/workspace/worktrees/gpgpu-sim-ep-l2/tests/ep_l2/run_descriptor_mshr_integrated.sh`
constructs a real `memory_partition_unit` and exercises the production
ICNT→L2→MissQ→L2→DRAM→return→fill→L2→ICNT path. It passes all five review
closure checks:

1. a descriptor remains allocated through MissQ drain, lower issue, DRAM
   return, fill, and a deliberately full L2→ICNT FIFO; it frees only after
   successful response enqueue;
2. `A+0` and `A+32` use one line MSHR, two descriptors, and exactly two lower
   sector reads;
3. two `A+0` requesters use one line MSHR, two descriptors, one lower read,
   and receive two replies;
4. 64 lines × four same-sector requesters consume all 256 global descriptors;
   request 257 is blocked as `DESCRIPTOR_POOL_FULL`, then the real path drains
   cleanly;
5. the non-mutating `l2_access_plan` now carries an EP-L2 block reason and
   target sector lower-read prediction for debug/instrumentation only. It does
   not add an admission rule or alter L2CHARV1 meanings.

The closeout fixture also verifies terminal queue/MSHR resource cleanliness.

## Explicitly not started

No WAD, payload RAM, legacy/banked payload scheduling, Unified/RO/TVD,
functional graphics bypass, `EPL2B0V1`, workload characterization, or
850-vs-1-GHz conclusion was started. C4+ remain subject to the required C3
review.
