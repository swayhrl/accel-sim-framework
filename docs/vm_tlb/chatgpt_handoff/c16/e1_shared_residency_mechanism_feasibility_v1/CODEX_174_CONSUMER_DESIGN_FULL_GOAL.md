# CODEX 174-new — C16 E1 Shared-Residency Design Review / Consumer Prep Full Goal V1

## Mode

GOAL MODE / CPU-side design review + parallel consumer prep

Suggested branch:

`hrl/c16-e1-shared-residency-design-review-174new-v1`

No GPU work.
Do not modify node164 accepted authority.

## Read first

Fetch and verify:

`hrl/c16-e1-shared-residency-mechanism-feasibility-handoff-v1`

Read completely:

1. `docs/vm_tlb/chatgpt_handoff/c16/e1_shared_residency_mechanism_feasibility_v1/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/c16/e1_shared_residency_mechanism_feasibility_v1/DESIGN.md`
3. this file

Accepted upstream:
- persistence producer: `4c0e6b998528e425578cacf5912bbcc4ff3bfaf6`
- persistence consumer: `1dcab9c8d932973399c5811dc817802bfb3b9dfe`

## Stage 1 — freeze upstream divergence

Create:

`UPSTREAM_DECISION_DIVERGENCE_AUDIT.json`

Preserve exactly:
- producer scoped state
- strict consumer state
- raw evidence match
- methodological divergence
- current project action:
  `DESIGN_REVIEW_AUTHORIZED_WITH_TRAFFIC_CAVEAT`

Do not reinterpret the frozen prior rules.

## Stage 2 — shared-experiment consumer contract

Implement fail-closed consumer for:

- rotating-window qualification;
- native shared conditions;
- policy transition receipts;
- decode-step timing;
- target occurrence timing;
- shared-policy NCU;
- critical-path NCU metrics.

Frozen natural conditions:

- SETASIDE_ONLY
- ROTATE_CONTROL_3
- SINGLE_L0_UP
- SHARE2_UP
- SHARE2_L0
- SHARE3

Verify:
- one fixed total set-aside;
- exact full qweight windows;
- hitRatio contract;
- no reset between in-run switches;
- reset before/after full condition;
- exact token/SHA sequence;
- policy switch order;
- API-control condition.

Synthetic tests must cover:
- stale reset
- wrong window
- wrong hitRatio
- missing switch
- duplicated switch
- target identity drift
- API-control accidentally persisting
- nonfinite timing
- duplicate/missing reps.

## Stage 3 — critical-path consumer contract

Consumer must accept runtime-resolved exact NCU metric names and categories.

Freeze aggregation policy:
- additive metrics: sum only when category semantics allow;
- percentage/stall/occupancy metrics: per-kernel only unless explicit aggregation authority exists.

Fail closed on:
- unknown category
- unit mismatch
- duplicate metric row
- kernel inventory mismatch
- missing critical metric that producer claims available.

Build synthetic:
- GEMM+reduction
- additive sector sum
- non-additive stall percentage preserved separately
- metric unavailable path
- cross-condition unit mismatch.

## Stage 4 — independent shared-policy analysis

When producer exists, independently compute:

- local target timing benefit vs ROTATE_CONTROL_3
- stable D1-D3 decode-step effects
- policy update CPU overhead
- local target L1/L2/DRAM effects
- critical-path metric changes
- MULTI_TARGET_RETAINED
- MATERIAL_DECODE_BENEFIT

Do not use producer SHARED_POLICY_ANALYSIS as calculation authority.

## Stage 5 — inspect actual simulator L2 code

Use accepted repo state.

Map actual source implementation for:
- L2 cache object
- cache block metadata
- replacement policy
- victim selection
- insertion / fill path
- replacement-state update
- memory request metadata reaching L2
- whether request includes:
  - address
  - PC
  - memory space/access type
  - kernel UID
  - warp/CTA identifiers

Cite exact files/classes/functions in:

