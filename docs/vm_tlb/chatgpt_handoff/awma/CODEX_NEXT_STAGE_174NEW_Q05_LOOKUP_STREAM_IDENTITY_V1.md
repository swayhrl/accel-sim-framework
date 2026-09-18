# CODEX NEXT STAGE — 174-new Q05 Lookup-Stream Identity Closure V1

Date: 2026-09-19

Status: ACTIVE MAINLINE.

Stage:

`AWMA_Q05_LOOKUP_STREAM_IDENTITY_CLOSURE_174NEW_V1`

Node:

`174-new / port 2239`

## 0. Scientific reason

The accepted lookup-model-validity stage established:

`LOOKUP_TIMING_COUPLED_NEEDS_MODEL_CALIBRATION`

and proved:

- 10/80 are generic model assumptions, not RTX4080-calibrated values;
- read-only launch-vs-completion residency telemetry is neutral;
- `LAUNCH_MISS -> COMPLETE_HIT = 0` for all bounded P8/P34 points;
- lookup latency perturbation still changes lookup/admission/retry stream.

P34 example:

```text
point      cycles    lookup launches/completions
10/80      871835    776915
5/80       778598    779016
0/80       748102    865036
0/0        657110    872241
```

GPU instruction/CTA totals stay fixed.

Therefore the next question is:

> Why does the number/identity of VM-boundary coalesced access objects change when only translation timing changes?

This must be closed before using lookup-latency sensitivity as architecture evidence.

No architecture mechanism is introduced.

## 1. Coordination and parent

Read:

`hrl/awma-q05-lookup-stream-identity-handoff-v1`

Execution parent:

```text
hrl/awma-q05-lookup-model-validity-174new-v1
9bbfad6ce1add1a6292f8177de7d92e71a3572d4
```

Recommended branch:

`hrl/awma-q05-lookup-stream-identity-174new-v1`

Node109 remains on the independent V2.1 side campaign. Do not use or interrupt it.

## 2. D0 — Freeze prior facts

Carry forward:

- same-trace P34 realism reference;
- target-only lookup matrix;
- 10/80 generic-model-assumption status;
- fill-race telemetry result;
- P8 screening-only policy;
- P34 final realism reference.

Do not repeat the previous latency sweep beyond the minimum points listed below.

## 3. D1 — Source audit: one mem_access_t must not retranslate after READY

Document and test the accepted source contract:

```text
ldst_unit::memory_cycle()
  if !access.vm_translation_applied():
      translate(...)
      on READY:
          access.set_sim_pa(...)

mem_access_t::set_sim_pa()
  m_vm_translation_applied = true
```

After this flag is set, downstream L1D/L2/ICNT backpressure must not re-enter translation for that same `mem_access_t`.

Add a disabled-by-default target-Q05 invariant counter:

- unique mem_access UID first seen at VM boundary;
- lookup launch count by mem_access UID;
- translation READY count by mem_access UID;
- count of any UID launching translation more than once after prior READY.

Expected invariant:

`NO_RETRANSLATION_AFTER_READY`

If violated, STOP_FOR_SCIENTIFIC_REVIEW.

## 4. D2 — Source audit: access generation/coalescing identity

Document where `mem_access_t` objects are created.

Accepted source:

`warp_inst_t::generate_mem_accesses()`

Global/local/param-local all go through `memory_coalescing_arch()`.

Important local-memory source contract:

`shader_core_ctx::translate_local_memaddr()`

maps thread-local addresses into the shared timing-address space using runtime quantities including:

- SM id;
- hardware CTA slot / thread placement;
- padded threads per CTA;
- number of shader cores.

Then coalescing operates on those translated timing addresses.

Therefore different CTA/SM placement can, in principle, change local-memory segment addresses and coalesced transaction count even when trace lane addresses/instruction count are fixed.

This is a hypothesis to test, not a conclusion.

Create:

`ACCESS_GENERATION_SOURCE_CONTRACT.md`

## 5. D3 — Read-only target-Q05 access-stream telemetry

Add disabled-by-default target-only telemetry.

It must not alter:

- instruction scheduling;
- CTA scheduling;
- local address mapping;
- coalescing;
- access queue order;
- cache policy;
- translation state/timing;
- replacement metadata.

For every target-Q05 memory instruction/access object, aggregate without unbounded raw logs.

### Required aggregate counters by address space

For:

```text
GLOBAL
LOCAL
PARAM_LOCAL
```

record:

- dynamic memory-instruction count entering access generation;
- active lane count;
- generated `mem_access_t` count;
- unique mem_access UID count;
- total bytes;
- 32B/64B/128B transaction-size histogram;
- load/store/atomic split;
- translation lookup launches;
- translation READY completions.

### Required per-PC summary

For each memory PC:

- space;
- dynamic instruction count;
- active lanes;
- generated access count;
- access-count-per-instruction distribution or min/max/mean;
- transaction size histogram.

