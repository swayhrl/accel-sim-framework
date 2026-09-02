# DTC-L1 Counter, Event, Invariant, and Debug Specification

Purpose: make correctness failures and performance bottlenecks explainable from the first implementation stages.

Counters should be emitted per kernel and aggregate; per-SM detail should be available where useful. Names may follow existing style, but semantic coverage below is required.

---

# 1. Result identity / provenance

Every machine-readable run summary must record:

- Core SHA;
- Framework SHA;
- mode (`LEGACY`, `PAPER_BASE`, `PAPER_IO`, `PAPER_OO`, sector diagnostic);
- config identity/hash;
- trace/workload/input identity/hash where available;
- kernel identity;
- result classification.

---

# 2. Basic dynamic operation counters

Count unique dynamic operations/events, not stall-cycle re-observations:

- memory instructions seen/created;
- memory instructions admitted to the modeled lifecycle;
- memory instructions retired/completed;
- loads;
- stores;
- atomics;
- fences;
- architectural bypass operations;
- active threads;
- coalesced 128B line references;
- sector references.

Required histogram:

- line references per memory instruction, at least bins 0..32/overflow.

For sector mode also record sectors requested per 128B line reference.

---

# 3. Access classification

Common/DTC access classes:

- valid hit;
- pending hit;
- new miss.

Baseline-specific where source exposes them:

- hit-reserved/pending equivalent;
- reservation failure;
- MSHR entry full;
- MSHR merge full.

DTC-specific:

- no free physical line;
- lower-request capacity block;
- allocation-width block.

---

# 4. PIB metrics

For every explicit paper PIB/buffer:

- admits;
- retires;
- current occupancy;
- occupancy cycle-sum;
- peak occupancy;
- occupancy histogram;
- full cycles;
- full transition/events;
- instruction lifetime histogram/summary.

Derived:

`avg_occupancy = occupancy_cycle_sum / active_cycles`.

At completed-kernel drain, admitted-retired accounting must close for all operations that are specified to use the PIB.

---

# 5. Stall accounting: two parallel views

## 5.1 Primary stall reason

Exactly one primary reason may be charged to a frontend-stall cycle. Required categories where applicable:

- PIB_FULL;
- TAG_BANK_CONFLICT;
- TAG_OR_LINE_ALLOC_FAIL;
- MSHR_ENTRY_FULL;
- MSHR_MERGE_FULL;
- PHYS_NO_FREE;
- ALLOC_WIDTH_FULL;
- LOWER_REQUEST_CAP_FULL;
- LOWER_ISSUE_BW;
- RETIRE_BW;
- ORDERING_FENCE;
- OTHER.

For the defined frontend-stall domain:

`sum(primary_reason_cycles) == total_frontend_stall_cycles`.

Document priority ordering used when multiple resources are unavailable.

## 5.2 Non-exclusive resource-unavailable view

Independently count every cycle each resource is unavailable, even if it is not the chosen primary reason:

- PIB full;
- MSHR full;
- lower-request cap full;
- no free physical line;
- Tag-bank conflict present;
- allocation width exhausted while work remains;
- lower issue bandwidth exhausted while queued work remains;
- retire bandwidth exhausted while ready work remains;
- ordering/fence blocks.

This view must not be made mutually exclusive.

---

# 6. Tag-bank metrics

- total Tag requests;
- requests per Tag bank;
- Tag service cycles;
- Tag conflict cycles;
- Tag wait cycles;
- max queued/pending Tag work if an explicit queue exists.

Expose enough information to compute bank imbalance and effective Tag throughput.

---

# 7. Physical allocation / occupancy metrics

For IO/OO:

- physical lines allocated current/peak;
- free physical lines current/minimum;
- Pending lines current/cycle-sum;
- Valid lines current/cycle-sum;
- orphan/Tag-invalid-but-live lines current/cycle-sum where meaningful;
- occupancy histogram;
- allocation attempts;
- allocation successes;
- allocation success count per cycle histogram (0..configured width);
- no-free-physical cycles;
- allocation-width-limited cycles;
- partially allocated instructions current/peak;
- total partial-allocation events;
- lines held by partial allocations current/peak;
- partial-allocation stall cycles.

Physical accounting invariant must reflect that valid tagged cachelines may remain resident at kernel completion; do not require the whole physical pool to be free unless an explicit flush is performed.

---

# 8. Lower-memory / MLP metrics

- lower requests created;
- lower requests issued;
- lower responses completed;
- read/write/atomic lower requests separately;
- current global outstanding count;
- outstanding cycle-sum;
- peak outstanding;
- outstanding histogram up to configured cap/overflow;
- per-SM issue count;
- per-SM issue-width blocked cycles;
- global outstanding-cap-full cycles;
- request queue wait latency.

Derived:

`avg_outstanding = outstanding_cycle_sum / active_cycles`.

Token accounting invariant:

`tokens_acquired - tokens_released == current_outstanding_or_queued_token_holders`.

At a fully drained completed kernel, the relevant lower-request token balance is zero.

---

# 9. DTC hit/merge/duplicate metrics

- valid hits;
- pending hits;
- new misses;
- pending-hit merged dependencies;
- lower requests avoided by pending-hit merge;
- logical Tag evictions;
- duplicate lower requests after logical-Tag eviction;
- duplicate bytes after logical-Tag eviction.

