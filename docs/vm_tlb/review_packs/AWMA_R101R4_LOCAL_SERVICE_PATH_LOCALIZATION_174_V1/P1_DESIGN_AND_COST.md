# P1 post-L1 local service

Arm: `P1_POST_L1_LOCAL_SERVICE`.

P1 is enabled only because P0 passed the 5% gate.

## Placement

P1 does not alter the normal L1 lookup. The original request traverses the
banked L1 latency queue and `l1_cache::access`. A read miss reserves/replaces
the normal line, allocates or merges the normal MSHR and enters the finite L1
miss queue. A write preserves its normal L1 policy outcome and lower-request
accounting.

The generic cache-cycle hook is explicitly gated by
`m_level == L1_GPU_CACHE`. L2 and other cache instances can never enter P1;
their miss queues and lower-level routing remain baseline.

At `baseline_cache::cycle`, after this state exists but before the configured
`mem_fetch_interface` injects request ICNT, a qualified request is routed to
the P1 per-LD/ST finite service.

At completion P1 calls `set_reply` on the original `mem_fetch` and enters
the existing `ldst_unit::fill` response FIFO. Reads then execute unchanged
`m_L1D->fill`, tag/fill-port bookkeeping, MSHR-ready and client-4 waiter
retirement. Writes execute the unchanged WRITE_ACK/store-ACK path. P1 does not
pretend the miss was an L1 hit.

## Fixed envelope

- scheduled capacity: 1 per LD/ST unit;
- ready capacity: 16 per LD/ST unit;
- READY eligibility: admission + 1 cycle;
- at most one ready response enters the existing LD/ST response FIFO per cycle;
- full scheduled/ready queues retain and backpressure the request;
- no request or return ICNT, L2 or DRAM service for a P1-served miss;
- nonqualified traffic follows the baseline memport.

P1 is a diagnostic oracle, not a hardware mechanism. Its service data source,
area, energy and lookup are not modeled.
