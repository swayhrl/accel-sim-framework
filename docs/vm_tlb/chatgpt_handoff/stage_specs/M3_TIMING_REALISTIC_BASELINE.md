# M3 — Timing-Realistic Single-GPU VM Baseline

## Objective

Replace M2's fixed-latency functional page-walk service with a timing/resource model in which page-table activity consumes realistic simulator resources, then close out a reusable single-GPU VM/TLB/PTW baseline for later LLM work.

M3 remains a resident-memory address-translation study. It does not add page faults, migration, UVM oversubscription, segmentation, sub-entry, or MCM behavior.

M3 is executed continuously after M2 **only if M2 fully passes its closeout gate**. See `M2_M3_TARGET_MODE.md` for the target-mode gate sequence.

## Required entry materials

Before any M3 semantic source modification, Codex must read:

1. `M2_M3_TARGET_MODE.md`;
2. `M3_REFERENCE_MATERIALS.md`;
3. the completed M2 review pack and exact M2 Core/Framework SHAs;
4. long-lived VM specs under `docs/vm_tlb/specs/`;
5. `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md` for target-paper known/unknown boundaries;
6. root `AGENTS.md`.

At M3 entry, record a parameter ledger that labels each relevant choice as `PAPER_SPEC`, `MODELING_DECISION`, `REFERENCE_OTHER_PAPER`, `DIAGNOSTIC`, or `UNKNOWN`.

Do not block generic M3 closeout merely because target-paper PTW/sub-entry details are unavailable. Build a replaceable generic baseline and preserve the evidence boundary for M4B.

## M3 entry gate

M3 may start only after all of the following are true:

- `M2_FUNCTIONAL_TRANSLATION` status is PASS;
- all required M2 directed tests/invariants pass;
- no deadlock/request loss/duplicate wakeup/duplicate store/atomic exists;
- VM-disabled transparency still passes;
- exact M2 Core/Framework SHAs are recorded;
- M2 review pack is complete;
- compact M2 regression rerun at M3 entry remains clean.

Any failure here is a STOP before M3.

## Architectural boundary

The VM core must allow the page-table backend to be replaceable. For the generic M3 baseline, a conventional configurable multi-level/radix walk is authorized as a `MODELING_DECISION` when target-paper details remain unavailable. Do not claim that this is the exact Segmentation-paper page-table structure.

The realistic resource path is the key M3 requirement:

`L2 TLB miss -> translation MSHR -> PWQ -> walker -> PTE memory request(s) -> real L2/DRAM timing -> walker progress -> TLB fill -> waiter wakeup -> replay/data access`.

The fixed-latency M2 PTW path must remain available as a diagnostic comparison until M3 closeout, unless removal is explicitly justified after equivalent validation coverage is preserved.

## M3.1 — PTE address/backend contract

Define and document:

- replaceable page-table/backend interface;
- page-table level count/configuration;
- PTE address derivation per walk step;
- physical address space reserved for page-table storage;
- PTE request type/tagging;
- resolved page size and PPN extraction;
- deterministic initialization of present mappings;
- response identity needed to resume the correct walker/request.

PTE requests are already physical. They must bypass normal VA translation and must never recursively trigger PTW.

The page-table physical range must not accidentally overlap application-data mapping in the generic model. Add an assertion/validation check where practical.

### M3.1 gate

PASS requires at minimum:

- deterministic PTE-address unit test;
- page-table physical-range validation;
- `vm_pte_no_recursion` directed test;
- no change to M2 replay/conservation behavior.

Only then proceed to M3.2.

## M3.2 — Integrate PTE requests with real memory hierarchy

Each walk step not satisfied by PWC must create an explicit page-table read that uses the real timing path.

Default generic behavior:

- bypass normal L1D unless an explicitly documented model requires otherwise;
- enter L2 / lower memory hierarchy as a distinct request class;
- consume real queues, ports, cache-MSHR resources, interconnect/bandwidth, and DRAM timing as applicable;
- wait for the actual response before the dependent walker step progresses;
- preserve enough request identity to associate each response with the correct walk step and translation key.

Keep PTE and data requests separately observable even when they share lower-level resources.

Required stats:

