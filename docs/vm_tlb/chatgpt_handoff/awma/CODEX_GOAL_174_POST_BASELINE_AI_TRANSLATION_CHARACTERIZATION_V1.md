# CODEX 174 GOAL — Post-Baseline AI Translation Bottleneck Characterization V1

Date: 2026-09-23

Mode:

`GOAL MODE / LONG-RUN / SOLVE-AND-CONTINUE / NO-MECHANISM-IMPLEMENTATION`

Node:

`174-new`

Stage:

`AWMA_RTX4080_V1_AI_TRANSLATION_BOTTLENECK_CHARACTERIZATION_V1`

Read first, completely:

`docs/vm_tlb/chatgpt_handoff/awma/REVIEW_AWMA_RTX4080_V1_BASELINE_FINAL_ACCEPTANCE_2026-09-23.md`

This Goal begins the actual research phase.

Purpose:

> determine where translation time is still exposed under the frozen V1 baseline, whether that exposure is hit-path, miss-path, queueing, walk, working-set, burstiness, or generic concurrency behavior, and whether the remaining opportunity is large/structured enough to justify a new architecture mechanism.

Do NOT implement a new TLB/PTW/cache mechanism in this Goal.

Do NOT tune the frozen baseline.

A scientifically valid outcome may be:

`NO_STRONG_TRANSLATION_MECHANISM_OPPORTUNITY`

if the evidence says so.

---

# 1. Frozen baseline authority

Use:

`AWMA_RTX4080_SIM_BASELINE_V1`

authority:

`hrl/awma-174-rtx4080-v1-baseline-promotion-v1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`

Mandatory:

```text
platform config SHA256 =
de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8

GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1
GPGPUSIM_READY_APPLICATION_V2=0

primary VM = 10/80
diagnostic VM = 0/80
```

Do not change:

- platform parameters;
- VM capacity/latency parameters;
- V1 semantics;
- Segment state;
- trace identity.

Legacy is not the main research baseline anymore.

Use Legacy only if needed as a historical causal reference; do not rerun expensive Legacy points unless required for one bounded attribution.

---

# 2. Primary discovery targets

Start from the accepted real AI targets:

## T0

`Q05_PREFILL_ATTN_FLASH`

## T1

`PREFILL_GEMM_PRIMARY_OCC0`

## T2

`DECODE_GEMV_PRIMARY_STEP16`

These are discovery targets, not yet evidence for broad model-family generality.

Interpret prior AI baseline result:

```text
V1 sensitivity:
T0 = 6.01%
T1 = 0.15%
T2 = 10.36%
```

Therefore T2 is the highest-priority target for genuine post-baseline translation characterization.

T0 is a secondary control.

T1 is a low-sensitivity control.

Do not bias telemetry or conclusions to force T2 to look important.

---

# 3. Research questions

The Goal must answer the following separately.

## Q1 — how much modeled translation overhead remains?

For each T0/T1/T2, distinguish:

- baseline 10/80;
- 0/80 diagnostic;
- any already-existing admissible ideal/near-ideal translation control found in the codebase.

Do not invent a new idealization mode without review.

If an accepted existing ideal translation control exists, use it.

If not, report only 10/80 vs 0/80 and structural telemetry.

## Q2 — where is the time exposed?

Attribute critical translation-related stall time into the strongest defensible buckets available from source semantics:

- L1 lookup / hit-path wait;
- L2 lookup wait;
- PTW / page-walk service;
- MSHR / merged-request wait;
- PWQ wait;
- walker-capacity wait;
- accessq/head blocking;
- non-translation base concurrency residual.

Do not force every cycle into a bucket if source identity is ambiguous.

Use:

`UNATTRIBUTED_TRANSLATION_RELATED`

when needed.

## Q3 — is the workload limited by translation capacity or latency?

Characterize:

- L1 TLB hit/miss;
- L2 TLB hit/miss;
- walk starts/completions;
- unique pages;
- reuse;
- repeated request merges;
- lookup queue occupancy;
- MSHR occupancy;
- PWQ occupancy;
- walker occupancy.

Do not call a modeled TLB capacity a measured RTX4080 hardware capacity.

## Q4 — is the opportunity bursty / phase-local?

Determine whether misses/walks/translation stalls are:

- uniformly spread;
- concentrated in short bursts;
- concentrated at kernel start;
- concentrated at page-working-set transitions.

Use bounded time-window histograms rather than massive per-access logs.

## Q5 — is there predictable page behavior?

From existing accepted trace payloads, characterize:

- page transition sequence;
- run length on same modeled page;
- reuse distance / recency at a bounded level;
- stride regularity where meaningful;
- page-sharing across warps/CTAs where observable.

This is behavioral characterization, not hardware page-size inference.

## Q6 — is a paper-worthy mechanism opportunity present?

