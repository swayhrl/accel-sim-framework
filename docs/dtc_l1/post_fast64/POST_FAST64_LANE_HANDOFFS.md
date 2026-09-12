# POST-FAST64 Lane Handoffs and Acceptance Matrix

Status: **ACTIVE — subordinate to `POST_FAST64_MULTI_GOAL_CONTRACT.md`**

This file defines the durable handoff, sub-stages, outputs, and HARD validation requirements for each parallel lane.

---

# Lane A — Paper-grade result analysis

Terminal state: `A_PAPER_RESULTS_READY`

## A0. Accepted-input freeze

Inputs may come only from completed FAST64 review/accepted generated packages.

HARD:
- exact HEAD authority `18a68dcc...` is recorded;
- FAST12 membership is exactly 12;
- primary numbers match accepted Stage4/5 hashes;
- sensitivity inputs match accepted Stage6 registry;
- no post-FAST64 diagnostic result appears in paper-primary tables.

Output:
- `generated/post_fast64/A_ACCEPTED_INPUT_MANIFEST.tsv`

## A1. Primary performance

Build Base-normalized IO/OO table and figure-ready data.

HARD:
- Base=1.0 by workload;
- speedups are accepted Base/IO and Base/OO cycles only;
- exact GM-FAST12 IO/OO reproduced from accepted 12 members;
- negative IO rows retained;
- optional leave-one-out analysis is clearly supplemental and never replaces GM.

Outputs:
- `generated/post_fast64/paper_primary_performance.tsv`
- figure source + reproducible plotting script/data.

## A2. Base structural pressure

Required source-defined categories:
- PIB full;
- cacheline/all-lines-reserved;
- Tag-bank conflict separately;
- MSHR entry full;
- MSHR merge full;
- missqueue/downstream full.

HARD:
- raw counts preserved;
- normalized view uses a stated denominator (e.g. per 1M dynamic instructions or source-domain memory ops when valid);
- non-exclusive counters are not stacked into a fake 100% distribution;
- unsupported denominator/metric is explicit.

Outputs:
- `paper_base_pressure_raw.tsv`
- `paper_base_pressure_normalized.tsv`

## A3. IO -> OO mechanism evidence

Derive:
- `IO_HOL_SM_CYCLE_FRACTION = io_hol_ready_younger_cycles / (64 * io_cycles)`;
- `OO_OOO_RETIRE_FRACTION = oo_out_of_order_retires / oo_retire_count`;
- reclaim/wakeup counts and defensible normalized forms.

HARD:
- formula/provenance table accompanies every derived field;
- no claim that a counter is exclusive causal proof;
- ATAX/BICG/GESUMMV IO regression vs OO recovery is retained;
- workloads where IO ~= OO are retained.

Outputs:
- `paper_io_oo_mechanism.tsv`
- plot-ready figure data.

## A4. Sensitivity presentation

Logical:
- IO normalized to IO@16 KiB;
- OO normalized to OO@16 KiB.

Physical:
- retain accepted authority table;
- add reader-facing IO-to-IO@32 and OO-to-OO@32 normalization;
- 16.5-KiB resource deadlocks remain nonnumeric boundary markers.

PIB:
- IO normalized to IO@128;
- OO normalized to OO@128.

HARD:
- no rerun/tuning to beautify curves;
- requested vs modeled capacity preserved;
- same-mode normalization formulas explicit.

Outputs:
- `paper_sens_logical.tsv`
- `paper_sens_physical.tsv`
- `paper_sens_pib.tsv`

## A5. Per-workload explanation

For all 12 workloads produce:
- performance behavior;
- Base pressure signature;
- IO HOL evidence;
- OO retire/reclaim evidence;
- traffic contrast;
- strongest supported interpretation;
- caveat/alternative explanation.

HARD:
- every statement traces to accepted tables;
- `SOURCE_PROVEN` and `MEASURED_CORRELATION` are distinguished;
- Gaussian should not be mechanically described as “no benefit” when accepted performance is ~1.108x; paper wording may use “modest benefit”.