- PTE requests by walk level;
- PTE L2 hit/miss outcome;
- PTE DRAM reads/bytes;
- PTE queueing/memory latency;
- PTE outstanding occupancy;
- translation traffic fraction of lower-memory requests/bandwidth where measurable;
- walker wait-on-memory time.

### M3.2 gate

PASS requires:

- `vm_pte_l2_hit`: expected PTE read returns through real L2 timing;
- `vm_pte_dram`: forced PTE L2 miss reaches lower memory and returns correctly;
- walker cannot advance before PTE response;
- PTE request never recursively translates;
- no lost/misassociated response;
- `vm_shared_resource_pressure` or equivalent proves PTE traffic consumes an actual shared resource rather than a statistics-only path;
- all relevant M2 replay/store/atomic invariants still pass.

Recursive translation, deadlock, response misassociation, request loss, or unexplained early progress is an immediate STOP.

## M3.3 — Page-walk cache (PWC)

Implement a configurable PWC or equivalent intermediate page-table-entry cache with precisely documented keys and covered levels.

Required behavior/statistics:

- finite capacity and replacement;
- access/hit/miss by covered walk level;
- PWC hits skip the corresponding lower-memory request(s);
- zero-capacity mode;
- ideal/unbounded diagnostic mode may be added for upper-bound studies, clearly labeled `DIAGNOSTIC`;
- PWC state/lifetime policy documented.

Do not use ordinary data-cache sector/subentry behavior as a substitute for PWC without proving semantic equivalence.

### M3.3 gate

PASS requires:

- `vm_pwc_warm` reduces expected PTE traffic;
- `vm_pwc_zero` emits the full expected set of PTE requests;
- PWC hit/miss/replacement counts are deterministic in microtests;
- PWC does not alter data request semantics;
- all M2 conservation checks still pass.

Only then proceed to M3.4.

## M3.4 — Multi-page foundation

Support at minimum:

- 64KB base pages;
- 2MB large pages.

Required:

- correct VPN/page-offset calculation per size;
- page-size-aware TLB tags/fills;
- deterministic page-size selection/mapping policy for directed tests;
- no accidental overlapping translation ambiguity;
- per-page-size stats;
- page-walk/backend termination appropriate to the resolved page-size class.

A 4KB mode may be retained/added if useful for generic GPU VM studies, but it must not delay M3 closeout if not required by current experiments.

Do not implement the Segmentation paper's L2-TLB sub-entry/coalescing mechanism in M3. That belongs to M4B after paper-specific evidence/approximation decisions.

### M3.4 gate

PASS requires:

- `vm_64kb_offset`;
- `vm_2mb_offset`;
- deterministic non-ambiguous mixed-size lookup if mixed sizes coexist;
- page-size-specific counters/entries validated;
- existing M2 behavior unchanged for its original 64KB tests.

## M3.5 — Timing and latency decomposition

For every completed translation, make these components measurable where applicable:

- L1 TLB lookup;
- L2 TLB lookup;
- translation-MSHR wait/merge delay;
- page-walk queue delay;
- walker active/service time;
- PWC access/benefit;
- PTE queueing + memory response time;
- walker wait-on-memory time;
- TLB fill/wakeup/replay delay;
- total translation latency.

Define timestamp ownership so time is not double-counted. Where components overlap, document whether totals are additive or critical-path intervals rather than forcing an invalid sum.

Required validation:

- synthetic/directed timing case with analytically known intervals;
- checks that timestamps are monotonic and non-negative;
- explain any difference between summed components and total translation latency.

## Directed tests

Extend M2 tests with at least:

1. `vm_pte_no_recursion` — PTE reads never translate.
2. `vm_pte_l2_hit` — expected walk step resolved from real L2 path.
3. `vm_pte_dram` — forced PTE L2 miss produces expected lower-memory request/response.
4. `vm_pwc_warm` — repeated related walks reduce PTE traffic through PWC hits.
5. `vm_pwc_zero` — PWC disabled produces expected full PTE accesses.
6. `vm_64kb_offset` — correct translation/page offset.
7. `vm_2mb_offset` — one large-page entry covers the correct 2MB region.
8. `vm_mixed_pages` if mixed sizes are supported simultaneously — deterministic non-ambiguous lookup.
9. `vm_shared_resource_pressure` — PTE traffic demonstrably competes for an approved shared resource.
10. `vm_pte_response_identity` — multiple outstanding walkers receive the correct PTE responses.
11. `vm_walk_latency_accounting` — known timing intervals validate decomposition.
12. all M2 replay/conservation tests remain passing.

