# DTC Granularity/Fairness Parallel Investigation Handoff

Status: `READY_TO_EXECUTE_WAVE_A`

## 0. Purpose

This handoff opens a new, bounded ISCAS-2027 investigation after the accepted FAST64/Lane-E package and the TC80 capacity-matched comparison exposed an important modeling asymmetry:

- frozen conventional Base/TC80 use the sector-cache path (`S`) with a 128-B line split into 4 x 32-B sectors;
- frozen DTC IO/OO issue whole-line lower requests at 128 B and complete a physical line only after all four 32-B sectors return.

The goal is to determine, with source-backed and controlled experiments, how much of the current workload-dependent DTC-vs-conventional behavior comes from:

1. request/fill granularity (32-B sector vs 128-B whole line),
2. ordinary searchable locality capacity,
3. DTC logical-Tag capacity and pending-Tag eviction,
4. downstream oversubscription after front-end constraints are relaxed,
5. genuine IO/OO lifetime/retirement advantages.

This handoff does **not** assume that DTC is wrong, and it does **not** assume that TC80 is the correct final baseline. It is designed to separate implementation/modeling effects from architectural effects.

## 1. Authority and immutable inputs

Repository: `swayhrl/accel-sim-framework`

New investigation branch:

`hrl/iscas2027-dtc-granularity-fairness-v0`

Branch parent:

`b6248660c290326aee49620b2245ff4cf0baf33c`

Frozen scientific authorities remain read-only:

- FAST64 final authority: `18a68dcccd795f1b6cda75504e9450d00c9cee02`
- Lane-E canonical package freeze: `b201b03f8100b5df0010fb64849a3e826b5a2183`
- TC80 CM3/CM4 evidence present at branch parent `b6248660c290326aee49620b2245ff4cf0baf33c`
- currently running TC80 CM5 campaign remains on `hrl/iscas2027-dtc-tc80-baseline-v0` and must not be interrupted, modified, reprioritized, or reused as scratch space.

The existing accepted FAST12 membership, trace hashes, B16/IO/OO cycles, and Lane-E scientific interpretations are immutable inputs.

## 2. Source-backed starting observation

The conventional cache parser maps cache-type token `S` to `SECTOR`; for a sector cache the request atom is `SECTOR_SIZE=32 B`. Conventional MSHR addresses are formed at the atom granularity. The standard tag array tracks sectors independently inside a 128-B line.

The accepted DTC source audit instead proves that each `NEW_MISS` creates one 128-B whole-line lower request and requires all four 32-B response sectors before physical completion.

This is a scientifically relevant implementation distinction, not a formatting detail. The new investigation must therefore compare like-for-like request granularity before final ISCAS claims are frozen.

## 3. Dissertation relation to audit

The dissertation Chapter 4 is an architectural reference, not a substitute for source proof. It defines Decoupled-Tag Cache around logical Tag space, physical cacheline space, hit-based miss merging, and large PIB structures, but the current investigation must explicitly determine whether the original RTL/dissertation implementation intended whole-line or sector-granular lower transactions. Do not silently infer the answer from the word `cacheline`.

A paper claim about the current simulator being faithful to the dissertation on transaction granularity is forbidden until SG0 resolves it.

## 4. High-level structure

The investigation is divided into two waves.

### Wave A — execute now in parallel

- `SG0`: source/dissertation/RTL-semantics audit (analysis only; no simulation required)
- `SG1`: conventional whole-line fairness controls (config-only if possible)
- `SG4A`: DTC logical-Tag-capacity expansion (config-only)
- `SG5`: observer-only comparable lower-traffic instrumentation and selected reruns

These lanes are intentionally independent enough to run concurrently.

### Wave B — start only after the relevant Wave-A gate closes

- `SG2`: sector-granular DTC prototype/implementation
- `SG3`: downstream-aware admission/throttling study
- `SG4B`: pending-Tag-retention policy study

Wave B may involve Core source changes and therefore must use separate branches/worktrees and directed correctness tests. No Wave-B result may overwrite accepted FAST64/Lane-E evidence.

## 5. Common scientific workload set

