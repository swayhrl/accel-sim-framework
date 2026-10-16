# Finite service V1 — preregistration before comparative outcomes

Applies only to a new opt-in experiment identity. Default OFF preserves the existing implementation. R1 tests, rather than this document, decide qualification. Source: Core `6582b9d171330d88b17e8d5294c97704229e3823`, common/shader paths in `IMPLEMENTED_SERVICE.tsv`, and frozen `DTC_L1_SPEC.md` sections 3–5. There is no claim that these are measured RTX4080 DTC ports or latencies.

| Operation | Fixed V1 service | Basis and declared assumption |
| --- | --- | --- |
| Tag lookup | one core cycle from granted lookup to commit; four banks, one/bank/cycle, four total | Frozen bank width and one-cycle stage abstraction. Repeated LD/ST calls cannot refresh the same-cycle quota. |
| Physical allocation | at most four successful lines/core-cycle, at lookup commit | Existing source/frozen RR allocator. Partial allocation and same-cycle release visibility preserved. |
| Lower injection | one candidate creation and one ICNT injection/SM/core-cycle | Frozen one-request width; enforce absolute-cycle quota rather than relying on LD/ST invocation count. |
| 32B refill | one DTC sector/SM/core-cycle | Conservative global single 32B refill port, using the source's 32B transfer unit. This is an assumption, not a measured bank map. Other response ownership and conventional path routing stay intact. |
| 128B data-ready | final distinct 32B response plus one core-cycle stage | Four distinct sectors remain required. Preserve request/physical generation identity and exact duplicate rejection. |
| OO waiter updates | at most four attached PIB waiters/core-cycle across returning lines, after the readiness stage | Explicit conservative metadata-port assumption. A returning physical allocation becomes observable-ready only after its waiter work finishes. Do not expose a partly updated line as ready. New pending merges keep the same physical generation. |
| Ready selection | one core-cycle before collection starts | Bounded IO head or OO eligible-ready selection; no retirement before full reference admission, and no bypass of same-warp fences. |
| Data collection | four 32B sectors/SM/core-cycle; amount is the union of sectors actually referenced by the instruction | Conservative aggregate 128B/cycle transfer capacity. No invented Data-bank mapping. This transfer is separate from refill and writeback. Store no extra architectural values. |
| Writeback/retirement | at most one instruction/core-cycle, conditional on the existing shared operand collector | Both IO and OO require an absolute-cycle success guard. A failed writeback consumes no completion or reclamation ownership. |
| Last-Ref update/reclaim | atomic at successful retirement; up to 32 line-reference updates per instruction, bounded by 32-lane coalescer | Preserve per-line Ref semantics and same-cycle allocation visibility. Declare a 32-lane metadata update fabric and bounded generation/slot bookkeeping as resource cost; it is not free, equal area, or a serialized post-retire release queue. |

These values are fixed before observing V1 comparative outcomes. They must not be tuned to restore historical speedups. The ready-selection and waiter structures are bounded by configured PIB depth; report the depth and update fabric separately from data bytes. Traditional PIB/MSHR growth also requires explicit resource accounting. No equal-area claim is authorized by this contract.

Required R1 evidence: successful-only quota consumption where applicable; pending merge; replaced-Tag return; repeated-sector rejection; no same-step early completion; writeback backpressure; last-reference reclaim; slot reuse; bounded legal-domain progress; exact small OFF checks. Failures retain immutable attempts. A protocol, ordering, value, instruction-support, reference-granularity or legal-capacity change requires review before implementation. Timing holds may lengthen residence but cannot redefine allocation legality or silently drop a return.

V1 measurement contract: fully-admitted-and-ready timestamp precedes collection; retirement timestamp requires successful writeback; record ready-to-collection, collection service, writeback wait, map-loss-to-free and per-core-cycle occupancy integrals separately. Existing frontend-ready counters remain historical counters and must not be renamed to these metrics.
