# C2P peer-locality diagnostic contract

This diagnostic isolates why the local redundant-L2 opportunity rate can
differ from the C2P-Cache paper.  It is enabled only with
`-c2p_cache_peer_locality_diagnostic 1` and is observation-only: no cache
state, replacement metadata, resource credit, request route, latency, or
completion path may depend on its results.

## Eligible event

An accepted L1 `MISS` for a non-atomic `GLOBAL_ACC_R` request is first
classified as either a new lower request or an MSHR merge.  The latter has no
lower request and is reported only in the accepted/Merge split.  A physical
lower request is sampled twice:

- **detect**: at the common miss-queue insertion point used by every normal
  read-allocation path;
- **issue**: when the same miss reaches the L1 miss-queue head and C2P's
  existing lower path actually calls `m_memport->push()`.

Detect and issue records are keyed by the original `mem_fetch` and must match
one-to-one for a qualified oracle run.  Locating detect at queue insertion,
rather than in one L1 access wrapper, is required because a few normal lower
allocation paths create their `mem_fetch` inside the cache implementation.

The implementation uses the common `baseline_cache` hooks immediately after
`m_miss_queue.push_back()` and immediately after `m_memport->push()`.
`-c2p_cache_peer_locality_diagnostic` defaults to zero; with that default the
hooks return before scanning any peer or modifying any C2P statistic.  With
the overlay enabled, the only reused value is the exact issue-time mask for
the already-existing oracle decision; paired baseline/oracle controls must
therefore retain identical cycles and lower traffic before a diagnostic run
may be accepted.

## Peer masks

For requester SM `r`, the scan excludes `r` and returns a 64-bit logical-SID
mask.  The primary opportunity definition is:

`P_sector = { s != r | L1_s returns HIT for the requested sector }`.

`P_line = { s != r | L1_s has the matching valid line tag }` is a diagnostic
counterfactual.  A matching tag with an absent requested sector is recorded as
`SECTOR_MISS`; a pending fill is recorded as `HIT_RESERVED`; neither is a
usable peer copy.

## Locality

Logical clusters are fixed for statistics only:

`cluster(sid) = floor(sid / 8)`.

For each redundant request (`P_sector` nonempty), it is exactly one of:

- `local_only`: peer copies only in requester's logical cluster;
- `outer_only`: peer copies only outside it;
- `both`: peer copies in both regions.

The report gives both conditional probability given redundancy and the
unconditional fraction of all eligible misses.

`abs_distance = abs(peer_sid - requester_sid)` is the primary logical-SID
distance.  Ring distance and signed SID delta are separate secondary views;
none are physical NoC latency in the current model.

## Required invariants

For each semantic/time snapshot:

```text
events = peer_count[0] + redundant_events
redundant_events = local_only + outer_only + both
redundant_events = sum(peer_count[1..63])
sum(nearest_abs_distance) = redundant_events
sum(all_abs_distance) = sum(k * peer_count[k])
local_peer_total + outer_peer_total = sum(k * peer_count[k])
```

The exact-sector mask must be a subset of the resident-line mask, and the
requester bit must be clear in all masks.  For issue-time records,
`detect_records = issue_records`; all accepted L1 misses split
into `detect_records + l1_mshr_merge_records`.  Qualified
paper16 runs require 64 registered L1s, no missing detect record at issue, and
no pending detect record at simulator exit.

## Configuration sensitivity

The canonical current point is `16 sets x 32 ways x 128 B = 64 KiB`.  Six
high-discrepancy workloads additionally use:

- Table-1 literal: `4 x 32 x 128 B = 16 KiB`;
- four-set 64 KiB: `4 x 128 x 128 B = 64 KiB`.

These are diagnostic points only.  They do not relabel any local workload as a
paper class.
