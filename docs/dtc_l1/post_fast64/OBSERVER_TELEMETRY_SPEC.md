# Post-FAST64 observer telemetry specification

Status: `D0_SPECIFIED`. This is observer-only diagnostic instrumentation for
the Lane-B B4 gaps and the Lane-C C4 OO semantic gap. It is not a FAST64
result and does not authorize a mechanism change or a replacement run.

## Authority and scope

The accepted authority remains
`hrl/decoupled-l1-fast64-v0@18a68dcccd795f1b6cda75504e9450d00c9cee02`.
The requirements are consumed from Lane B's
`LANE_D_TELEMETRY_REQUIREMENTS_FROM_LANE_B.md` and Lane C's
`DUPLICATE_MISS_HANDOFF.md` after their lane commits are integrated. All
future rows use `POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`.

The default-off parser option is `-gpgpu_dtc_l1_post_fast64_telemetry 0`.
When disabled, observer maps are not populated and every field below that is
new to the observer prints as zero. The accepted
`DTC_L1_io_duplicate_after_eviction` field is deliberately not in that set:
it is an existing FAST64 scientific counter and remains part of the exact
off/on equality comparison.

## Required counter families

| Counter family | Increment / timing definition | Cleanup and aggregation | Question it observes |
| --- | --- | --- | --- |
| `DTC_L1_{io,oo}_alloc_to_ready_{count,sum_cycles,max_cycles}` | Save the global cycle at each successfully committed whole-line `NEW_MISS`, keyed by existing `{physical id,generation}`. At that identity's matched successful response completion, add `response_cycle - allocation_cycle` exactly once. Exclude valid/pending hits, allocation-width retries, no-free retries, and stale fills. | Remove the allocation record at that matched completion. Counts/sums aggregate by addition; max is the maximum across SM-local observers. | The absent L2-pressure-to-pending-lifetime exposure for H3/H4. |
| `DTC_L1_{io,oo}_pending_tag_evictions` | Increment once when a valid logical Tag victim's physical allocation is `!ready`, immediately before the normal logical Tag replacement. | The event itself holds no new persistent record. Counts aggregate by addition. | The absent pending-Tag-eviction denominator for H3. |
| `DTC_L1_io_pending_eviction_to_response_{count,sum_cycles,max_cycles}` | At the IO pending-Tag-eviction event, save its cycle by identity. At the matching original response, add `response_cycle - eviction_cycle` once. | The allocation record is removed at that matching completion. Counts/sums add; max is the SM-local maximum. | The response-wait exposure after an IO pending Tag eviction in H3. |
| `DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_{count,sum_cycles,max_cycles}` | At a valid OO Tag eviction whose physical line has `ref_count > 0`, save the eviction cycle by identity. At that exact Tag-invalid identity's final-reference reclaim, add `reclaim_cycle - eviction_cycle` once. Immediate zero-reference reclaim is excluded. | The deferred-reclaim record is removed only at its matching final reclaim. Counts/sums add; max is the SM-local maximum. | The missing OO deferred-reclaim lifetime for H4. |
| `DTC_L1_oo_duplicate_after_eviction` | For a valid pending OO Tag victim, record `(line,identity)` only in observer state. On a later successful same-line `NEW_MISS` before the original completion, erase the record and increment once. A pending Tag hit, failed allocation, stale fill, and post-response re-access cannot count. | Remove all matching line records at original completion; identity includes generation to prevent recycled-slot joins. Count aggregates by addition. | The exact OO counterpart requested by Lane C; no accepted OO proxy is used. |
| `DTC_L1_{io,oo}_observer_live_records` | Snapshot of remaining observer allocation/deferred-reclaim records at terminal output. | Sum across SM-local observers; it must be zero in every retained terminal row. | Conservation/drain of the observer itself. |

## Isolation and validation contract

Observer data may be written and printed only. It is never read by Tag lookup,
victim selection, admission, allocation/free choice, retirement, reclaim,
lower scheduling, response routing, completion ownership, or a return value
used by those decisions. It has no production assertion or timeout effect.

Each observer Core is rooted at its accepted parent (Core95 for non-2D and
Core658 for 2D). Directed tests must cover positive and negative OO duplicate
cases, pending-tag event accounting, a deferred OO final-reclaim duration,
an immediate-reclaim exclusion, allocation-to-response arithmetic, identity
reuse safety, and terminal zero live records. Before any retained diagnostic
row, D3 must show exact telemetry-off/on equality for cycles, instructions,
all pre-existing compact scientific fields (including IO duplicates), lower
and dependency accounting, and terminal drain on NN and Btree.
