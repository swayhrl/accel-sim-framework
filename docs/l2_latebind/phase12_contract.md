# LateBind-L2 phase 1/2 contract

This document is the executable definition for the characterization and
oracle phase of the LateBind-L2 study.  It deliberately describes the
baseline model rather than claiming to reproduce a particular commercial GPU.

## Scope and frozen baselines

The abstract decoupled-L2 prototype is archived separately as
`decoupled-l2-abstract-v0-20260821`.  It is not a performance baseline for
this study.

The Phase 1/2 functional and timing baseline is the unmodified GPGPU-Sim
commit `03c1fe443b1a46de695381662830bb4b9a4b3a00` (`origin/dev` when this
branch was created).  The matching experiment harness starts from
Accel-Sim commit `dca4742ed268afc56f317f7544ba360a14b91e81`.  Every result
records both source commits, the config file digest, the trace digest, and
the selected oracle mode.

The default V100-like configuration has 32 memory partitions, two L2
subpartitions per partition, and a sector L2 of `S:32:128:24` per
subpartition.  It is therefore 64 independently banked subpartition caches
and 6 MiB of resident payload in total.  `-gpgpu_l2_rop_latency 160` is an
upstream request delay; it is **not** reported as an intrinsic L2 hit
latency.  Hit and miss latencies are measured at the model boundaries stated
below.

## Phase 1: baseline characterization

Phase 1 only observes the baseline.  With statistics disabled, it must be
cycle-for-cycle and output-for-output identical to the frozen baseline.  The
required evidence is a trace digest plus a per-cycle stream of accepted L2
requests, lower requests, fills, and L2 replies for directed tests.

The instrumentation reports, per L2 subpartition and in aggregate:

- accepted accesses, tag outcomes, MSHR merges/full stalls, and reservation
  failures;
- resident sector occupancy, reserved-without-payload sector occupancy, and
  dirty sector occupancy, each sampled once per cache cycle;
- reservation lifetime from allocation at miss until the corresponding sector
  fill becomes usable;
- writeback generation, dirty bytes/sectors, and writeback queue residency;
- data-port and fill-port busy cycles; and
- request latency from L2 acceptance to L2 reply, separated into hit, merged
  miss, and first-miss classes.

The lower-memory interface and DRAM timing are not changed in Phase 1.  A
bank counter is labelled *observational* unless it is driven by an actual
single-port arbitration point; it must never be used as a performance claim.

## Common oracle rules

An oracle has one narrowly stated counterfactual and leaves all other
baseline effects intact.  Each run prints an `oracle_contract` record with
its enabled changes.  No oracle may silently use the abstract v0 bank model.

`capacity` always has two values: resident payload bytes and transient
metadata bits.  Equal-area claims additionally state tag/state bits, data
bits, transient metadata bits, and every added read/write port.  A pool whose
payload is absent while memory is outstanding is not charged as resident
payload, but its metadata is charged separately.

## Phase 2 oracle definitions

1. **infinite_mshr** removes only the entry and merge-count limits of the
   baseline MSHR table.  Miss-queue, set reservation, ports, and writeback
   behavior remain finite.
2. **shadow_no_set_reservation** is a non-timing shadow analysis.  It counts
   admission opportunities that baseline rejects solely because all candidate
   sectors are reserved, while preserving the baseline's real hit/miss stream.
   It is never presented as a speedup or as having the same hit rate.
3. **ideal_delayed_victim** keeps the baseline tag/data capacity and all
   lower-memory timing, but gives a miss an unbounded abstract landing record
   until fill.  The victim is selected at fill.  Its result is marked an upper
   bound because landing storage and fill arbitration are idealized.
4. **ideal_writeback** removes only writeback queue and writeback data-port
   backpressure after a dirty victim is selected.  Dirty victim selection,
   request ordering, and DRAM read timing are unchanged.  Its report includes
   both the number of suppressed stalls and the modeled dirty traffic.
5. **equal_capacity_transient** uses the explicit transient bit budget stated
   by the run manifest.  It shares that finite budget among in-flight line
   records; it does not assume free data storage or extra ports.  It is
   invalid to run this oracle without a nonzero metadata budget in the
   manifest.
6. **sector_transient** is oracle 5 with a record keyed by line address plus
   sector-valid, sector-dirty, and request-order masks.  It is compared only
   against oracle 5 using the same total metadata-bit budget.

The only performance oracles are 1, 3, 4, 5, and 6.  Oracle 2 produces a
counterfactual pressure distribution and is used to decide whether a delayed
victim implementation is worth modeling.

## Required safety invariants

For all instrumentation and oracle modes:

- a lower read has exactly one fill or an explicit cancellation record;
- every accepted request is eventually replied, merged into a request that is
  replied, or is a writeback acknowledgement explicitly consumed by baseline
  policy;
- an address cannot own two independent transient records;
- a dirty victim is either retained, represented by one writeback record, or
  consumed by `ideal_writeback` with a counted dirty-traffic record; and
- all finite resource credits are acquired before the request is accepted.

Violations are assertions in development builds and are included in the
directed regression suite.  A timeout alone is never accepted as deadlock
evidence without the corresponding resource-state dump.
