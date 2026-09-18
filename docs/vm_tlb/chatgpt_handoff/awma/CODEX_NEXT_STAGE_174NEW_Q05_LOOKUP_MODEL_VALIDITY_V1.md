# CODEX NEXT STAGE — 174-new Q05 Lookup-Model Validity Closure V1

Date: 2026-09-18

Status: ACTIVE MAINLINE.

Stage:

`AWMA_Q05_LOOKUP_MODEL_VALIDITY_CLOSURE_174NEW_V1`

Node:

`174-new / port 2239`

## 0. Scientific reason

The accepted contextual lookup decomposition established strong model sensitivity to target L1 lookup latency:

```text
P34:
10/80 = 871835 cycles
 5/80 = 778598
 2/80 = 771796
 0/80 = 748102
 0/0  = 657110
 I0   = 674121
```

However, changing lookup latency also changes the observed lookup stream and miss ordering:

```text
P34 L1 launches:
10/80 = 776915
 5/80 = 779016
 2/80 = 786997
 0/80 = 865036

P34 L2 misses:
10/80 = 249
 5/80 = 306
 2/80 = 307
 0/80 = 308

L2-only:
10/80 misses = 249
10/40 misses = 277
10/0  misses = 304
```

Therefore these points are not a pure additive subtraction of a fixed hit latency.

Accepted source explains why: the actual TLB `probe()` occurs when the modeled service interval ends. Shortening the latency moves the probe earlier in time, so the request can observe a different evolving TLB/fill state. In particular, a slower lookup can observe a translation that was filled while it waited; a faster lookup may reach L2/MSHR before that fill exists.

The stage must distinguish:

```text
service-delay sensitivity
from
probe-time / fill-race sensitivity
from
retry / memory-transaction stream changes
```

before any architecture mechanism is designed.

## 1. Coordination and parent

Read coordination branch:

`hrl/awma-q05-lookup-model-validity-handoff-v1`

Execution parent:

```text
hrl/awma-q05-contextual-lookup-decomposition-174new-v1
07d8c3cdd414b0a881264df341685e864fed2761
```

Recommended execution branch:

`hrl/awma-q05-lookup-model-validity-174new-v1`

No node109 GPU task is authorized by this stage.

## 2. D0 — Accept and freeze prior lookup result with scope

Carry forward:

```text
P34 realism reference:
10/80 871835
5/80  778598
2/80  771796
0/80  748102
10/40 904750
10/0  878836
0/0   657110
I0    674121
```

P8 remains screening-only.

Allowed interpretation:

- target L1 lookup timing strongly affects modeled Q05 total cycles;
- L2-only latency perturbation is non-monotonic;
- zero/zero is not equivalent to I0;
- lookup latency perturbations alter the timing/order of translation events and lower-memory execution.

Do **not** interpret 10->5 as an implementable hardware speedup yet.

## 3. D1 — Lookup-latency provenance audit

Audit source history and project evidence for the baseline values:

```text
-gpgpu_vm_l1_tlb_lookup_latency = 10
-gpgpu_vm_l2_tlb_lookup_latency = 80
```

Source-history anchor:

`swayhrl/gpgpu-sim @ 5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

The introducing source labels them:

```text
"generic M3 L1 TLB lookup service cycles"
"generic M3 L2 TLB lookup service cycles"
```

Search all project docs/review packs/commit history for a direct calibration receipt or external hardware source for 10/80.

Classify each parameter as one of:

```text
HARDWARE_CALIBRATED
LITERATURE_TRANSFERRED_WITH_SCOPE
GENERIC_MODEL_ASSUMPTION
UNKNOWN
```

Fail closed: do not invent an RTX4080/Ada latency calibration.

Create:

- `LOOKUP_LATENCY_PROVENANCE_AUDIT.md`
- `LOOKUP_LATENCY_EVIDENCE_MATRIX.tsv`

## 4. D2 — Existing-log invocation accounting

Before new simulation, mine the already durable lookup-matrix logs.

For each P34 point and the P8 screening points, extract where source-supported:

- `vm_requests`;
- `vm_translation_lookup_requests`;
- `vm_translation_lookup_inflight_bypasses`;
- `vm_translation_pending_waiter_bypasses`;
- `vm_translation_requester_completions`;
- `vm_ideal_translations` / functional completed;
- L1/L2 launches/completions/hits/misses;
- MSHR alloc/merge;
- global/local/param-local memory transaction counters;
- local/global load/store counters;
- CTA/SM assignment or local-memory mapping counters if already emitted;
- L2/data-cache/DRAM counters used in the previous stages.

Verify the source-backed accounting identity for each natural-translation row if it holds:

```text
vm_requests
=
inflight-bypass invocations
+ pending-waiter-bypass invocations
+ new lookup admissions/attempts
+ ready/completion retry invocations
(+ any explicitly source-defined remaining category)
```

Do not force the identity if source counters define different units.

Create:

- `LOOKUP_INVOCATION_ACCOUNTING.tsv`
- `LOOKUP_STREAM_VARIATION_AUDIT.md`

Explicitly distinguish:

`function call / retry invocation`

from:

`unique memory transaction requiring one completed translation`.

## 5. D3 — Source semantic explanation of probe-time coupling

Document the accepted controller semantics precisely.

Current model:

```text
lookup launch
-> ready_cycle = launch + configured latency
-> only when ready_cycle is reached:
     probe current TLB state
