# EP-L2 Research Charter

## Primary objective

EP-L2 is an L2-cache architecture project. Its primary objective is not to maximize one benchmark's end-to-end speedup in isolation. The architectural objective is:

> **At comparable L2 storage budget and basic L2 timing, improve the L2's effective capacity for concurrent misses, pending transactions, and payload state, and reduce structural blocking caused by static resource/lifetime coupling.**

The project should seek end-to-end speedup whenever the rest of the memory system has sufficient headroom, but must distinguish L2-local architectural improvement from system-level bottleneck substitution.

## Why this objective is necessary

A structural L2 change can be correct and useful even when application cycles move little if the removed L2 bottleneck exposes another bottleneck in L1, the L2-to-DRAM path, the DRAM scheduler, memory bandwidth, WAD, or another resource. Conversely, a large raw counter reduction is not enough by itself: the project must show that the counter represents a real structural demand/block relation or service delay rather than repeated retry bookkeeping.

## Success hierarchy

### Level 1 — L2 structural pressure improvement

Examples:

- lower `descriptor_pool_full_block / descriptor_need`;
- lower `line_mshr_full_block / line_mshr_need`;
- lower `tag_way_alloc_block / tag_way_alloc_need`;
- lower `per_address_cap_block / per_address_cap_check`;
- lower payload-capacity/service blocking when the corresponding demand exists;
- reduced near-full/full occupancy time and long high-average pressure windows.

This level supports the claim that the L2 is structurally less constrained.

### Level 2 — L2 service effectiveness improvement

Examples:

- more useful transactions admitted without increasing invalid/retry work;
- lower structural wait cycles or request-age/lifetime;
- higher sustained useful concurrency;
- fewer L2-local retries/stalls for the same trace;
- pressure shifts from an artificial L2 resource ceiling to a true downstream resource.

This level supports the stronger claim that the L2 not only has fewer blocker events but serves the same workload more effectively.

### Level 3 — system performance improvement

Examples:

- fewer application cycles;
- higher IPC/throughput;
- speedup preserved across representative workloads and realistic configurations.

This is the strongest outcome but is not required to prove every Level-1/2 architectural claim. When Level-1/2 improve but Level-3 does not, the project must explicitly identify the newly exposed bottleneck rather than imply hidden performance benefit.

## Required scientific discipline

1. Do not tune resource sizes merely to manufacture an MSHR-, descriptor-, or payload-centric story.
2. Do not call occupancy saturation a causal bottleneck without exact blocker/wait evidence or a controlled headroom experiment.
3. Do not equate retry-event counts with unique requests or stalled cycles unless their semantics explicitly support that interpretation.
4. Separate simulator-model claims from claims about physical NVIDIA hardware.
5. Every mechanism claim must report both the intended L2-local effect and the movement of downstream pressure.
6. A mechanism that only moves a bottleneck is still informative, but must be labeled as bottleneck substitution rather than performance improvement.

## Non-goals

The current project is not trying to:

- reproduce an undocumented commercial GPU cache exactly;
- maximize speedup by arbitrarily enlarging all queues/resources;
- change L1, DRAM, traces, and L2 simultaneously until a desired result appears;
- treat speculative calibration data as a primary baseline without a reviewed baseline decision.

## Current working architecture thesis

The broad EP-L2 thesis is that **Tag state, pending/requester metadata, MSHR-like transaction state, and physical payload ownership have different useful lifetimes and should not be unnecessarily coupled.** Static coupling can cause one resource to block new work while another still has useful capacity.

The eventual mechanism set may include payload pooling/borrowing, more flexible pending-tag state, RO paths that avoid traditional MSHR allocation where semantically safe, and WAD/TVD-style payload decoupling. Each mechanism must be justified by measured opportunity and controlled sensitivity rather than by this thesis alone.