Tests must assert expected counts/invariants, not merely exit 0.

## Baseline characterization / sensitivity

Only after all correctness gates pass, run a small closeout suite with representative regular, memory-intensive, and irregular traces already available.

Required sweeps:

- L2 TLB capacity: at least 3 points around default;
- translation MSHR entries: at least 3 points;
- walkers: e.g. 1 / 4 / 8 / 16 or closest practical sequence;
- PWC: off / baseline / ideal diagnostic;
- fixed-latency M2 PTW vs real-memory M3 PTW for causality;
- 64KB vs 2MB on at least one trace where both are valid under the mapping model.

Interpretation rules:

- do not require strictly monotonic IPC in all cases;
- do require that larger/removing resources do not create unexplained new stalls;
- explain performance using measured TLB behavior, MSHR/PWQ pressure, PWC, PTE traffic, lower-memory contention, blocked-warp effects, and latency decomposition;
- IPC alone is never correctness evidence.

## M3 configuration / evidence boundary

M3 should keep configuration tiers distinguishable:

- `GENERIC_M3_BASELINE`: project-defined reusable timing model;
- `SEGMENTATION_PAPER_KNOWN`: only target-paper parameters explicitly known (e.g. 64KB, 32-entry L1, 768-entry/16-way L2, 16 walkers), with unknown timing/PTW details still labeled;
- `DIAGNOSTIC_IDEAL`: upper-bound resources/translation.

See `M3_REFERENCE_MATERIALS.md` for allowed reference use of CLAP and legacy `dev-uvm`.

M3 closeout may claim correctness/causality of the implemented generic model. It must not yet claim exact Segmentation-paper baseline reproduction.

## Acceptance criteria

M3 PASS requires all of the following:

1. M2 entry gate was PASS and its regression invariants remain PASS;
2. PTE requests are explicit, physical, and non-recursive;
3. realistic PTE activity consumes intended L2/DRAM/shared resources;
4. response identity is correct under multiple outstanding walks;
5. PWC behavior is deterministic in directed tests;
6. 64KB and 2MB semantics are correct;
7. latency decomposition is internally consistent and documented without obvious double-counting;
8. no request loss/deadlock/duplicate wakeup/duplicate side effect;
9. real-memory PTW differs from fixed-latency PTW only in explainable ways;
10. sensitivity trends are supported by structured statistics;
11. VM-disabled transparency remains intact;
12. parameter/evidence labels correctly separate project model from target-paper facts;
13. build, provenance, `git diff --check`, worktree cleanliness, and review-pack integrity pass.

Any correctness failure is a hard STOP before macro closeout.

## Review-pack requirements

Create:

`docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/`

In addition to standard review-pack files, include:

- `PARAMETER_EVIDENCE_LEDGER.md` or equivalent;
- directed-test expected-vs-actual table;
- PTE request/response conservation report;
- PTE L2/DRAM traffic summary;
- PWC behavior summary;
- 64KB/2MB validation summary;
- translation latency-decomposition sample/consistency check;
- fixed-vs-real PTW causality summary;
- sensitivity summary with structured CSV/TSV artifacts.

## M1-M3 macro closeout

After M3 PASS, create:

`docs/vm_tlb/review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`

It must summarize:

- final Core and Framework SHAs;
- frozen VM architecture and request path;
- all M1/M2/M3 directed-test statuses;
- conservation/invariant evidence;
- baseline/default configuration(s);
- latency/resource model;
- parameter evidence ledger;
- limitations and `MODELING_DECISION`s;
- what remains required before target-paper reproduction;
- explicit statement that page fault/migration/MCM/segmentation/sub-entry are not implemented unless separately authorized.

Update:

- `docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`;
- `docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`.

Push both source repositories, report final SHAs, then STOP.

**STOP BEFORE M4B / Segmentation / synthetic-KV simulator injection / new AI-aware TLB mechanisms.**
