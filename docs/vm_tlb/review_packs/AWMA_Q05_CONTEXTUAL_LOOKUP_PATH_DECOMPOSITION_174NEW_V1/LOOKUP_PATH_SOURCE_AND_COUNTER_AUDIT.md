# Lookup-path source and counter audit

Natural P34 has 776915 L1 lookup requesters, 773501 L1 hits, 3414 L1 misses, and 3165 L2 hits. The modeled service totals are 7769150 (=776915×10) L1 cycles and 273120 (=3414×80) L2 cycles. Requester-latency composition is summed requester cycles—not exposed GPU cycles—and is never converted directly to a speedup prediction.

L1 hit rate is 99.56%; L2 hit rate among L1 misses is 92.71%; L2 misses/requesters are 0.032%; walk allocations/requesters are 0.0019%. This supports lookup-path sensitivity diagnosis, not a hardware-latency claim.
