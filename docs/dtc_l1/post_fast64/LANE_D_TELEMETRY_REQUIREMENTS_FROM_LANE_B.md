# Lane B -> Lane D: minimum observer-only telemetry requirements

Status: `B4_SPECIFIED_NOT_YET_OBSERVER_QUALIFIED`

Lane B needs only the following four counter families. They close the named gaps below; they are not authorization for a broad diagnostics suite or a mechanism change. The existing separate observer Core branches are the intended implementation locations: Core95-rooted `hrl/dtc-l1-post-fast64-observer95-v0` for these non-2D workloads (and the Core658 branch only if a 2D extension is later requested).

| Required observer family | Exact event semantics | Named arrow/hypothesis closed | Why existing Stage6 is insufficient |
| --- | --- | --- | --- |
| `DTC_L1_{io,oo}_alloc_to_ready_{count,sum_cycles,max_cycles}` | On each successfully committed physical `NEW_MISS`, save cycle keyed by `{id,generation}`. On the matching successful `complete()`, add `complete_cycle - allocation_cycle`; count each identity once. Do not count allocation-width/no-free retries, valid hits, or stale fills. | L2 pressure -> pending lifetime; H3 | Stage6 has pending-hit counts, not allocation-to-ready duration. Pending hits are not a lifetime denominator or latency proxy. |
| `DTC_L1_{io,oo}_pending_tag_evictions` | Increment exactly when a valid victim’s matching physical allocation is `!ready`, immediately before logical Tag replacement. IO location: `io_frontend::access`, Core95 `dtc-l1-common.h:213-218`; OO location: `oo_frontend::access`, `485-495`. | pending lifetime -> pending Tag eviction; H3 | Stage6 exports all Tag evictions but cannot distinguish evicting a ready Tag from evicting a pending Tag. |
| `DTC_L1_io_pending_eviction_to_response_{count,sum_cycles,max_cycles}` | When an IO pending Tag is evicted, save the eviction cycle keyed by that victim identity. When the matching original response completes, add `response_cycle - eviction_cycle`; count once. Cleanup on matching completion only. This observes response wait after a pending eviction; it does not infer a duplicate. | pending Tag eviction -> duplicate-traffic exposure; H3 | Existing IO duplicate count proves a reallocation occurred before original completion, but lacks the size of the exposed interval and the pending-eviction denominator. |
| `DTC_L1_oo_deferred_tag_eviction_to_final_reclaim_{count,sum_cycles,max_cycles}` | On an OO Tag eviction with `ref_count > 0`, save cycle keyed by victim identity. On the matching final-ref `release()`, add `reclaim_cycle - eviction_cycle`; count once. Immediate zero-reference releases are excluded: this family is specifically the deferred lifetime. | OO Tag eviction/lifetime -> exposed concurrency; H4 | Stage6 has aggregate deferred and final-ref reclaim counts but no elapsed lifetime between the paired events. |

## Observer safety and qualification contract

Each family is observation state only. It may write counters/timestamps and print them, but must never affect return values, allocation/free selection, Tag lookup/victim choice, admission, retirement, lower scheduling, completion, or assertion behavior. Every timestamp record is keyed by existing `physical_identity {id,generation}` solely to prevent stale/recycled joins.

Before any B5 row, Lane D must satisfy the post-FAST64 observer-equivalence gate on NN and Btree (or a source-justified equivalent): exact cycles, instructions, all pre-existing compact counters, lower/dependency accounting, and terminal drain must match telemetry-off/reference. Retained rows must use `POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT` and record the required Core, runtime, config, and runner identities.

After equivalence, the smallest informative B5 wave is exactly the Lane-B matrix not already covered by telemetry: BICG, GESUMMV, Btree at 24/32/48 KiB, in IO and OO. Do not run an exact telemetry-covered point twice. No B5 result is needed for the present Lane-B evidence classification.
