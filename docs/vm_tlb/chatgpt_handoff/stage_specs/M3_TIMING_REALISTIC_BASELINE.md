# M3 — Timing-Realistic Single-GPU VM Baseline

## Objective

Replace M2's fixed-latency functional page-walk service with a timing/resource model in which page-table activity consumes realistic simulator resources, then close out a reusable single-GPU VM/TLB/PTW baseline for later LLM work.

M3 remains a resident-memory address-translation study. It does not add page faults, migration, UVM oversubscription, segmentation, or MCM behavior.

## Architectural boundary

The VM core must allow the page-table backend to be replaceable. For the generic M3 baseline, a conventional multi-level/radix walk may be implemented as a `MODELING_DECISION` when needed. Do not claim that this is the exact target-paper page-table structure unless M4A establishes that fact.

The realistic resource path is the key M3 requirement:

`L2 TLB miss -> translation MSHR -> PWQ -> walker -> PTE memory request(s) -> L2/DRAM timing -> walker progress -> TLB fill -> waiter wakeup`.

## M3.1 — PTE address/backend contract

Define and document:

- page-table/backend interface;
- PTE address derivation per walk step;
- physical address space reserved for page-table storage;
- PTE request type/tagging;
- resolved page size and PPN extraction;
- deterministic initialization of present mappings.

PTE requests are already physical. They must bypass normal VA translation and must never recursively trigger PTW.

If a radix hierarchy is used for the generic baseline, keep the number of levels/configuration explicit and replaceable.

## M3.2 — Integrate PTE requests with memory hierarchy

Each required walk step that misses any page-walk cache must create an explicit page-table read that uses the real timing path authorized by the implementation.

Default desired behavior for the generic baseline:

- bypass normal L1D unless a documented model requires otherwise;
- enter L2 / lower memory hierarchy as a distinct request class;
- consume real queues/ports/MSHR/bandwidth as applicable;
- wait for the memory response before the dependent walker step progresses.

Keep PTE and data requests separately observable even when they share lower-level resources.

Required stats:

- PTE requests by walk level;
- PTE L2 hit/miss outcome;
- PTE DRAM reads/bytes;
- PTE queueing/memory latency;
- translation traffic fraction of lower-memory requests/bandwidth where measurable.

## M3.3 — Page-walk cache (PWC)

Implement a configurable PWC or equivalent intermediate page-table-entry cache with precisely documented keys and covered levels.

Required behavior/statistics:

- finite capacity and replacement;
- access/hit/miss by covered walk level;
- PWC hits skip the corresponding lower-memory request(s);
- zero-capacity mode;
- ideal/unbounded diagnostic mode may be added for upper-bound studies, clearly labeled diagnostic.

Do not use ordinary data-cache sector/subentry behavior as a substitute for a PWC without proving semantic equivalence.

## M3.4 — Multi-page foundation

Support at minimum the baseline page-size classes needed for subsequent work:

- 64KB base pages;
- 2MB large pages.

Required:

- correct VPN/page-offset calculation per size;
- page-size-aware TLB tags/fills;
- deterministic selection/mapping policy for tests;
- no accidental overlapping translation ambiguity;
- per-page-size stats.

A 4KB mode may be retained/added if useful for generic GPU VM studies, but it must not delay M3 closeout if not required by current experiments.

Do not implement the Segmentation paper's L2-TLB sub-entry/coalescing mechanism in M3; that belongs to the later paper-reproduction track after M4A audit.

## M3.5 — Timing and latency decomposition

For every completed translation, make the following components measurable where applicable:

- L1 TLB lookup;
- L2 TLB lookup;
- translation-MSHR wait/merge delay;
- page-walk queue delay;
- walker active/service time;
- PWC benefit;
- PTE memory response time;
- TLB fill/wakeup/replay delay;
- total translation latency.

Define timestamp ownership so time is not double-counted between overlapping components.

## Directed tests

Extend the M2 microtests with at least:

1. `vm_pte_no_recursion` — PTE reads never translate.
2. `vm_pte_l2_hit` — expected walk step resolved from L2 path.
3. `vm_pte_dram` — forced PTE L2 miss produces expected lower-memory request/response.
4. `vm_pwc_warm` — repeated related walks reduce PTE traffic through PWC hits.
5. `vm_pwc_zero` — PWC disabled produces expected full set of PTE accesses.
6. `vm_64kb_offset` — correct translation/page offset.
7. `vm_2mb_offset` — one large-page entry covers correct 2MB region.
8. `vm_mixed_pages` if mixed sizes are supported simultaneously — deterministic non-ambiguous lookup.
9. `vm_shared_resource_pressure` — PTE traffic demonstrably competes for an approved shared resource rather than being only a counter.
10. all M2 replay/conservation tests remain passing.

## Baseline characterization/sensitivity

Only after all correctness tests pass, run a small formal/closeout suite with representative regular, memory-intensive, and irregular traces already available.

Required sweeps:

- L2 TLB capacity: at least 3 points around default;
- translation MSHR entries: at least 3 points;
- walkers: e.g. 1 / 4 / 8 / 16 or closest practical sequence;
- PWC: off / baseline / ideal diagnostic;
- fixed-latency M2 PTW vs real-memory M3 PTW for causality;
- 64KB vs 2MB on at least one trace where both are valid under the mapping model.

Interpretation requirement: explain performance through measured hit/miss, queueing, PTE traffic, and blocked-warp effects. Do not use IPC alone as proof of correctness.

## Acceptance criteria

M3 PASS requires:

1. PTE requests are explicit, physical, and non-recursive;
2. realistic PTE activity consumes the intended L2/DRAM resources;
3. PWC behavior is deterministic in directed tests;
4. 64KB and 2MB translation semantics are correct;
5. latency decomposition is internally consistent and free of obvious double-counting;
6. all M1/M2 correctness invariants still pass;
7. no request loss/deadlock/duplicate side effects;
8. real-memory PTW behavior differs from fixed-latency PTW only in explainable ways;
9. sensitivity trends are supported by structured statistics;
10. VM-disabled transparency remains intact;
11. build, provenance, `git diff --check`, review-pack integrity pass.

## M1-M3 macro closeout

After M3 PASS, create:

`docs/vm_tlb/review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`

It must summarize:

- final Core and Framework SHAs;
- frozen VM architecture;
- all directed-test statuses;
- conservation/invariant evidence;
- baseline configuration(s);
- latency/resource model;
- limitations and `MODELING_DECISION`s;
- what remains required before target-paper reproduction;
- explicit statement that page fault/migration/MCM/segmentation/sub-entry are not yet implemented unless separately authorized.

After this closeout, Track A must STOP. Do not start the Segmentation mechanism.