Classify only after all evidence is closed.

---

# 4. Telemetry design: aggregate first, not giant logs

All new telemetry must be:

- independent opt-in;
- default OFF;
- observational only;
- neutrality-qualified;
- aggregated/histogrammed where possible.

Do NOT emit one line per translation request for millions of accesses unless a bounded sample is explicitly needed.

Suggested umbrella switch:

`GPGPUSIM_AWMA_TRANSLATION_CHARACTERIZATION=1`

Prefer one centralized diagnostics object/module.

Keep existing diagnostics separate if already sufficient.

---

# 5. Required aggregate telemetry

At minimum collect per kernel/SM and global summary:

## Translation-source counts

- L1 hit;
- L1 miss;
- L2 hit;
- L2 miss;
- page-walk start;
- page-walk completion;
- merged request;
- retry/re-admission counts where source-supported.

## Latency/stall histograms

Use bounded logarithmic or fixed bins for:

- translation request→READY;
- READY→head/application if relevant under V1;
- MSHR wait;
- PWQ wait;
- walker wait;
- total translation-blocked memory-stage cycles.

Do not change simulation ordering to measure them.

## Occupancy high-water marks / histograms

- lookup entries;
- MSHR;
- PWQ;
- active walkers.

## Burstiness

Aggregate translation events over fixed windows, e.g. 128/256/512 cycles.

Choose one window size after a cheap pilot and freeze it.

Publish:

- mean events/window;
- p95/p99;
- max;
- fraction of events in top 10% busiest windows.

## Per-PC summary

For the top memory PCs only, bounded to e.g. top 16 by translation stall contribution:

- requests;
- hits/misses;
- walk starts;
- stall cycles.

Do not produce unbounded PC tables.

---

# 6. Telemetry neutrality

Before formal characterization:

for at least:

```text
T2 V1 10/80
T0 V1 10/80
```

compare diagnostics OFF vs ON.

Require exact equality in:

- gpu_sim_cycle;
- gpu_sim_insn;
- CTA;
- coverage;
- core VM counters;
- cache counters used later;
- final quiescence.

Only new diagnostics output may differ.

If diagnostics perturb simulation:

repair diagnostics and continue.

Do not change baseline semantics.

---

# 7. Offline trace characterization

Use accepted trace payloads directly where possible.

Do not rerun Native capture.

For T0/T1/T2 derive, at modeled page granularities:

Primary:

`64 KiB`

Supporting sensitivity only:

`4 KiB`

Do not infer RTX4080 hardware page size.

For each target compute:

- effective memory references;
- unique modeled pages;
- page-transition count;
- same-page run-length distribution;
- bounded reuse-distance distribution;
- top-page concentration;
- top-PC page footprint;
- warp/CTA page-sharing if recoverable.

Avoid memory-heavy exact reuse-distance algorithms if they are not necessary.

A streaming approximate/bounded method is acceptable if its approximation is documented.

---

# 8. Formal characterization matrix

The main matrix should remain small.

For each T0/T1/T2:

```text
V1 10/80 diagnostics ON
V1 0/80  diagnostics ON
```

Total formal points:

`6`

Do not rerun Legacy unless one specific attribution cannot otherwise be made.

If an already-existing accepted ideal translation mode is discovered and source identity is clean, optionally add:

```text
T0 ideal
T1 ideal
T2 ideal
```

as a bounded 3-point upper-bound control.

Do not create a new mode merely to fill the table.

---

# 9. T2 deep dive

Because T2 remains the highest-sensitivity AI target, perform one deeper characterization.

At minimum answer:

- what fraction of T2 requests hit L1/L2/walk;
- what fraction of modeled translation-stall cycles come from each path;
- whether misses/walks are bursty;
- whether MSHR/PWQ/walker occupancy saturates;
- whether repeated admissions are concentrated on specific PCs/pages;
- whether the 10.36% 10/80→0/80 sensitivity is mostly:
  - L1 hit-path latency;
  - miss-path latency;
  - queueing;
  - scheduling/concurrency interaction.

Do not assume the answer.

---

# 10. T0/T1 controls

Use T0/T1 to understand why their corrected V1 behavior differs.

Specifically:

## T0

Why does 6.01% residual remain?

## T1

Why is V1 sensitivity only 0.15%?

Compare:

- TLB hit rate;
- accessq cardinality;
- translation-level parallelism;
- miss/walk rate;
- memory pipeline overlap;
- page reuse.

The goal is to isolate what makes decode GEMV different from prefill attention/GEMM.

---

# 11. No parameter fitting

Absolutely no changes to:

- TLB entries;
- associativity;
- lookup latency;
- page size;
- walkers;
- MSHR;
- PWQ;
- platform caches;
- clocks.

Characterization is observational.

If a hypothetical capacity/latency sensitivity appears scientifically necessary, record it as a proposed next diagnostic rather than changing parameters inside this Goal.

