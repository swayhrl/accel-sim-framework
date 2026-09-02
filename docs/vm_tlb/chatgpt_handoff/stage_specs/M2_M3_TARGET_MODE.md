# M2-M3 Target-Mode Execution Plan

## Purpose

Run M2 and M3 as one continuous Codex target-mode task with explicit internal quality gates. Codex may advance automatically only after the current gate passes. A failed gate is a STOP, not permission to weaken tests or silently change semantics.

## Target-mode progress record

Maintain a Codex-owned progress file during execution:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

Update it after every gate with:

- goal/gate ID;
- status: `NOT_STARTED | RUNNING | PASS | FAIL | BLOCKED`;
- Core SHA / Framework SHA;
- exact tests run;
- review-pack evidence path;
- unresolved issues;
- next goal.

This file is a recovery/checkpoint aid for long target-mode runs. It does not replace stage review packs or `LATEST_REPORT.md`.

## Execution graph

```text
M1 PASS
  |
  v
G2-0  M2 entry/provenance check
  |
  v
G2-1  pre-mapped backend + L1/L2 TLB
  |
  v
G2-2  translation MSHR + same-key merge/backpressure
  |
  v
G2-3  PWQ + fixed-latency walkers
  |
  v
G2-4  real stall/replay integration + directed microtests
  |
  v
G2-CLOSEOUT  M2 full acceptance gate
  |
  | PASS only
  v
G3-0  M3 entry snapshot / M2 regression freeze
  |
  v
G3-1  PTE backend + physical request contract
  |
  v
G3-2  PTE requests integrated into L2/DRAM timing
  |
  v
G3-3  PWC + non-recursion/shared-resource tests
  |
  v
G3-4  64KB/2MB foundation + timing decomposition
  |
  v
G3-5  integrated sensitivity/causality validation
  |
  v
G3-CLOSEOUT  M3 acceptance + M1-M3 macro closeout
  |
  v
STOP before M4B / Segmentation / synthetic KV
```

## G2-0 — M2 entry gate

Required before any M2 semantic source change:

- Core branch clean at or descendant of M1 Core `82fa2bc79cf09dd137073431dc41e48bc2f30cec`;
- Framework branch clean at current Track-A handoff head;
- writable `research` Core remote verified;
- M1 transparency evidence still present and attributable;
- read M2 spec, M3 spec, `M3_REFERENCE_MATERIALS.md`, root `AGENTS.md`.

PASS -> G2-1.

## G2-1 — mapper + L1/L2 TLB gate

Required:

- deterministic present-page backend;
- finite per-SM L1 TLB and shared single-GPU L2 TLB;
- page-size-aware tags;
- replacement deterministic on microtests;
- finite lookup throughput/ports or explicitly justified equivalent;
- `SimPA` cannot be consumed before translation completion.

Minimum directed evidence:

- one-page cold/hit sequence;
- L1 capacity eviction;
- L2 capacity eviction;
- two-SM shared-L2 behavior;
- VM-disabled transparency regression.

PASS -> G2-2.

## G2-2 — translation MSHR gate

Required:

- key `(ASID, VPN, page-size-class)`;
- one active translation per key;
- same-key misses merge;
- finite entries/full backpressure;
- waiter registered once;
- merge is not counted as TLB hit;
- allocation/release and waiter conservation checks.

Minimum directed evidence:

- multi-warp same-VPN merge;
- MSHR-full pressure;
- deterministic allocation/merge/wakeup counts.

PASS -> G2-3.

## G2-3 — fixed-latency walker gate

Required:

- finite PWQ;
- finite walker count;
- fixed service latency only for M2;
- queue wait separated from service time;
- `active_walkers <= configured_walkers` hard invariant;
- completion fills translation state and wakes waiters exactly once.

Minimum directed evidence:

- walker saturation test;
- PWQ backpressure test if independently bounded;
- walk start == completion at quiescence.

PASS -> G2-4.

## G2-4 — stall/replay correctness gate

Required:

- untranslated data request never enters real cache path;
- completed translation resumes exactly once;
- already-translated request does not retranslate on replay;
- no duplicate store/atomic side effect;
- cross-page behavior follows M1 proof/split policy;
- ordinary kernel boundary preserves TLB state per frozen modeling decision.

