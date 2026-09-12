# Lane B0 — physical-pool source audit

Classification: `SOURCE_PROVEN`

This audit reads the Core revision used by every non-2D accepted Stage6 physical row:

- Core: `hrl/decoupled-l1-m5-v0@95ccdb7a056f2d53f740d90869785cac6d4ee0f5`
- Frozen Framework authority: `hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e9450d00c9cee02`
- Scope: whole-line `PAPER_IO` and whole-line `PAPER_OO`; the physical sweep uses these modes, not `MODERN_OO_SECTOR`.

No simulator code was changed and no simulation was launched for this audit.

## Exact source behavior

| Concern | Source evidence | Source-proven behavior |
| --- | --- | --- |
| Physical identity | `src/gpgpu-sim/dtc-l1-common.h:93-100` | `physical_identity` is exactly `{ id, generation }`. The generation distinguishes a recycled slot from an older allocation. |
| IO physical free-line selection | `dtc-l1-common.h:204-211,354-357` | IO scans `m_phys` from `m_rr_next`, chooses the first unallocated slot, and advances the round-robin cursor. No-free returns `NO_FREE_LINE` and increments the IO no-free counter. |
| OO physical free-line selection | `dtc-l1-common.h:477-498,782-790` | OO performs the same round-robin free-slot scan. If no slot is free, only a zero-reference victim can first be reclaimed; otherwise it returns `NO_FREE_LINE`. |
| Tag set and victim | `dtc-l1-common.h:343-352` (IO); `759-780` (OO) | Both modes derive the logical set from `line / 128B`, return an invalid way if available, otherwise choose the least-recently-used way by the logical Tag `lru`. Physical ID does not participate in set or victim selection. |
| IO Tag eviction | `dtc-l1-common.h:213-223` | A valid victim increments Tag evictions. If its physical line is not ready, the logical line and physical identity are recorded in `m_evicted_pending_lines`. Reallocating that same logical line before the original response completes increments `m_duplicate_after_eviction`. |
| IO release on retirement | `dtc-l1-common.h:218,261-268,359` | Evicting a valid IO Tag appends its identity to the current entry’s `release_on_retire`; physical release occurs only when that FIFO head is ready and retires. `release()` clears `allocated` and `ready`, preserving generation checking. |
| OO Tag eviction and reclaim | `dtc-l1-common.h:485-512,792-799` | OO clears `tag_valid` on a victim. A zero-ref victim is released immediately and counted as immediate reclaim; a live-ref victim is counted as deferred reclaim and remains allocated. |
| OO final-reference reclaim | `dtc-l1-common.h:541-571,577-603` | Any ready entry may retire, at width one/cycle. Each reference is decremented; an already tag-invalid physical line is released only when the final reference reaches zero, incrementing final-ref reclaim. |
| OO wakeups | `dtc-l1-common.h:523-539,739-750` | Each pending reference is registered as a waiter. A matched fill makes the allocation ready, closes each waiter dependency, increments wakeups, and clears the waiter list. |
| Lower request generation | `src/gpgpu-sim/shader.cc:2929-3004,3011-3045` (IO); `3193-3289,3292-3346` (OO) | A `NEW_MISS` enqueues `{physical, line_address}`. The lower `mem_access_t` is constructed with `candidate.line_address` (IO) or `request_address` derived from `candidate.line_address` (OO). `physical` is placed only in the DTC inflight record for response validation/completion. The lower create and issue queues are FIFO; their scheduling uses queue front and interconnect availability, not physical ID. |
| Response completion | `shader.cc:3061-3098,3349-3382` | On a matched response, the stored physical identity is passed back to `complete()` / `complete_sector()` only to make that exact allocation ready and protect against stale/recycled fills. |
| L2 partition mapping | `src/gpgpu-sim/mem_fetch.cc:75-81,124-127`; `src/gpgpu-sim/addrdec.cc:79-94,96-130` | A `mem_fetch` maps `access.get_addr()` into raw partition fields and partition address. It receives no physical identity. |
| L2 set mapping | `src/gpgpu-sim/gpu-cache.cc:77-80,162-170` | L2 set index is a hash of the request address after partition-bit removal. It receives no physical identity. |

## H5 disposition — physical-ID mapping hypothesis

`H5 = DATA_DOES_NOT_SUPPORT / SOURCE_PROVEN_INERT`.

`physical_identity.id` is an internal `m_phys` vector index. The exhaustive Core95 use outside the frontends is storage in the DTC candidate/inflight records (`shader.cc:2991,3032,3084,3264,3278,3327,3373,3375`). Those uses preserve allocation-generation identity until the response completes; none is used to form request address, L2 set, memory partition, or queue priority.

The request path instead passes the logical `line_address` into `mem_access_t`, and both partition and L2 set mapping derive from `access.get_addr()`. Therefore a direct hypothesis of “physical free-list index changes L2 address/set/partition mapping or lower-request ordering” is ruled out by source. This does not rule out an indirect timing effect: pool availability can still determine whether a logical miss is admitted at a given cycle.

## Counter-semantic caveat retained in Lane B

The accepted IO raw field `DTC_L1_io_physical_free_minimum_per_sm` must not be interpreted as a true zero-sensitive global minimum. `paper_frontend_stats::add()` takes a minimum only when `other.io_physical_free_minimum` is nonzero (`dtc-l1-common.h:1495-1499`), so an SM-local zero can be lost during aggregation. The Lane-B raw table retains the field as `physical_free_minimum_per_sm_reported`; it is not used as evidence that a pool never reached zero free lines. `physical_allocated_peak_per_sm`, in contrast, is explicitly aggregated with `max` (`1492-1494`).

The accepted compact schema does not export OO no-free events, OO allocation-width events, OO physical peak, or OO minimum-free values, although the first two counters exist in the frontend implementation. Those cells are explicitly marked `NA_NOT_REPORTED_IN_ACCEPTED_COMPACT` in Lane-B tables.
