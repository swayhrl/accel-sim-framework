# First simulator mechanism specification

## Placeholder name

`ORACLE_ELASTIC_QWEIGHT_RESIDENCY_V1`

This is a modeling specification, not an implementation authorization or a claim about NVIDIA replacement policy.

## Target-tag semantics

A memory request is target-tagged when the current address presented to L2 by `mem_fetch::get_addr()` lies in an explicitly supplied, exact qweight allocation interval selected for the experiment. The sidecar must declare intervals in that same modeled address namespace. Preserved SimVA is not available through the current L2 interface and must not be assumed. The lookup excludes PTE traffic, synthetic VM requests, instructions, writebacks, and all unlisted allocations. The first experiment uses this oracle/software tag only.

## Line metadata and quota

- One `protected` bit per valid L2 line.
- Optional small target-class ID for statistics only; replacement correctness must not depend on it.
- Per-L2-instance protected occupancy counter.
- Per-L2-instance protected line quota. A global requested byte budget is converted to `ceil(bytes / line_bytes)` lines and distributed by quotient/remainder across instances so the sum is exact.
- Invalid lines never count as protected.

## Opt-in configuration

- `enable_oracle_elastic_qweight_residency` (default false).
- `protected_quota_bytes` or a mutually exclusive exact line quota.
- interval-sidecar path and accepted sidecar SHA.
- optional target-class statistics switch, separately diagnostic.

With the mechanism disabled, allocation, hit/update, victim choice, fills, cycles, ordering, and statistics other than explicit opt-in diagnostics must match the accepted baseline.

## Insertion and replacement

1. Prefer invalid lines exactly as the baseline does.
2. For a tagged fill while protected occupancy is below quota, prefer a non-protected victim chosen by baseline recency.
3. For a tagged fill at quota, choose a protected victim by baseline recency; occupancy remains bounded.
4. For an ordinary fill, choose a non-protected victim by baseline recency when one exists.
5. If every eligible valid candidate is protected, use baseline recency across those candidates as bounded fallback.
6. A tagged fill sets `protected`; an ordinary fill clears it. Eviction/invalidation decrements occupancy exactly once when the departing valid line was protected.

No new tag-match, hit-latency, data-port, MSHR, or memory-ordering behavior is introduced.

## Hit/update behavior

All hits retain baseline replacement-state updates. A hit does not promote an ordinary line merely because the current request is target-tagged; protection is assigned on fill so aliases and stale metadata cannot silently change occupancy. A later experiment may evaluate promotion, but it is outside V1.

## Overflow, borrowing, and lifetime

- Protected occupancy must never exceed quota.
- Ordinary lines borrow every unused slot automatically.
- Protected lines compete with one another using baseline recency once quota is full.
- Protection lasts until eviction, explicit cache invalidation, context/reset behavior already modeled by the baseline, or an explicitly modeled interval-authority reset. There is no guessed hardware timer.
- Removing/changing an oracle interval does not retroactively retag resident lines unless the experiment explicitly performs a validated reset.

## Statistics

- target-tagged L2 accesses, hits, and misses;
- protected fills and protected hit count;
- protected/non-protected victim counts by incoming request class;
- protected occupancy current/max and quota-full events;
- ordinary borrowing occupancy;
- protected-protected replacement count;
- fallback eviction of protected line by ordinary fill;
- counters by optional target class without changing behavior.

## Required invariants

- `0 <= protected_occupancy <= protected_quota_lines` per L2 instance;
- occupancy equals the number of valid protected lines;
- one eviction/invalidation changes occupancy at most once;
- no untagged fill becomes protected;
- no tagged fill outside the validated intervals;
- disabled mode is cycle/counter/order transparent except opt-in diagnostics;
- VM/PTE and synthetic request identities remain separate;
- cache request conservation and baseline MSHR behavior remain unchanged.

## Evidence boundary

The mechanism tests whether a bounded, selectively protected residency class can reproduce the local/shared timing envelope. It does not claim target-specific DRAM behavior, identify a final autonomous classifier, or emulate CUDA's undocumented replacement implementation.