-> hit/miss decision
```

Therefore the configured lookup latency controls both:

1. when the requester can complete;
2. when the TLB contents are sampled.

This means a translation filled during the service interval can convert a launch-time miss opportunity into a completion-time hit.

Create:

`PROBE_TIME_COUPLING_CONTRACT.md`

This is a model semantic statement, not a hardware claim.

## 6. D4 — Read-only fill-race telemetry

Add a disabled-by-default target-only diagnostic that does **not** change functional timing.

Need a non-mutating lookup-state observation helper for L1/L2.

At lookup launch, record whether the exact key is resident **without**:

- changing LRU/replacement metadata;
- consuming a port;
- modifying hit/miss counters;
- changing ready cycles;
- filling or invalidating any entry.

At normal completion, compare the actual existing probe result.

For L1 and L2 count:

```text
LAUNCH_HIT -> COMPLETE_HIT
LAUNCH_HIT -> COMPLETE_MISS
LAUNCH_MISS -> COMPLETE_HIT
LAUNCH_MISS -> COMPLETE_MISS
```

The most important class is:

`LAUNCH_MISS -> COMPLETE_HIT`

because it directly measures "became resident while service latency elapsed".

Also record, target-Q05 only:

- per-space global/local/param-local lookup admissions;
- post-PTW delivery/retry L1 probes if source-safe;
- unique waiter UID count;
- lookup launch count by space.

No event-level raw dump unless bounded and necessary; aggregate counters are preferred.

## 7. D5 — Neutrality gate

With fill-race telemetry enabled at natural 10/80, rerun:

```text
P34_R0_TELEMETRY
P8_R0_TELEMETRY
```

Require all previously accepted scientific metrics to reproduce exactly.

If a supposedly non-mutating observation changes replacement or timing, repair before continuing.

## 8. D6 — Bounded coupling matrix

After neutrality, run only the minimum points needed to explain the previous matrix:

### P34

```text
10/80
5/80
0/80
10/40
10/0
0/0
```

### P8

Only:

```text
10/80
5/80
0/80
```

For each point report:

- normal Q05 cycles;
- launch-vs-completion transition counts;
- lookup admission/completion counts;
- inflight/pending retries;
- unique completed translations;
- L1/L2 hit/miss;
- MSHR/walks;
- per-space translation counts;
- L2 data/DRAM counters.

Do not add new latency values.

## 9. D7 — Model-validity decision

Answer:

1. Why do L1 lookup launches rise when latency falls?
2. How much of the L1/L2 hit/miss change is explained by fill-during-service races?
3. Are global and local memory requests affected equally?
4. Does the 10->5 cycle speedup remain large even when the lookup-stream change is small, or is much of it coupled to changed request ordering?
5. Is L2 non-monotonicity substantially explained by `LAUNCH_MISS -> COMPLETE_HIT` opportunities at longer service latency?
6. Can the current 10/80 model support a qualitative claim of "lookup-path sensitivity"?
7. Can it support a quantitative RTX4080 claim? Only answer YES if calibration evidence exists.
8. What additional native calibration is required before mechanism evaluation?

Allowed final classifications:

```text
LOOKUP_SENSITIVITY_QUALITATIVELY_ROBUST
LOOKUP_TIMING_COUPLED_NEEDS_MODEL_CALIBRATION
LOOKUP_RESULT_NOT_INTERPRETABLE_WITHOUT_MODEL_REWORK
```

These are not architecture-mechanism verdicts.

## 10. D8 — RTX4080 native calibration plan, no GPU execution

Prepare a future calibration plan only; do not use node109 in this stage.

The plan should investigate whether a native dependent-load microbenchmark can separate:

- warm L1-TLB condition;
- L1 miss / lower-TLB hit condition;
- lower-TLB miss condition;

while controlling data-cache residency as tightly as possible.

Required plan elements:

- dependent pointer-chase or equivalent serialization;
- `clock64` / cycle timing;
- working-set and stride sweeps;
- warmup;
- discovered rather than assumed page/reach boundaries;
- repeated samples/distribution;
- explicit data-cache confound controls;
- same-SM / occupancy control if feasible;
- no assumption that an end-to-end memory latency plateau equals pure TLB lookup latency.

Create:

`RTX4080_TLB_NATIVE_CALIBRATION_PLAN.md`

No calibration run is authorized here.

## 11. External-literature scope

Use published GPU microbenchmarking only as methodology/background unless the architecture exactly matches and the measured quantity is comparable.

Older NVIDIA GPU studies may reveal TLB hierarchy/reach or end-to-end latency plateaus, but do not transfer those cycle counts directly to RTX4080/Ada.

No literature number should silently replace missing native calibration.

## 12. No mechanism experiment

Forbidden:

- faster-TLB architecture proposal/evaluation;
- TLB capacity/ports changes;
- PTW/PWC changes;
- segmentation;
- prefetch/speculation;
- page-size changes;
- cache redesign.

This stage validates the model and the interpretation of the existing sensitivity.

## 13. Durable output

Large new logs:

`/root/share/mnt164/huangrulin/awma_q05_lookup_model_validity_v1/`

No node109 data or GPU task.

## 14. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_LOOKUP_MODEL_VALIDITY_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_LOOKUP_MODEL_VALIDITY_174NEW_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
LOOKUP_LATENCY_PROVENANCE_AUDIT.md
LOOKUP_LATENCY_EVIDENCE_MATRIX.tsv
LOOKUP_INVOCATION_ACCOUNTING.tsv
LOOKUP_STREAM_VARIATION_AUDIT.md
PROBE_TIME_COUPLING_CONTRACT.md
READ_ONLY_TELEMETRY_CONTRACT.md
NEUTRALITY_RESULTS.tsv
P34_FILL_RACE_MATRIX.tsv
P8_FILL_RACE_MATRIX.tsv
SPACE_SPLIT_TRANSLATION_MATRIX.tsv
MODEL_VALIDITY_DECISION.md
RTX4080_TLB_NATIVE_CALIBRATION_PLAN.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Success marker:

`AWMA_Q05_LOOKUP_MODEL_VALIDITY_CLOSURE_174NEW_V1_COMPLETE_WITH_SCOPE`

Then report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