A Pending hit to the same pending read allocation must not itself create a duplicate lower read request.

---

# 10. IO head-of-line metrics

- IO head-ready cycles;
- IO head-not-ready cycles;
- cycles where head is unready and at least one younger entry is ready;
- ready-younger count cycle-sum;
- ready-younger peak;
- total blocked-ready-younger instruction-cycles.

After M4 classify HOL by head operation type:

- LOAD;
- STORE;
- ATOMIC;
- BYPASS/OTHER.

The scientifically useful HOL condition is `head_unready && younger_ready_exists`, not merely `head_unready`.

---

# 11. OO Ref Count / reclamation metrics

- Ref Count increments;
- decrements;
- current sum of live refs;
- per-line Ref Count peak;
- Ref Count value histogram/sampled distribution;
- Tag evictions with ref=0;
- Tag evictions with ref>0;
- immediate reclamations;
- deferred reclamations;
- deferred reclamation latency;
- physical orphan lifetime.

Debug invariant: independently reconstructed Shadow Ref counts must equal modeled Ref Count for every physical line while the checker is enabled.

Ref Count is line-level and follows the frozen per-coalesced-128B-reference definition.

---

# 12. OO Merge / wakeup metrics

Whole-line mode:

- merge registrations;
- merge fanout histogram;
- fill wakeups;
- merge bits set/cleared;
- maximum waiters on one physical allocation.

Sector mode:

- same counters per sector or aggregated with sector identity;
- pending-sector dependencies created/resolved;
- sector fill wakeups.

All merge registrations must clear exactly once before slot/allocation reuse.

---

# 13. Latency breakdown

For each sampled or all memory instructions as feasible, record timestamps sufficient for:

- arrival -> PIB admit;
- PIB admit -> Tag complete;
- Tag complete -> last physical allocation complete;
- allocation/Tag complete -> last lower request issue;
- request issue -> all dependencies ready;
- all dependencies ready -> retire;
- total memory-instruction lifetime.

Required aggregate distributions/means/P95/P99 where practical:

- entrance/backpressure latency;
- Tag/allocator service time;
- lower-issue queue delay;
- memory wait;
- ready-to-retire delay;
- total lifetime.

`ready_to_retire` is especially important for IO-vs-OO analysis.

After M4 provide these split by operation type where feasible.

---

# 14. Required invariants

Implement assertions/debug checks for all relevant modes:

## Common

- PIB occupancy never exceeds configured capacity.
- One dynamic memory instruction owns at most one live PIB slot/context for the modeled lifecycle.
- A non-admitted instruction cannot inject modeled L1/lower work through that lifecycle.
- A dynamic instruction retires/completes at most once.
- `wait_cnt` never underflows.
- Global outstanding count never exceeds configured limit.
- Per-SM lower issue count never exceeds configured width in one cycle.
- Kernel completion/drain cannot silently discard live modeled requests/PIB dependencies.

## DTC Tag/physical

- Every valid logical Tag maps to an allocated physical line.
- A free physical line cannot be referenced by a valid Tag.
- A physical line has at most one currently visible logical Tag owner.
- It is legal for an old physical allocation with `tag_valid=0` to remain live while refs/dependencies exist.
- Lower fill identity must match the intended physical allocation generation/UID.
- A recycled physical allocation must reject/detect stale fill.

## IO

- Only FIFO head retires.
- Head retirement requires all required read data ready.
- IO retirement sequence is monotonic in FIFO order.
- Physical release must not invalidate data still required by an earlier live instruction.

## OO

- Modeled Ref Count equals Shadow Ref Count in checker mode.
- Ref Count never underflows/overflows configured width.
- A physical line is reclaimed only when `tag_valid==0 && ref_count==0`.
- Each merge dependency is awakened exactly once.
- Merge state cannot target an invalid/reused PIB slot generation.
- Retire count in one cycle never exceeds configured width.

## Sector

- Tag->Physical mapping stays 128B line granular.
- Sector state transitions are legal.
- A single coalesced 128B line reference contributes one line-level Ref increment regardless of sector mask.
- `wait_cnt` counts unresolved required sector dependencies correctly.

## M4 operation semantics

- Atomic architectural operations are never merged/lost by read merge logic.
- Executed Atomic count/side-effect request count obeys the audited simulator semantics.
- OO retirement does not violate required Fence ordering.
- Architectural bypass does not incorrectly allocate DTC Tag/physical state.

---

# 15. Bounded debug event trace

Provide optional filtered events useful for directed tests, e.g.:

- INST_ADMIT / INST_READY / INST_RETIRE;
- TAG_REQ / TAG_HIT / TAG_PENDING / TAG_MISS / TAG_EVICT;
- PHYS_ALLOC / PHYS_RELEASE / PHYS_RECLAIM;
- LOWER_CREATE / LOWER_ISSUE / LOWER_FILL;
- REF_INC / REF_DEC;
- MERGE_SET / MERGE_WAKE / MERGE_CLEAR;
- STALL(reason);
- WATCHDOG_NO_PROGRESS.

Each event should contain cycle, SM, instruction identity, relevant line/sector/physical identity, and generation where relevant.

The trace must be disabled or tightly bounded for full workloads.