Use the frozen FAST12 identity exactly. For rapid diagnosis, the six-workload `G6` set is fixed **before** observing new results:

1. `ATAX`
2. `BICG`
3. `GESUMMV`
4. `Btree`
5. `2DConvolution`
6. `Gaussian`

Rationale:

- ATAX/BICG/GESUMMV: conventional-capacity-favoring / current DTC regression-sensitive cases;
- Btree/2DConvolution: DTC-favoring controls;
- Gaussian: high duplicate share but modest DTC gain and zero accepted L2 misses.

The G6 set is diagnostic. FAST12 remains the only primary aggregate when a lane is promoted to paper-facing evidence.

## 6. Hard global boundaries

### Never modify

- `docs/dtc_l1/post_fast64/review_packs/POST_FAST64_FINAL/**`
- `docs/dtc_l1/post_fast64/lane_e/qa_records/**`
- accepted FAST64 raw results or final tables
- TC80 CM3/CM4 accepted evidence
- the running TC80 CM5 raw directories/processes
- frozen FAST12 traces or membership

### Never do

- select a configuration because it looks faster after observing results;
- drop a negative workload;
- replace a failed scientific result with a nearby parameter;
- silently equate transaction count with bytes;
- compare traditional `L1_accesses/misses` against DTC custom-frontend counters as if they were identical semantics;
- claim DRAM traffic from lower-request payload counters;
- claim area/timing fairness before RTL/DC data is available.

## 7. Wave A lane SG0 — source/dissertation/RTL granularity audit

### SG0 goal

Resolve exactly which differences between conventional and DTC paths are architectural intent versus simulator implementation choices.

### Required questions

1. Conventional Base/TC80:
   - cache type (`SECTOR` vs `NORMAL`);
   - line size;
   - atom/MSHR address granularity;
   - lower request payload size;
   - per-sector RESERVED/VALID semantics;
   - refill completion semantics;
   - merge semantics.
2. DTC IO/OO:
   - logical lookup granularity;
   - physical allocation granularity;
   - lower request payload size;
   - response completion granularity;
   - pending-hit merge granularity;
   - physical-line lifetime granularity.
3. Dissertation Chapter 4:
   - whether request granularity is explicitly stated;
   - whether cacheline/physical-line references imply an implementation detail or only a logical structure.
4. RTL evidence, if available locally:
   - width/valid-bit organization of data arrays;
   - lower-request interface width/sector masks;
   - refill-valid granularity.
5. Quantify every source-level asymmetry that can influence performance independently of Tag/Data decoupling.

### SG0 outputs

- `docs/dtc_l1/iscas2027/granularity/SG0_SOURCE_SEMANTICS_AUDIT.md`
- `docs/dtc_l1/iscas2027/granularity/SG0_BASE_DTC_SEMANTIC_DIFF.tsv`
- `docs/dtc_l1/iscas2027/granularity/SG0_DISSERTATION_ALIGNMENT.md`

### SG0 PASS

PASS only when every row in the semantic diff is labeled one of:

- `ARCHITECTURAL_INTENT`
- `SIMULATOR_MODEL_CHOICE`
- `PLATFORM_BASELINE_CHOICE`
- `UNRESOLVED_REQUIRES_RTL_EVIDENCE`

No unlabeled behavior difference may remain.

## 8. Wave A lane SG1 — conventional whole-line fairness controls

### SG1 goal

Measure how much of the conventional advantage comes from 32-B sectorized miss handling rather than ordinary searchable capacity.

### New controlled variants

Create conventional NORMAL-cache controls while preserving all unrelated parameters:

- `B16-S`: frozen accepted Base, 16 KiB, sectorized (`S`), read-only input.
- `B16-N`: new conventional 16 KiB, NORMAL/whole-line (`N`), 32 sets x 4 ways x 128 B.
- `TC80-S`: accepted TC80 canonical 80 KiB sectorized (`S`), read-only input.
- `TC80-N`: new conventional 80 KiB, NORMAL/whole-line (`N`), canonical geometry 32 sets x 20 ways x 128 B unless SG0 proves this comparison invalid.
- `IO16/80`: frozen DTC IO.
- `OO16/80`: frozen DTC OO.