`ACCEL_SIM_L2_CODE_MAP.md`

Do not invent fields.

## Stage 6 — candidate mechanism comparison

Evaluate at least:

### M0_STATIC_PROTECTED_PARTITION

Fixed protected quota/ways.

Questions:
- how to map 8/16/24/32/full budget to ways/sets?
- how much normal capacity is stranded?
- can non-target lines borrow unused protected space?

### M1_ELASTIC_PROTECTED_QUOTA

Requirements:
- target-tag bit on line/request;
- protected occupancy budget;
- non-target may borrow unused capacity;
- on target arrival under pressure, non-target preferred victim;
- protected-vs-protected victim uses baseline recency.

Evaluate:
- metadata bits;
- state counters;
- victim-search changes;
- expected timing impact;
- implementation complexity.

### M2_PRIORITY_INSERT_EVICT

No hard partition:
- target line gets high insertion priority;
- target line protected/demoted according to reuse lifetime;
- ordinary replacement otherwise.

Evaluate same dimensions.

Do not rank based on novelty alone.

## Stage 7 — identity-source separation

Keep detection separate from replacement efficacy.

Review:

### Oracle/software-region tag
- exact qweight address-range identity
- preferred first simulator mechanism test

### Static PC/signature
- only if current trace/request format exposes stable PC and evidence supports it

### Dynamic reuse classifier
- defer unless simpler identity fails

The first simulator mechanism should normally use oracle/software-region tagging so policy efficacy can be measured independently of classifier accuracy.

## Stage 8 — choose first simulator mechanism spec

Create:

`FIRST_SIMULATOR_MECHANISM_SPEC.md`

Must define:
- mechanism name placeholder
- exact target tag semantics
- line metadata
- quota representation
- config knobs
- insertion rule
- hit/update rule
- victim rule
- overflow behavior
- normal-line borrowing behavior
- reset/lifetime behavior
- baseline compatibility
- stats/counters
- expected invariant checks.

Do not write implementation code.

## Stage 9 — simulator experiment plan

Create:

`SIMULATOR_EXPERIMENT_PLAN.md`

Plan:
- baseline
- static partition control
- chosen mechanism
- quota sweep mapped to measured budgets
- q/down/up operator controls
- natural reuse pattern if trace supports it
- no classifier confound in first experiment.

Also specify:
- exact workload/trace requirements;
- minimum trace duration;
- whether existing trace assets are enough.

## Stage 10 — trace requirement decision

Create:

`TRACE_REQUIREMENT_DECISION.json`

Possible:

- EXISTING_TRACE_SUFFICIENT
- BOUNDED_ADDITIONAL_TRACE_REQUIRED
- FULL_TRACE_REQUIRED_BUT_NOT_AUTHORIZED

If additional trace is needed:
specify minimum scope only.

Do not authorize or run capture.

## Stage 11 — prepare review pack

Create:

`docs/vm_tlb/review_packs/C16_E1_SHARED_RESIDENCY_DESIGN_REVIEW_174NEW_V1/`

with all DESIGN-required deliverables.

## Stage 12 — one-shot consume producer if ready

Expected producer:

`hrl/c16-e1-shared-residency-feasibility-109-v1`

After design/consumer prep:
fetch once.

If producer complete:
- consume raw hardware evidence;
- fill independent shared analysis;
- update design recommendation if evidence changes the requirement envelope;
- do not rewrite frozen experimental contracts;
- commit/push/verify/clean;
- STOP.

If producer absent/incomplete:
- commit/push prep;
- verify/clean;
- STOP:
  `READY_FOR_E1_SHARED_RESIDENCY_FEASIBILITY_109`

No polling.

## Boundary

No GPU.
No NVBit.
No trace capture.
No simulator code mutation.
No mechanism simulation.

Routine parser/code-map/document/Git issues:
solve-and-continue.

Small issues:
fix inside this Goal; do not create a separate repair turn.
