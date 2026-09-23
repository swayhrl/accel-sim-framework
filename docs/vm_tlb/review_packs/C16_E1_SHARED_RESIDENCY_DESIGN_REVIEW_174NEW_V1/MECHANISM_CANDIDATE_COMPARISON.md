# Shared-residency mechanism candidate comparison

## Evidence and decision boundary

The accepted hardware intervention establishes large target-specific module-timing benefits, but not target-specific material DRAM reduction. The first simulator study must therefore test replacement/residency efficacy without claiming that DRAM traffic is the unique mediator. Identity detection is held out of the first mechanism comparison by using an oracle/software address-range tag.

Measured budgets are tested points, not exact thresholds: 8, 16, 24, 32 MiB and one 33,947,648-byte qweight request. A simulator quota maps bytes to cache-line slots as `ceil(requested_bytes / line_bytes)` and distributes the total deterministically across L2 instances by quotient/remainder. It must not be described as a CUDA set-aside emulation or an inferred hardware alignment rule.

## M0_STATIC_PROTECTED_PARTITION

M0 reserves fixed ways or an equivalent fixed line quota for tagged target lines.

- Metadata: at least one protected/target bit per line; optional target-class bits for diagnostics.
- Extra state: fixed protected-way mask or per-set protected-slot count.
- Victim path: target fills select only the protected partition; ordinary fills select only the normal partition.
- Budget mapping: bytes-to-lines must then be converted to integer protected slots per set. Coarse associativity makes 8/16/24/32/full mappings quantized and potentially inaccurate.
- Normal borrowing: if allowed, the mechanism ceases to be a strict static partition and needs ownership/reclamation rules. Without borrowing, unused protected capacity is stranded.
- Critical-path risk: low selection complexity, but two disjoint victim domains and way-mask checks enter miss selection.
- Qualitative PPA/control cost: low metadata, low-to-moderate control.
- Failure modes: capacity stranding; set-level imbalance; protected hot sets can thrash while reserved slots elsewhere sit idle; ordinary data loses capacity even when target demand is absent.

M0 is retained as an interpretable static-partition control, not the recommended first mechanism.

## M1_ELASTIC_PROTECTED_QUOTA

M1 adds a target/protected bit to each valid line and a bounded protected occupancy quota. Ordinary lines may borrow every unused slot.

- Metadata: one protected bit per line. Target-class bits are optional for statistics and are not required by replacement.
- Extra state: protected occupancy counter and configured line quota per L2 instance; deterministic remainder distribution preserves the requested global line budget.
- Insertion: an oracle-tagged fill is protected. Below quota, it prefers an invalid line and then a non-protected victim. At quota, it replaces a protected line using the baseline recency order so protected occupancy cannot grow.
- Ordinary insertion: uses baseline behavior among ordinary candidates. Borrowed capacity needs no ownership bit because every valid non-protected line is ordinary. If all candidates are protected, baseline recency among the eligible protected lines provides bounded fallback.
- Hit/update: hit/miss lookup is unchanged. Baseline recency update still runs; the protected bit and occupancy change only on fill, replacement, invalidation, and reset.
- Budget mapping: direct line quota from 8/16/24/32/full requested bytes; no way rounding is required.
- Normal borrowing: complete; all capacity above current protected occupancy remains usable by ordinary traffic.
- Critical-path risk: the victim scan gains a protected/non-protected preference, but the tag-hit path and data-return path need not change. Counter updates are off the hit critical path.
- Qualitative PPA/control cost: one line bit, small counters/comparators, moderate victim-selection control.
- Failure modes: per-instance/skew imbalance; long-lived stale protected lines; oracle range mistakes; target-target contention once quota is full; benefits may remain local without decode-level speedup.

M1 best separates the evidence-backed question—whether bounded target residency helps—from classifier accuracy, while avoiding M0 capacity stranding.

## M2_PRIORITY_INSERT_EVICT

M2 uses priority insertion and delayed eviction/demotion without a hard protected quota.

- Metadata: target bit plus priority/lifetime state, or additional replacement-state encodings.
- Extra state: epoch/reuse counters or demotion state; potentially per-line age beyond the baseline replacement state.
- Victim path: ordinary replacement remains nominally compatible, but target priority alters ordering until lifetime expiry.
- Budget mapping: indirect. A byte budget must be translated into priority lifetime or admission pressure; this is harder to calibrate and less interpretable than a line quota.
- Normal borrowing: inherent because there is no partition.
- Critical-path risk: priority comparisons can affect insertion and every victim decision; lifetime updates may touch hits or periodic epochs.
- Qualitative PPA/control cost: moderate-to-high metadata and control.
- Failure modes: unbounded protected occupancy, priority pollution, phase sensitivity, difficult mapping from tested budgets, and conflation of admission/lifetime tuning with replacement efficacy.

M2 is deferred until the bounded quota experiment is understood.

## Recommendation

Use `M1_ELASTIC_PROTECTED_QUOTA` as the first simulator mechanism, with oracle/software-region tagging. Run `M0_STATIC_PROTECTED_PARTITION` as a capacity-stranding control. Do not introduce static-PC or dynamic-classifier accuracy into the first replacement-policy experiment.
