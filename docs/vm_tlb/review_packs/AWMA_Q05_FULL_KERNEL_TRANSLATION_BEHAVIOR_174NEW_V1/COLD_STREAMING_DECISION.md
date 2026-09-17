# Classification

Classification: `MIXED` with `INCONCLUSIVE` per-translation fill attribution.

Evidence supports substantial same-translation pre-fill fanout: 125 miss requesters are exactly 19 allocations plus 106 merges, with maximum waiter depth 35 and high requester MSHR-wait contribution. The full offline footprint is only 228 pages but has highly skewed structural popularity, so a simple capacity/streaming explanation is not justified. Natural completion proves the whole selected kernel finishes, while 10k/50k CTA-issued coverage is only 31.25%.

Existing frozen telemetry cannot associate a translation fill cycle with subsequent requester keys. Therefore this stage does not quantify cold-first-touch fraction, post-fill hit rate, or page revisit intervals in simulator-cycle units. No timing-neutral instrumentation was added, so no D3 equivalence replay was required.