Only the cache type/request atom may change between `B16-S -> B16-N` and `TC80-S -> TC80-N`; capacity, sets, ways, line size, PIB, MSHR entry count, banks, policies, L1 modeled latency, shell, traces, L2/DRAM, scheduler and clocks remain fixed.

Changing `S` to `N` necessarily changes MSHR address granularity from 32 B to 128 B; this is part of the requested whole-line control and must be documented, not hidden.

### SG1 phase A — G6 qualification

Run G6 for `B16-N` and `TC80-N`.

Required comparison ratios per workload:

- `B16-N / B16-S`
- `TC80-N / TC80-S`
- `IO / B16-N`
- `OO / B16-N`
- `IO / TC80-N`
- `OO / TC80-N`

All ratios are recomputed from integer cycles.

### SG1 phase B — FAST12 promotion

If G6 results are valid and the NORMAL conventional path needs no scientific source repair, expand `B16-N` and `TC80-N` to all FAST12.

The lane may not stop after a favorable G6 subset if FAST12 promotion is technically possible.

### SG1 outputs

- immutable configs + resolved diffs;
- G6 manifest and summary;
- FAST12 manifest/summary if promoted;
- `SG1_SECTOR_VS_WHOLELINE_COMPARISON.tsv`;
- `SG1_INTERPRETATION.md`.

### SG1 interpretation gates

If switching conventional Base from S to N materially closes the DTC gap on ATAX/BICG/GESUMMV, record `SECTOR_GRANULARITY_MATERIAL`.

If it does not, record `SECTOR_GRANULARITY_SECONDARY`.

No threshold is hard-coded before seeing the data; the artifact must report exact numeric ratios and avoid binary wording when the effect is mixed.

## 9. Wave A lane SG4A — logical Tag-capacity expansion

### SG4A goal

Separate the cost of a small searchable logical Tag space from the value of a large physical pool.

### Fixed variants

Physical pool stays frozen at 80 KiB / 640 physical lines.

For both IO and OO, evaluate logical Tag capacities:

- 16 KiB (frozen reference, do not rerun unless needed for identity validation)
- 32 KiB
- 64 KiB
- 80 KiB

Keep PIB, physical pool, lower-request behavior, banks, line size, scheduler and all unrelated platform parameters fixed.

### SG4A execution policy

Existing accepted 32/64-KiB sensitivity rows for BICG/GESUMMV/Btree may be reused only when every relevant identity matches the new lane contract exactly. Do not rerun accepted rows just for convenience.

Run missing points for the full FAST12 whenever config-only execution is valid. This yields at most 72 new primary-sized rows (3 new logical capacities x 2 modes x 12 workloads), with accepted reusable rows subtracted.

### Required analysis

For each workload and mode compute:

- `speedup(logical32 vs logical16)`
- `speedup(logical64 vs logical16)`
- `speedup(logical80 vs logical16)`
- DTC logical80 vs `TC80-S`
- DTC logical80 vs `TC80-N` when SG1 provides it.

Also track Tag eviction, pending Tag eviction, duplicate-after-eviction, lower-created, physical full exposure and any already source-qualified counters.

### SG4A PASS

PASS requires exact one-dimensional logical-capacity changes only. A result where larger Tag capacity hurts performance remains valid.

## 10. Wave A lane SG5 — comparable lower-traffic observer

### SG5 goal

Create one observer-only, default-off telemetry extension that makes conventional and DTC lower-request work directly comparable at 32-B-sector and byte granularity.

### Required new counters

Per mode/SM where source semantics permit, record:

- lower request transaction creations;
- lower request payload bytes;
- 32-B sector-equivalent requests/payload;
- response payload bytes/sectors;
- outstanding lower-request integral over active SM cycles;
- lower queue/backpressure stall exposure;
- for DTC, whole-line request count and number of actually demanded sectors if reconstructible from the originating access mask without affecting behavior;
- for conventional sector cache, sector transaction count;
- for conventional normal cache, whole-line transaction count.

Counters must be observer-only, default-off, and never read by allocation, lookup, arbitration, victim selection, issue, completion, retirement or throttling.

