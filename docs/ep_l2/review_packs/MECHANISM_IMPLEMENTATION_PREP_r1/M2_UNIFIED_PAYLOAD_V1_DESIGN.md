# M2 Unified Payload Pool v1 Design

## Preconditions

M1 static-equivalence must pass. M0 must produce a semantically defined bypass/pending demand trace and show time-aligned role opportunity. The present implementation has no production bypass allocation, so an M2 claim cannot be based on existing `bypass_free=128` alone.

M2 is enabled only by `ep_l2_feature_unified_payload=1` above the separately selected base-resource configuration. It must reject configuration if `ep_l2_feature_elastic_substrate=0`, if an unavailable bypass consumer is requested, or if any future M3/M4 combination is not explicitly declared composable. Feature OFF uses the M1 static-compatible path in the same source/binary family.

## Fixed physical model

One 1152-entry, 128-B pool per slice; four 288-entry banks; `bank = payload_id % 4`; one arbitrary operation per bank per cycle; existing Legacy/Banked arbitration ordering; 1024 resident tags. No new data storage, tag ways, L1 or lower-path capacity is part of M2.

## Allocation contract

Resident allocation receives a tag index and obtains any legal free global payload ID, then records it in `tag_payload_id[tag_index]`. Bypass allocation receives an explicit pending transaction handle and records the same `{id,generation}` in its owner state and its lower-return `mem_fetch`. Fill and hit service look up the handle rather than translating role-local IDs. A failed allocation has no side effects. A release removes the owner mapping before inserting the ID in its per-bank free list and increments/invalidate-generates before reuse.

## Candidate policies

| policy | benefit | unsafe/limitation |
|---|---|---|
| fully shared | maximal borrowing | resident can consume all slots and strand a required pending/bypass fill; rejected for v1 |
| shared + protected reserve | allows borrowing while preserving slots required by live/predicted bypass demand | needs an explicit, auditable reserve rule; recommended |
| watermark/hysteresis | may reduce churn | adds policy/tuning before mechanism evidence; defer to M7 |

## Recommended safe v1 policy

Use `shared_reserve` with an allocation guard: resident may allocate only if `free_total > protected_bypass_reserve`; bypass may allocate from any free slot. Start with `protected_bypass_reserve = 128` for static compatibility, not as a tuned value. M0 may lower the reserve only when it establishes an upper bound on live bypass/pending demand and the allocation protocol proves a pending request cannot need more than that reserve. The reserve is checked before tag mutation and before an MSHR/lower request whose fill needs the slot.

This preserves forward progress: a live or newly-admitted bypass path always has protected physical storage even during resident saturation. It does not reintroduce a fixed physical partition because any free ID can serve either role; it is an admission guard. An M2 experiment must report reserve denials separately from total-pool denials.

## Required invariants

- Total occupied slots never exceeds 1152; resident tags never exceed 1024.
- An in-flight fill owns one immutable `{payload_id,generation}`; stale/reused fill is rejected before tag change.
- A payload can have one role/owner until release; tag sidecar and pending-side handle agree.
- Bank mapping and one-grant/bank/cycle stay byte-for-byte logically equivalent to M1 for a given stream of payload operations.
- Bypass/pending forward progress does not require eviction of a pending resident or cancellation of a lower request.
- All policy decisions and capacity denials are observable; no retry counter is used as a denial proxy.

## Directed test families

1. Static M1 trace replay yields identical allocation IDs/bank grants.
2. Resident borrows a formerly bypass-range ID and hits/fills/releases correctly.
3. Bypass borrows a formerly resident-range ID and its fill/response/release correctly.
4. Exhaust resident allocations to the protected threshold, then admit/complete bypass; prove no deadlock.
5. Same-bank resident/bypass concurrency keeps oldest-ready bank arbitration.
6. Replacement, sector merge, dirty victim/WAD hazard, allocation rollback, and late fill each reject stale ownership.

M2 status after code/test only: implementation-ready for review; no performance claim is implied.