Outputs:
- `POST_FAST64_PAPER_RESULT_ANALYSIS.md`
- `paper_workload_explanations.tsv`

Lane A PASS when A0-A5 all pass and all plotting inputs are reproducible without raw-log scraping.

---

# Lane B — Physical Pool causal analysis

Terminal state: `B_PHYSICAL_CAUSAL_READY`

## B0. Source audit

Audit:
- physical line selection/free-list;
- physical identity usage;
- Tag victim selection;
- tag eviction;
- IO release-on-retire;
- OO immediate/deferred/final-ref reclaim;
- lower request generation;
- downstream address/L2 mapping.

HARD:
- explicitly determine whether `physical_identity.id` can affect lower address, L2 set/partition mapping, request ordering, or only internal storage identity;
- direct physical-index mapping hypothesis H5 is ruled out only by exact source path evidence.

Output:
- `PHYSICAL_POOL_SOURCE_AUDIT.md`

## B1. Existing-data full matrix

Before any new run, consume all accepted Stage6 numeric physical points for BICG/GESUMMV/Btree and IO/OO.

Extract at minimum:
- cycles/instructions;
- lower requests;
- L2 accesses/misses/reservation fails;
- global reads/writes;
- valid/pending hits;
- Tag evictions;
- IO duplicate-after-eviction;
- IO no-free/partial/allocation-width/physical peak/min-free;
- OO OOO-retire/immediate/deferred/final-ref reclaim/wakeups.

HARD:
- exact source compact path and SHA per row;
- no 16.5-KiB failed row treated as numeric performance;
- no missing supported field silently filled with zero.

Output:
- `generated/post_fast64/physical_pool_mechanism_raw.tsv`

## B2. Normalization and contrast

Produce defensible normalized tables:
- per 1M instructions;
- per 1M lower requests where denominator is semantically meaningful;
- per simulated cycle/SM-cycle where appropriate;
- same-mode performance normalization.

HARD:
- each normalized column has formula/unit/provenance;
- raw counts remain available;
- accumulated counts are never interpreted without exposure/time denominator when such interpretation matters.

Output:
- `physical_pool_mechanism_normalized.tsv`

## B3. Hypothesis adjudication using existing data

Classify each:

H1 — smaller pool is simply capacity-starved.
H2 — larger pool removes front-end throttling and shifts pressure to L2/reservation resources.
H3 — longer pending lifetime increases pending-Tag eviction and duplicate lower traffic.
H4 — OO reclaim/lifetime changes exposed concurrency.
H5 — physical ID/free-list changes downstream mapping.

Allowed verdicts only:
- `SOURCE_PROVEN`
- `MEASURED_CORRELATION`
- `DATA_DOES_NOT_SUPPORT`
- `INSUFFICIENT_NEEDS_TELEMETRY`

HARD:
- do not select a story because it is aesthetically preferred;
- non-monotonic/negative evidence must be retained;
- H5 cannot survive if source audit proves physical ID is downstream-inert.

Output:
- `PHYSICAL_POOL_CAUSAL_HANDOFF.md`

## B4. Telemetry gap definition

Only if B3 contains `INSUFFICIENT_NEEDS_TELEMETRY`, specify the minimum observer-only counters needed.

Candidate metrics:
- alloc->ready count/sum/max;
- pending Tag eviction count;
- pending-eviction->response latency count/sum/max;
- OO tag-eviction->final-reclaim latency count/sum/max;
- event-driven physical occupancy integral if implementation is low-risk.

HARD:
- every requested counter maps to one unresolved arrow/hypothesis;
- no “collect everything” instrumentation;
- no mechanism state may branch on observer state.

## B5. Diagnostic wave

Minimal high-information first wave:
- workloads: BICG, GESUMMV, Btree;
- physical points: 24, 32, 48 KiB;
- modes: IO/OO;
- skip an exact point if required telemetry already exists.