All required M2 microtests must have machine-checkable expected-vs-actual counts.

PASS -> G2-CLOSEOUT.

## G2-CLOSEOUT — mandatory M2 stage gate

Before entering M3, all M2 acceptance criteria in `M2_FUNCTIONAL_TRANSLATION.md` must pass.

Required artifacts:

- `review_packs/M2_FUNCTIONAL_TRANSLATION/README.md`;
- expected-vs-actual directed-test table;
- conservation/invariant report;
- structured TLB/MSHR/PWQ/walker stats;
- integrated regular/memory-intensive/irregular smoke;
- VM-disabled transparency regression;
- clean build, `git diff --check`, clean worktrees, provenance.

If any correctness item fails: set target progress to FAIL/BLOCKED, update `LATEST_REPORT.md`, push evidence, STOP. Do not enter M3.

If PASS: record the exact M2 Core/Framework SHAs and continue automatically to G3-0.

## G3-0 — M3 entry / freeze gate

Before changing PTW timing semantics:

- snapshot M2 PASS SHAs and baseline stats;
- rerun a compact subset of M2 invariants to ensure the M3 starting point is clean;
- read `M3_TIMING_REALISTIC_BASELINE.md` and `M3_REFERENCE_MATERIALS.md`;
- explicitly record which M3 parameters are `MODELING_DECISION`, `PAPER_SPEC`, or `UNKNOWN`.

PASS -> G3-1.

## G3-1 — PTE backend / request-contract gate

Required:

- replaceable page-table backend;
- deterministic PTE physical address derivation;
- reserved/non-overlapping simulated physical region for page tables;
- explicit PTE request class/tag;
- PTE request bypasses normal translation;
- directed no-recursion test passes.

PASS -> G3-2.

## G3-2 — real memory integration gate

Required:

- walker-generated PTE reads enter the approved real L2/lower-memory timing path;
- PTE requests consume actual shared queue/MSHR/bandwidth/resource behavior rather than only incrementing counters;
- walker advances only after the PTE response;
- PTE and data requests remain separately observable;
- deterministic L2-hit and forced-DRAM PTE tests pass.

Hard STOP on recursive translation, request loss, deadlock, response misassociation, or unexplained early walker progress.

PASS -> G3-3.

## G3-3 — PWC/shared-resource gate

Required:

- finite configurable PWC with explicit key/covered levels;
- zero-capacity mode;
- warm-related-walk test demonstrably reduces PTE traffic;
- shared-resource-pressure test proves data/PTE competition on an intended resource;
- all M2 replay/conservation tests still pass.

PASS -> G3-4.

## G3-4 — page-size/timing gate

Required:

- correct 64KB translation semantics;
- correct 2MB translation semantics;
- mixed-size behavior deterministic if supported simultaneously;
- no overlapping translation ambiguity;
- per-page-size stats;
- timestamp ownership documented;
- latency decomposition checked for double counting.

PASS -> G3-5.

## G3-5 — integrated causality/sensitivity gate

Only after G3-1..G3-4 pass:

- regular, memory-intensive, irregular available traces;
- L2 TLB capacity sweep;
- translation-MSHR sweep;
- walker sweep;
- PWC off/baseline/ideal diagnostic;
- M2 fixed-latency vs M3 real-memory PTW causality comparison;
- 64KB vs 2MB on at least one valid trace.

No strict IPC monotonicity requirement. Every claimed trend must be explained with translation hit/miss, queueing, PTE traffic, blocked-warp and latency statistics.

PASS -> G3-CLOSEOUT.

## G3-CLOSEOUT — M3 + macro closeout

M3 must satisfy every acceptance item in `M3_TIMING_REALISTIC_BASELINE.md` and create:

- `review_packs/M3_TIMING_REALISTIC_BASELINE/`;
- `review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`.

Macro closeout must state exactly:

- final Core/Framework SHAs;
- implemented VM architecture and timing path;
- all directed-test/invariant statuses;
- baseline/default configuration;
- `MODELING_DECISION`s and paper-specific unknowns;
- what M4B must still implement or replace (notably target-paper sub-entry and any paper-specific PTW details);
- explicit exclusions: page fault/migration/UVM/MCM/Segmentation/sub-entry unless separately authorized.

Then push, update `LATEST_REPORT.md`, mark target progress complete, and STOP.