---

# 12. Mechanism-opportunity classification

At the end, assign one or more evidence-based labels.

Allowed:

```text
HIT_PATH_EXPOSURE_DOMINANT
L2_MISS_PATH_DOMINANT
PTW_SERVICE_DOMINANT
TRANSLATION_QUEUEING_DOMINANT
WALKER_CONCURRENCY_DOMINANT
TLB_CAPACITY_PRESSURE_SUPPORTED
BURSTY_TRANSLATION_PRESSURE_SUPPORTED
PAGE_REUSE_OPPORTUNITY_SUPPORTED
PREDICTABLE_PAGE_TRANSITION_SUPPORTED
BASE_CONCURRENCY_RESIDUAL_DOMINANT
MIXED_TRANSLATION_BOTTLENECK
NO_STRONG_TRANSLATION_MECHANISM_OPPORTUNITY
```

Do not use a label unsupported by direct telemetry.

---

# 13. Paper-opportunity gate

A new mechanism should be considered only if at least one of the following is true:

## Gate A — material headroom

A translation-specific component accounts for at least ~5% of total cycles on at least one real AI target after V1 baseline correction.

## Gate B — strong recurring structural behavior

Even if total current-cycle headroom is modest, there is a strong recurring AI-specific pattern such as:

- concentrated translation bursts;
- repeated page reuse not captured by current hierarchy;
- systematic queue/walker bottleneck;
- highly predictable page transitions;
- decode-specific sustained translation pressure.

## Gate C — robustness / future scaling motivation

The current target is modestly affected but the measured pressure clearly scales with:

- larger page footprint;
- more warps/requests;
- decode length;
- model/operator shape.

Do not invent scaling evidence in this Goal.

If none of A/B/C is supported:

classify:

`NO_STRONG_TRANSLATION_MECHANISM_OPPORTUNITY`

and STOP for ChatGPT review.

---

# 14. Optional existing-target expansion

Only if T0/T1/T2 evidence is too narrow to distinguish the bottleneck:

search existing accepted/durable trace assets for at most:

- one additional attention-like kernel;
- one additional decode/GEMV-like kernel.

Use existing assets only.

No new node109 capture in this Goal.

Target selection must be predeclared by operator class / provenance, not based on observed sensitivity.

If no suitable accepted traces exist, skip.

Do not let target expansion dominate the Goal.

---

# 15. Publication

Suggested branch:

`hrl/awma-174-ai-translation-bottleneck-characterization-v1`

Report:

`docs/vm_tlb/codex_handoff/awma/AI_TRANSLATION_BOTTLENECK_CHARACTERIZATION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_AI_TRANSLATION_BOTTLENECK_CHARACTERIZATION_V1/`

Required:

```text
README.md
SOURCE_ANCHORS.md
BASELINE_AUTHORITY.json
CHARACTERIZATION_DIAGNOSTIC_CONTRACT.md
CHARACTERIZATION_DIAGNOSTIC.patch
TELEMETRY_NEUTRALITY.tsv
MATRIX_CONFIG_AUTHORITY.tsv
TRANSLATION_PATH_SUMMARY.tsv
TRANSLATION_STALL_BREAKDOWN.tsv
TRANSLATION_OCCUPANCY_SUMMARY.tsv
TRANSLATION_BURSTINESS.tsv
TOP_PC_TRANSLATION_SUMMARY.tsv
TRACE_PAGE_BEHAVIOR.tsv
T2_DEEP_DIVE.md
T0_T1_CONTROL_ANALYSIS.md
MECHANISM_OPPORTUNITY_DECISION.md
PAPER_OPPORTUNITY_GATE.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Do not create fake empty files if one telemetry category is scientifically not available.

If a required category cannot be source-supported, replace it with a short non-empty file explaining:

`NOT_AVAILABLE_WITHOUT_SEMANTIC_INVENTION`

---

# 16. Publication close

```text
characterization closure
→ opportunity classification
→ report/review pack
→ SHA256SUMS
→ commit/push
→ fetch-back
→ remote HEAD/tree verify
→ required files non-empty
→ sha256sum -c
→ clean worktree
→ STOP
```

Do not implement a mechanism after classification.

Mechanism design is a separate scientific decision for ChatGPT/user review.

---

# 17. Solve-and-continue policy

Ordinary engineering:

`solve-and-continue`

Also solve-and-continue for:

- obvious report fixes;
- diagnostic formatting;
- deterministic artifact reconstruction;
- small provenance cleanup;
- known benign source plumbing.

STOP only for:

- frozen baseline identity cannot be reproduced;
- trace payload identity changes;
- diagnostic requires semantic modification;
- characterization evidence invalidates the promoted baseline correctness;
- a new mechanism would need to be introduced to answer the question.