Then optionally 40 KiB only if needed.

HARD per row:
- observer-qualified diagnostic Core;
- immutable/fresh run identity;
- natural terminal or source-classified expected boundary;
- strict pre-existing accounting/drain;
- classification `POST_FAST64_EXPLORATORY_NOT_PRIMARY_RESULT`.

## B6. Integrated physical-pool explanation

For each arrow:

`pool -> admitted/inflight pressure -> L2 pressure -> pending lifetime -> pending Tag eviction -> duplicate traffic -> performance`

assign:
- `SOURCE_PROVEN`
- `MEASURED_CORRELATION`
- `NOT_SUPPORTED`
- `INSUFFICIENT`

Lane B PASS when non-monotonic physical sensitivity is explained to the strongest evidence-supported level and unsupported causal arrows remain explicitly bounded.

---

# Lane C — No-MSHR duplicate-request quantification

Terminal state: `C_DUPLICATE_MISS_READY`

## C0. Semantic proof

Prove exact IO counter semantics in source:
`DTC_L1_io_duplicate_after_eviction` increments only when a pending line loses its Tag and the same line is reallocated before the original response completes; post-response re-access is not duplicate.

HARD:
- identify source locations for eviction tracking, response cleanup, and increment;
- prove one increment corresponds to one newly created miss/lower transaction before calling it duplicate traffic;
- audit request granularity before converting count to bytes.

Output:
- `DUPLICATE_MISS_SOURCE_SEMANTICS.md`

## C1. FAST12 IO extraction — no rerun

From accepted FAST12 IO rows extract:
- lower_created;
- pending_hits;
- tag_evictions;
- duplicate_after_eviction;
- physical allocations;
- traffic counters.

Derived metrics:
- `duplicate_share_of_lower = duplicate / lower_created`;
- `duplicate_escape_fraction = duplicate / (duplicate + pending_hits)`;
- `duplicate_per_tag_eviction = duplicate / tag_evictions`.

HARD:
- raw counts retained;
- zero denominator handled explicitly;
- ratios are descriptive, not probabilities unless semantics prove that interpretation;
- no performance gain is inferred from “removing” duplicates.

Output:
- `generated/post_fast64/duplicate_miss_fast12_io.tsv`

## C2. Thesis 4.2.2 claim adjudication

Answer:
- are duplicates rare for most FAST12 workloads?
- what is the distribution, not just average?
- are there exceptions?
- do exceptions coincide descriptively with high Tag eviction, long pending behavior, or physical-pool anomalies?

HARD:
- no threshold chosen after seeing data may redefine “rare” as a formal theorem;
- if display bands are used (<0.1%, 0.1-1%, 1-5%, >5%), label them presentation bins only;
- exceptions must be retained.

Output:
- `DUPLICATE_MISS_HANDOFF.md`

## C3. Physical-sweep duplicate correlation

Using existing Stage6 IO physical points, relate duplicate rate to:
- pool size;
- pending hits;
- Tag evictions;
- L2 reservation fails/misses;
- cycles.

HARD:
- correlation is not causality;
- normalize by lower requests and/or instructions.

## C4. OO semantic gap

Audit whether accepted OO already has an equivalent duplicate counter. If not, define the exact observer-only OO semantics required. Do not approximate OO duplicates from `new_misses - ...` unless source equivalence is proved.

If the thesis claim is already adequately adjudicated from IO, OO telemetry remains useful extension rather than a blocker for C PASS. If the scientific question explicitly requires IO/OO comparison, invoke Lane D.

## C5. Optional OO FAST12 exploratory wave

Only after Lane D observer qualification. Prefer reuse of Lane D physical telemetry first; then run FAST12 OO only if needed to answer the no-MSHR question robustly.

HARD:
- 2D uses Core658-rooted observer descendant;
- non-2D uses Core95-rooted observer descendant;
- same accepted workload/config semantics;
- diagnostic-only classification.