Output bounded top-changing-PC analysis between runs.

### Required per-SM / CTA-placement summary

For target Q05:

- CTA count assigned per SM;
- ordered CTA identifiers/slots if source-stable;
- per-SM global/local generated access counts;
- per-SM local unique translated timing-address page counts if source-safe.

Do not infer model-layer identity from CTA id.

### Required access-UID integrity

Count:

- total unique access UIDs;
- UIDs with exactly one lookup launch;
- UIDs with >1 lookup launch before READY;
- UIDs with any post-READY retranslation attempt.

No unbounded per-UID artifact in Git; bounded diagnostic raw can live on node164 if needed.

## 6. D4 — Neutrality gate

With telemetry enabled and lookup latency natural:

```text
P34_10_80_STREAM_CONTROL
P8_10_80_STREAM_CONTROL
```

Require exact reproduction of prior accepted scientific metrics.

If telemetry changes behavior, repair before proceeding.

## 7. D5 — Minimum comparison matrix

Use only:

### P34

```text
10/80
5/80
0/80
0/0
```

### P8

```text
10/80
0/80
```

No new latency values.

Each row is fresh process; predecessor context remains natural R0.

## 8. D6 — Stream-difference attribution

For every comparison, determine:

1. Does total generated `mem_access_t` count change by the same amount as lookup launches?
2. Is the change entirely GLOBAL, entirely LOCAL, PARAM_LOCAL, or mixed?
3. Which PCs account for >=90% of the access-count delta?
4. Are those PCs local-memory instructions?
5. Does CTA-to-SM placement differ across timing points?
6. If local access counts change, is the change consistent with different local-address coalescing caused by SM/CTA mapping?
7. If global access counts change, what source-level path permits a fixed trace/instruction stream to generate a different coalesced-access count?
8. Does every access UID translate exactly once after creation?

Do not claim causality until counter conservation closes.

## 9. D7 — Optional controlled placement diagnostic

Only if D6 strongly shows the stream delta is caused by LOCAL accesses and CTA/SM placement differences.

Audit whether the simulator already supports a source-safe deterministic CTA-placement/replay control that can hold Q05 CTA placement fixed **without changing**:

- trace semantics;
- resource limits;
- scheduling policy beyond tie/order determinism;
- cache/TLB architecture.

If such a control already exists and its semantics are clean, run a bounded P34 comparison:

```text
fixed-placement 10/80
fixed-placement 0/80
```

Purpose:

> test whether access-count variation collapses when placement is held fixed.

If no clean existing control exists, record:

`FIXED_PLACEMENT_DIAGNOSTIC_NOT_SOURCE_SAFE`

and do not implement a new scheduler mechanism in this stage.

## 10. D8 — Decision

Allowed classifications:

```text
LOOKUP_STREAM_DELTA_EXPLAINED_BY_LOCAL_MAPPING_COALESCING
LOOKUP_STREAM_DELTA_EXPLAINED_BY_OTHER_ACCESS_GENERATION
LOOKUP_STREAM_DELTA_MIXED
LOOKUP_STREAM_DELTA_UNRESOLVED
```

Also state separately:

- whether lookup-latency sensitivity remains qualitatively meaningful;
- whether quantitative lookup-latency claims still require native calibration;
- whether P8 remains an acceptable screening prefix.

## 11. Claim boundaries

Allowed:

- source-backed access-stream identity differences;
- per-space/per-PC/per-SM structural effects;
- timing-induced scheduling/coalescing interaction inside the simulator.

Not allowed:

- claiming real RTX4080 local-memory coalescing behaves this way;
- treating simulator CTA-placement effects as hardware truth;
- using this stage to calibrate 10/80;
- architecture mechanism claims.

## 12. Durable output

Large diagnostic logs:

`/root/share/mnt164/huangrulin/awma_q05_lookup_stream_identity_v1/`

174 local disk remains bounded scratch/source only.

## 13. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_LOOKUP_STREAM_IDENTITY_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_LOOKUP_STREAM_IDENTITY_174NEW_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
ACCESS_GENERATION_SOURCE_CONTRACT.md
VM_ACCESS_UID_INVARIANT.md
NEUTRALITY_RESULTS.tsv
P34_ACCESS_STREAM_MATRIX.tsv
P8_ACCESS_STREAM_MATRIX.tsv
SPACE_SPLIT_ACCESS_COUNTS.tsv
TOP_PC_ACCESS_DELTA.tsv
CTA_SM_PLACEMENT_MATRIX.tsv
ACCESS_UID_INTEGRITY.tsv
STREAM_DELTA_CONSERVATION.tsv
OPTIONAL_FIXED_PLACEMENT.md
STREAM_IDENTITY_DECISION.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Success marker:

`AWMA_Q05_LOOKUP_STREAM_IDENTITY_CLOSURE_174NEW_V1_COMPLETE_WITH_SCOPE`

Then report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
