# M2 — Functional Translation Pipeline

## Objective

Implement and close out the functional single-GPU translation pipeline:

`SimVA -> per-SM L1 TLB -> shared L2 TLB -> translation MSHR -> page-walk queue -> fixed-latency walkers -> fill/wakeup -> translated data access`.

M2 proves resource/state-machine correctness before realistic PTE memory traffic is introduced.

## Baseline modeling scope

- resident pages only;
- ASID may be fixed to 0 for v0, but key structure must not prevent future ASIDs;
- base page bring-up: 64KB;
- initial mapper/page table content deterministic;
- single GPU only;
- fixed-latency PTW service in this stage;
- no page faults/migration/UVM;
- no segmentation/sub-entry;
- no realistic PTE L2/DRAM traffic until M3.

TLB capacities/associativities must be configurable. A bring-up config may use target-paper-scale capacities, but any latency/resource value not supported by the target paper must be labeled `MODELING_DECISION`, not `PAPER_EXACT`.

## M2.1 — Pre-mapped translation backend

Create a deterministic mapping/PTE backend over the trace-covered address space or approved lazy-present equivalent.

Required properties:

- page offset preserved;
- no two present VPNs accidentally alias to one PPN unless explicitly mapped that way;
- identity-like data mapping remains available for causality/transparency;
- application pages are always present;
- translation lookup can return the resolved page size and PPN.

## M2.2 — Per-SM L1 and shared L2 TLB

Implement configurable:

- per-SM L1 TLB;
- single-GPU shared L2 TLB;
- lookup latency and finite lookup throughput/ports or a clearly justified equivalent resource model;
- associativity/replacement;
- L2-hit L1-fill behavior;
- page-size-aware tags/entries.

Do not implement a TLB as only a fixed latency counter with unlimited concurrent lookups.

Required stats:

- L1 access/hit/miss/eviction;
- L2 access/hit/miss/eviction;
- occupancy;
- lookup/port stalls if modeled;
- per-page-size counters.

## M2.3 — Translation MSHR

Key semantics:

`(ASID, VPN, page-size-class)`

Required behavior:

- one active walk per translation key;
- later misses merge into that entry or backpressure if resources forbid it;
- finite MSHR entries;
- explicit full behavior;
- waiter registration exactly once;
- fill wakes each waiter exactly once;
- merge is not counted as a TLB hit.

Required stats:

- allocations;
- merges;
- full/backpressure events and cycles;
- occupancy histogram;
- merge-depth histogram/average/max;
- entry lifetime;
- waiters awakened.

## M2.4 — Page-walk queue and fixed-latency walkers

Implement:

- finite page-walk queue;
- configurable number of active walkers;
- fixed service latency for functional bring-up;
- completion event that fills the appropriate TLB level(s), releases MSHR state, and wakes waiters.

Hard invariant:
`active_walkers <= configured_walkers`.

Separate page-walk queue wait time from walker service time in statistics.

## M2.5 — Translation-caused stall and replay

Integrate the functional pipeline into the real load/store path.

Required behavior:

- data-cache access cannot issue before required translation completes;
- a stalled request resumes exactly once;
- no duplicate load request caused by replay;
- no duplicate store/atomic side effect;
- multiple outstanding translations from a warp/instruction are handled according to the actual transaction decomposition;
- simulator forward progress and backpressure remain correct when TLB/MSHR/PWQ/walkers saturate.

## Directed microtest matrix

Create small deterministic tests with machine-checkable expected counts. At minimum:

1. `vm_one_page` — repeated one-page accesses: one cold translation then hits.
2. `vm_l1_capacity` — predictable L1 eviction.
3. `vm_l2_capacity` — predictable L2 eviction and PTW.
4. `vm_two_sm_same_vpn` — separate L1 behavior with shared lower-level translation state.
5. `vm_multi_warp_merge` — multiple waiters, one active walk.
6. `vm_mshr_full` — finite MSHR backpressure, no loss.
7. `vm_walker_limit` — queue delay rises, active walkers never exceed limit.
8. `vm_cross_page_or_assert` — exercise the M1-approved transaction boundary behavior.
9. `vm_store_replay` — no duplicate store.
10. `vm_atomic_replay` if atomics traverse the implemented v0 global path — no duplicate atomic side effect.
11. `vm_kernel_persist` — ordinary kernel boundary retains translation state per frozen modeling decision.
12. `vm_disabled_regression` — existing baseline remains transparent when VM disabled.

Each test should specify expected TLB misses, MSHR allocations/merges, walk count, wakeups, and final request completion where applicable.

## Conservation/invariant checks

Provide machine-checkable checks for at least:

- one active walk per key;
- MSHR entries allocated == released at quiescence;
- waiter registrations == successful wakeups at quiescence;
- walk starts == walk completions at quiescence;
- no outstanding translation requests disappear at simulation end;
- no PTE-memory requests exist yet in M2;
- no translation-caused duplicate data-side requests/side effects.

Do not force a simplistic global equation between L2 misses and retries if the implementation reissues lookups; define event counters precisely in the spec and check the corresponding conservation law.

## Integrated validation

After directed tests pass, run at least:

- one regular/coalesced workload;
- one memory-intensive workload;
- one irregular workload if already available without new trace acquisition.

Perform small functional sensitivity sweeps over:

- L2 TLB capacity;
- translation MSHR entries;
- walkers;
- fixed PTW latency.

The purpose is sanity, not formal performance claims. Expected monotonicity must be interpreted carefully: larger resources should not create unexplained additional stalls, but IPC need not be strictly monotonic if unrelated resource timing changes interaction.

## Acceptance criteria

M2 PASS requires:

1. all required directed microtests PASS;
2. no deadlock/request loss/duplicate wakeup/duplicate store or atomic;
3. one active walk per translation key;
4. finite MSHR/PWQ/walker limits demonstrably affect backpressure/queueing;
5. TLB hit/miss/replacement behavior is deterministic on microtests;
6. fixed-latency PTW correctly stalls and resumes the real data path;
7. translation latency components are separately observable;
8. VM-disabled transparency still passes;
9. build, `git diff --check`, provenance and review-pack integrity pass.

Any functional correctness failure is a hard STOP before M3.

## Deliverables

Review pack:
`docs/vm_tlb/review_packs/M2_FUNCTIONAL_TRANSLATION/`

Include:

- microtest expected-vs-actual table;
- invariant/conservation report;
- representative TLB/MSHR/PTW structured statistics;
- integrated smoke/sensitivity summary;
- source/config/test provenance.

If PASS, Codex may proceed directly to M3.