### Directed SG5 tests

Create deterministic micro-fixtures proving:

- one 32-B sector miss increments exactly 32 B in sector mode;
- one 128-B normal miss increments exactly 128 B;
- one DTC whole-line NEW_MISS increments exactly 128 B;
- pending hits do not create new lower payload;
- duplicate-after-eviction creates an additional 128-B DTC lower payload;
- telemetry disabled vs enabled is cycle/instruction/output-equivalent on at least NN and Btree.

### SG5 runtime scope

After equivalence PASS, run G6 across available variants:

- B16-S
- B16-N (if SG1 ready)
- TC80-S
- TC80-N (if SG1 ready)
- IO
- OO

No SG5 observer row becomes a primary performance row.

### SG5 outputs

- source semantics document;
- directed-test report;
- telemetry off/on equivalence report;
- G6 comparable lower-payload table;
- per-workload lower-payload inflation and in-flight-pressure analysis.

## 11. Wave B lane SG2 — sector-granular DTC prototype

### Start condition

Start only after SG0 establishes that current DTC whole-line behavior is a simulator/implementation choice worth testing, and SG1/SG5 show that request granularity materially affects the problematic workloads or remains scientifically unresolved.

### SG2 architectural target

Do **not** merely split a 128-B request into four unconditional 32-B requests. That would preserve overfetch and change only transaction count.

Prototype true sector-aware DTC semantics:

- logical line remains 128 B unless source/RTL evidence dictates otherwise;
- each physical line has sector-valid/sector-pending state;
- an access allocates/requests only demanded sector(s);
- later accesses to other sectors of the same logical line can issue additional sector requests without losing the line identity;
- pending-hit merging occurs per required sector;
- completion/wakeup is dependency-correct per sector;
- IO/OO lifetime/reclaim remains correct when only a subset of sectors is ready;
- duplicate-after-eviction semantics are redefined and separately audited.

### SG2 correctness gates

Before workload simulation:

- directed sector miss/hit/pending tests;
- mixed-sector same-line tests;
- Tag eviction while sectors pending;
- stale generation response tests;
- IO release ordering tests;
- OO reference-count/reclaim tests;
- lower create/issue/response conservation;
- terminal drain.

Then run G6, and expand to FAST12 only after G6 correctness and identity PASS.

## 12. Wave B lane SG3 — downstream-aware admission/throttling

### SG3 motivation

Accepted D4 evidence shows that larger physical capacity can reduce pool-full exposure while increasing in-flight work, L2 pressure, miss lifetime and runtime for BICG/GESUMMV. This is consistent with bottleneck migration after front-end capacity is relieved, but does not yet prove an optimal throttle policy.

### SG3 phase A — static non-mechanism-changing sensitivity

Before designing new adaptive logic, sweep an existing source-reachable lower/outstanding cap or equivalent admission bound if one exists, with **predeclared global points** shared by all workloads.

Suggested points must be source-audited and chosen before performance observation. Do not invent a per-workload optimum.

Run G6 IO/OO at all legal points.

### SG3 phase B — adaptive candidate only if justified

If static sensitivity shows a robust interior region, design one global policy using source-visible downstream occupancy/backpressure. Candidate policy must be deterministic and workload-independent.

No adaptive policy may be promoted without RTL-cost discussion later.

## 13. Wave B lane SG4B — pending-Tag retention

### SG4B motivation

DTC uses Tags both for locality lookup and for pending-miss merging. Evicting a pending Tag can create a duplicate lower request before the original response returns.

### Candidate policy

Prefer a victim whose physical identity is already ready/non-pending when one exists. Only evict a pending Tag when all eligible ways are pending or another source-proven condition requires it.

This policy is not authorized for implementation until SG0 confirms exact current victim semantics and SG4A quantifies whether logical Tag pressure is material.

Required tests must include no-starvation and no-deadlock proofs/fixtures.

## 14. CPU/memory parallel-execution policy

The host has 512 logical CPUs and large memory. Use parallelism to reduce wall time, not to manufacture unnecessary parameter sweeps.

### Coexistence with live CM5