Lane C PASS when the dissertation statement has a quantified, source-backed answer and any exceptions are characterized without hiding them.

---

# Lane D — Observer-only telemetry and diagnostic execution

Terminal state: `D_OBSERVER_EVIDENCE_READY_IF_NEEDED`

Lane D is conditional: only instrument unresolved B/C questions.

## D0. Instrumentation specification

At minimum, if needed:
- `DTC_L1_oo_duplicate_after_eviction` with semantics matched to IO;
- selected event-driven lifetime counters from B4.

HARD:
- counter definitions written before implementation;
- each counter has increment/reset/cleanup semantics;
- no observer data is read by mechanism decisions.

Output:
- `OBSERVER_TELEMETRY_SPEC.md`

## D1. Isolated implementation

Use separate Core branches rooted exactly at accepted Core95 and Core658 as needed.

HARD source review:
- diff contains observation state/printing only;
- no changes to Tag lookup/victim choice/allocation/free selection/retirement/reclaim/lower scheduling/completion;
- no production assertion weakened;
- observer state cannot affect a return value used by mechanism behavior.

Output:
- exact Core diff and source-audit record.

## D2. Build/unit regression

HARD:
- clean isolated Release build;
- existing focused DTC tests pass;
- new counter unit/directed test validates positive and negative cases;
- hash diagnostic runtime.

## D3. Observer equivalence qualification

Cheap workloads: NN and Btree unless source requires another minimal path.

Compare telemetry-off/reference vs telemetry-on diagnostic binary/config as appropriate.

HARD exact equality:
- cycles;
- instructions;
- all pre-existing scientific counters available in compact output;
- lower/dependency accounting;
- terminal drain;
- payload/config scientific identity except observer-only instrumentation identity.

Any difference requires investigation before D4.

## D4. Physical diagnostic wave

Run minimal B lane wave after D3 PASS.

HARD:
- same accepted workload and one-dimensional physical config semantics;
- fresh immutable attempt;
- diagnostic classification;
- no use in FAST64 GM/sensitivity accepted tables.

## D5. Duplicate-request diagnostic wave

If Lane C needs OO across FAST12, dispatch dynamically after D3 PASS and reuse D4 data when possible.

HARD:
- avoid duplicate runs;
- strict source lineage (Core95 vs Core658 2D);
- complete counter conservation/drain.

## D6. Telemetry closeout

Produce:
- diagnostic identity manifest;
- observer equivalence report;
- counter semantic/provenance table;
- retained exploratory results index;
- explicit list of any failed/obsolete attempts.

Lane D PASS only when observer-only equivalence is demonstrated and every retained diagnostic row is source/provenance-valid.

---

# Lane E — Integrated synthesis

Terminal state: `POST_FAST64_PAPER_ANALYSIS_AND_MECHANISM_EXPLORATION_READY_FOR_REVIEW`

## E0. Merge accepted lane packages

HARD:
- Lane A PASS;
- Lane B PASS;
- Lane C PASS;
- Lane D PASS if invoked, otherwise explicit `NOT_REQUIRED_FOR_CONCLUSION` disposition;
- all references resolvable and hash-bound where appropriate.

## E1. Integrated mechanism chain

For every link in:

`physical pool -> exposed concurrency -> downstream/L2 pressure -> pending lifetime -> Tag eviction while pending -> duplicate lower traffic -> performance`

record evidence level and counterexample(s).

HARD:
- do not force one root cause if evidence shows multiple contributors;
- explicitly evaluate whether duplicate traffic is negligible, secondary-but-measurable, or major per workload;
- state whether the larger-pool slowdown is primarily downstream pressure with duplicate traffic as feedback, if and only if supported.

## E2. Final review package

Required outputs:
- paper-grade primary figures/tables;
- physical-pool root-cause report;
- duplicate-miss thesis-claim report;
- observer telemetry report if used;
- integrated limitations/open-questions section;
- machine-readable manifests for derived/new evidence.

No accepted FAST64 result is changed by E PASS.
