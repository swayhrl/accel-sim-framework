# IO duplicate-after-eviction source semantics

Status: **C0 PASS**

Evidence class: **SOURCE_PROVEN**. This audit uses the accepted Core source
commits represented by FAST12 IO: `bbcbb5e7565417102087bc80b14c349b4e568c05`,
`95ccdb7a056f2d53f740d90869785cac6d4ee0f5`, and
`6587238c60214d99491f4048e28ce8a3458c1509`. The relevant IO source blocks
are identical across those commits.

The counter has this exact meaning:

> `DTC_L1_io_duplicate_after_eviction` increments once when an IO Tag miss
> reallocates line `L` while `m_evicted_pending_lines` still records a prior,
> pending physical identity for the same `L`. That record is installed only
> when a valid victim Tag is evicted while its physical line is not ready, and
> it is removed when that original physical identity completes. Therefore, a
> re-access after the old response is complete does not increment the counter.

This is an event counter, not a probability estimator. It is specifically a
same-128-B-logical-line reallocation event with a previously evicted response
still pending.

## Exact state transitions

| Transition | Source location | Source behavior |
| --- | --- | --- |
| Tag lookup / pending hit | `src/gpgpu-sim/dtc-l1-common.h`, `io_frontend::access`, lines 177–195 | `find_tag(line)` returns a Tag for the aligned logical line. A non-ready physical identity increments `m_pending_hits`; it does not create a new miss. |
| Pending-line Tag eviction | `dtc-l1-common.h:213–219` | On the new-miss path, a valid selected victim increments `m_tag_evictions`. If `!m_phys[victim->physical.id].ready`, the old `(line, physical_identity)` is inserted into `m_evicted_pending_lines`. |
| Pending-address tracking | `dtc-l1-common.h:216–217,370` | `m_evicted_pending_lines` is a `std::map<uint64_t, physical_identity>` keyed by the victim's aligned logical-line address and retaining its generation-qualified physical identity. |
| Duplicate test and increment | `dtc-l1-common.h:220–234` | `m_evicted_pending_lines.erase(line)` is executed only on the successful Tag-miss allocation path. A nonzero erase increments `m_duplicate_after_eviction`, then a new pending physical identity is installed and the function returns `NEW_MISS`. |
| Same-line reallocation | `dtc-l1-common.h:224–234` | The selected Tag is overwritten with `(valid=true, line, new identity)`, the new physical line is marked allocated/not-ready, `m_new_misses` increments, and `NEW_MISS` is returned. |
| Old-response cleanup | `dtc-l1-common.h:237–250` | `complete(identity)` marks the original physical line ready and erases every map entry with the same physical id and generation. This happens before any later re-access can pass the `erase(line)` test. |
| Counter export | `src/gpgpu-sim/shader.cc:2148–2154,5595–5598` | The frontend getter is copied into aggregate statistics and printed as `DTC_L1_io_duplicate_after_eviction`. |

`complete()` matches both physical id and generation, so reusing an id cannot
clear tracking for a different allocation. Conversely, a normal re-access
that still finds the pending Tag follows the hit branch and increments only
`m_pending_hits`; it cannot reach the duplicate increment.

## One increment is one new lower-request path

The frontend returns `NEW_MISS` immediately after the possible duplicate
increment. The IO integration in `src/gpgpu-sim/shader.cc:2979–2992` appends
exactly one DTC lower candidate only for `NEW_MISS`. Later,
`dtc_l1_io_issue_lower_requests()` at `shader.cc:3011–3045` atomically acquires
a lower credit, allocates one `mem_fetch`, records its distinct request UID in
the IO in-flight map, and increments `m_dtc_l1_io_lower_created` once.

The candidate queue is capacity-reserved before frontend mutation
(`shader.cc:2961–2972`), so this is not a post-allocation failure path. The
accepted terminal rows additionally enforce
`io_lower_created == io_lower_issued == io_lower_responses`
(`shader.cc:5541–5550`). Thus every retained FAST12 counter increment is bound
to one distinct completed lower-request creation, rather than to a duplicate
response or a post-response cold re-access.

## Request-size audit

`dtc_l1::kLogicalLineBytes` is explicitly `128` in
`src/gpgpu-sim/dtc-l1-common.h:22`. On lower creation, the IO code constructs
one `mem_access_t whole_line` at the aligned candidate line address with size
`dtc_l1::kLogicalLineBytes` (`shader.cc:3020–3028`). Its byte and sector masks
are both set. The response path requires all four 32-B sectors before it calls
`complete()` and retires the lower transaction (`shader.cc:3069–3087`).

Therefore `duplicate_after_eviction * 128` is source-proven **duplicate lower
request payload bytes**. It is not asserted to be total network traffic: the
counter and these source lines do not establish packet headers, interconnect
flits, reply payload accounting, or writeback traffic. The Lane-C table labels
this distinction explicitly and does not report an unsupported total-traffic
byte figure.
