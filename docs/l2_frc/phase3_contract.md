# Phase 3 FRC contract

This branch implements the mechanism described by *Improving GPU Cache
Hierarchy Performance with a Fetch and Replacement Cache* (HPCA 2019).  The
source copy used for this study is retained outside this worktree with SHA256
`f6fdb58e00da49dfa66305f0581a1e74ed11240334a9ad06229681f85cd4f1dc`.

It is an experimental GPGPU-Sim model, not a claim of RTL equivalence.  The
baseline is the Phase-1 characterization branch plus the read-miss dirty
victim ownership correction in core commit `5721256a`.  Consequently every
FRC comparison uses `-gpgpu_l2_frc_enable 0` from this branch as its control.

## Mechanism contract

- There is one FRC per L2 subpartition.  The QV100 address map assigns a
  32-byte sector to one subpartition, so an FRC entry is that partition-local
  allocation unit and is set associative by sector address.  A full 128-byte
  L2 line spans multiple subpartitions and cannot be fetched or owned by one
  slice without a cross-subpartition FRC fabric.
- The normal L2 tag lookup and the FRC lookup are concurrent logical checks.
  A true miss may allocate a free FRC entry and issue the lower read without
  reserving an L2 victim.  A full FRC set falls back to conventional L2 miss
  handling.
- An FRC entry is `FREE`, `FETCHING`, `FETCHED`, or `EVICTING`.  `FETCHED` is
  only the internal completed-before-swap state: the model swaps it into L2
  immediately, so later hits use L2 rather than a second data source.
  `EVICTING` retains a dirty L2 victim until its writeback is accepted by the
  lower interface and is never a hit.
- Victim choice happens at fill/swap time.  A clean victim releases the FRC
  entry immediately.  A dirty victim stays in the entry until the lower
  writeback handshake transfers its ownership.
- FRC does not add or remove MSHRs.  MSHR keys and FRC ownership both remain
  32-byte sectors.  A later request for a fetching sector merges into its
  normal MSHR before that sector swaps into L2.
- FRC currently owns only read-miss scheduling.  Stores (including partial
  sector stores) and atomics explicitly use the unmodified baseline path,
  which remains authoritative for byte masks and atomic order.  Their
  per-subpartition fallback counters are printed and checked by the directed
  suite; this is a deliberate semantic boundary, not an unmodelled path.  A
  same-line store or atomic stalls while an entry is `FETCHING`, preventing a
  baseline allocation from creating a second owner before swap.
  A read is accepted into FRC only after all finite credits needed for its
  chosen path are known available.

## Timing modes

`paper` is the default.  It makes the FRC lookup and a completed clean swap
logically overlap the L2 lookup and does not charge an additional L2 data
port.  `conservative` charges `lookup_latency` on allocation and
`swap_latency` on swap through the ordinary fill-side management port; this
serializes later fills for the requested number of cycles.  Results always
print the selected mode; neither mode claims a physical equal-area design.

## Capacity and comparison rules

The default QV100 L2 is 64 subpartitions, each with 32 sets x 24 ways x
128-byte lines.  FRC capacity is reported separately as payload capacity and
transient metadata.  A 32-byte FRC entry is one quarter of a conventional L2
way's per-set payload: `frc128` and `frc256` require matched baseline
comparisons with respectively one and two additional L2 ways.  FRC's finite
state/tag/mask metadata and all extra port assumptions are reported, not
hidden in payload capacity.

## Required invariants

- At most one FRC entry owns a line in any subpartition.
- Every FRC-owned lower read maps to one entry and all returned sectors are
  either recorded or explicitly rejected before reply.
- A line cannot simultaneously be resident in L2 and serve as an FRC hit.
- A dirty victim is in exactly one of: L2, an `EVICTING` FRC entry, or a
  lower writeback request.
- No FRC entry is released before its dirty writeback lower handshake.

`wb_wait_cycles` measures the interval from inserting that FRC-owned
writeback into the L2 miss queue to its lower acceptance.  It may be zero in
an uncongested run; ownership is nevertheless held until the acceptance edge.
`flush_calls` is diagnostic only: Accel-Sim may invoke end-of-kernel flushing
repeatedly while draining, so it is not a count of distinct cache lines.

The directed suite covers fetching-sector ownership, set-full fallback, clean
swap, dirty swap and the lower-WB ownership handshake, partial-write baseline
fallback, atomic baseline equivalence, and end-of-kernel flush.  The
simulator's ordinary queue model does not inject an artificial lower-port
stall; `wb_wait_cycles` keeps that future stress point observable rather than
claiming a blocked-WB result that the trace did not create.
