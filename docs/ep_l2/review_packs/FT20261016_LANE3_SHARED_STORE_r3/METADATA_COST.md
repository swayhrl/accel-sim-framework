# RO metadata accounting — bounded completion, not free MSHRs

Data: no new array or allocator. Primary 1168 x 128B / slice, sensitivity 1160 x 128B; landing belongs to the sole shared pool and remains pinned through last fill/read/response. Both paths consume the same 512-requester descriptor pool.

| Item | Bound and accounting |
|---|---|
| Native Line-MSHR occupancy avoided | At most 128 existing entries/slice; detach-only retains these entries, bypass mode allocates none for RO |
| Completion identity/line/masks | One record indexed by each physical payload ID, at most 1168 rows; every live transaction has at least one shared descriptor, so active transactions are additionally bounded by D512. No independent unbounded address map |
| Completion fields | Canonical line address (A-7 bits), epoch token E, attached Tag index 10, Tag generation Gt, payload generation Gp, required/issued/ready 12 bits, attachment/reuse flags, waiter head/tail/count and response-grant control |
| Waiters | At most 512 live descriptors globally, max 32/address across native/attached/detached; head/tail need 9 bits, count representing 0..32 needs 6 bits |
| Shared descriptor hook | External-owner bit plus canonical line/generation in software; report physical reuse/union or incremental cost, not free duplicated metadata |
| Native MSHR hook | One RO-owner flag/entry plus shared external-descriptor count; existing map capacity remains 128 |
| Response data | No per-transaction data buffer; source payload stays pinned, failed enqueue retries a bank read |
| Oracle | Offline preprocessing and ideal runtime annotation/membership input. Not claimed as existing hardware; compiler/runtime support and annotation cost remain separate |

The straightforward indexed completion upper-bound formula is N_payload * [(A-7)+E+10+Gt+Gp+12+attachment/reuse/control+9+9+6+response-control] bits before exploiting fields already in the common payload sidecar. Counted waiter records stay in the existing shared pool. Net benefit requires subtracting only the actually removed native line fields and adding all retained/new completion state. This source has not established lower total metadata area.

C++ unsigned/uint64_t widths and vector/object sizeof are not physical PPA. Payload ABI rejects live-generation aliasing; final G/E widths and wrap/reclamation proof must accompany a physical implementation. No fabricated area, energy or speedup result is supplied.

## r3 shared-store delta

The common store gains an RO allocation class and explicit attached/detached states, included once in live-slot accounting. Pending/ready masks, generation and pins are reused. Two RO bank-operation counters are instrumentation only. A transient return callback borrows the existing packet version pointer and never persists copied data. The production test uses symbolic sector-version validation, while the earlier independent module test uses a byte reference. Exact physical encoding/cost and real Tag/memport dispatch remain final integration work.