- do not signal, pause, renice, pin, attach to, or inspect CM5 in a way that perturbs it;
- new jobs should run at `nice +5` where practical;
- keep at least 64 logical CPUs uncommitted to this campaign;
- do not use all memory or trigger swap.

### Worker scaling

Controller should begin with a maximum of 192 simulation processes.

After at least 10 minutes of steady state, it may raise the ceiling to 256 if:

- no swap is active;
- memory available remains >35% of total;
- host load is stable;
- aggregate I/O wait is <10%;
- no launch or parser failures indicate filesystem pressure.

It may raise to 320 only after another stable observation interval satisfying the same conditions.

Hard maximum for this campaign: 384 concurrent simulator processes.

If I/O wait exceeds 20%, available memory falls below 20%, or swap becomes nonzero, reduce the worker ceiling. Preserve running scientific jobs; throttle only new launches.

### Launch priority

Launch long rows first within each independent lane:

1. GESUMMV
2. BICG
3. ATAX
4. remaining workloads

Stagger mass launch so hundreds of processes do not simultaneously decompress/read the same trace storage.

### Failure handling

Each attempt gets an immutable UUID namespace. Failed attempts are preserved. Retries use new namespaces. No output directory reuse.

## 15. Branch/worktree isolation

Wave-A lanes should use separate branches/worktrees to avoid source/config collisions:

- `hrl/iscas2027-dtc-sg0-audit-v0`
- `hrl/iscas2027-dtc-sg1-wholeline-controls-v0`
- `hrl/iscas2027-dtc-sg4a-logical-tag-v0`
- `hrl/iscas2027-dtc-sg5-lower-traffic-observer-v0`

Wave-B branches, created only when gates allow:

- `hrl/iscas2027-dtc-sg2-sector-dtc-v0`
- `hrl/iscas2027-dtc-sg3-throttle-v0`
- `hrl/iscas2027-dtc-sg4b-tag-retention-v0`

Each branch descends from this master investigation branch or an explicitly recorded reviewed descendant. Cross-lane cherry-picks require exact commit recording.

## 16. Stage status vocabulary

Every lane stage is exactly one of:

- `NOT_STARTED`
- `RUNNING`
- `PASS`
- `FAIL_REQUIRES_REPAIR`
- `BLOCKED_REQUIRES_RESEARCHER_DECISION`
- `NOT_APPLICABLE`

Do not call a stage PASS because a process is still alive or because error scans are empty.

## 17. Paper-facing decision tree

After Wave A:

### Case A — sector granularity explains most regressions

If whole-line conventional controls collapse much of TC80/B16 advantage and SG5 shows corresponding payload pressure, prioritize SG2 and rewrite the paper evaluation around a granularity-matched baseline.

### Case B — searchable capacity remains dominant

If TC80-N still strongly beats DTC on ATAX/BICG/GESUMMV, prioritize SG4A/SG4B and present DTC as a concurrency-oriented design with a locality-capacity trade-off.

### Case C — downstream oversubscription dominates

If DTC payload is not the main excess but in-flight/L2 pressure strongly tracks regressions and SG3 static caps recover performance, prioritize downstream-aware admission.

### Case D — mixed mechanisms

Retain workload-dependent classification and avoid a single-cause claim. The paper may still be strong if OO offers the best geometric-mean trade-off under a properly matched baseline plus RTL/DC cost evidence.

## 18. Required master outputs

Create under:

`docs/dtc_l1/iscas2027/granularity/`

- `MASTER_STAGE_STATUS.tsv`
- `MASTER_INPUT_MANIFEST.tsv`
- `MASTER_RESULT_INDEX.md`
- `MASTER_CLAIM_BOUNDARY.tsv`
- `MASTER_OUTPUT_MANIFEST.tsv`

No master READY status is permitted until all executed Wave-A lanes have independent validation and the result index points only to immutable accepted artifacts.

## 19. Wave-A completion state

When SG0, SG1, SG4A, and SG5 all close truthfully, emit:

`DTC_GRANULARITY_FAIRNESS_WAVE_A_READY_FOR_REVIEW`

This state does **not** imply SG2/SG3/SG4B are needed; Wave-B entry is decided from the Wave-A evidence.
