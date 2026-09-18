# CODEX NEXT STAGE — 174-new Q05 Contextual Lookup-Path Decomposition V1

Date: 2026-09-18

Status: ACTIVE MAINLINE.

Stage:

`AWMA_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1`

Node:

`174-new / port 2239`

## 0. Scientific reason

The accepted context-effect decomposition established a large target-only translation sensitivity under realistic context:

```text
FORMAL_ISOLATED: 864552 -> 670682  (-22.42%)
P2:              848511 -> 701244  (-17.36%)
P8:              835145 -> 664241  (-20.46%)
P34:             871835 -> 674121  (-22.68%)
```

P34 has only:

```text
15 walks
249 L2-TLB misses
3414 L1-TLB misses
773501 L1-TLB hits
```

yet eliminating the whole Q05 translation path saves 197714 cycles.

Therefore the next question is no longer whether cold PTW exists. It is:

> Which portion of the remaining contextual translation sensitivity comes from the always-paid L1 lookup path, the L2 lookup path, and the remaining miss/walk path?

No architecture mechanism is introduced in this stage.

## 1. Coordination and parent

Read coordination branch:

`hrl/awma-q05-contextual-lookup-decomposition-handoff-v1`

Execution parent:

```text
hrl/awma-q05-context-effect-decomposition-174new-v1
b24edffd7a90fc6417b95c6d4198f5c40dcf0b35
```

Recommended execution branch:

`hrl/awma-q05-contextual-lookup-decomposition-174new-v1`

Accepted context bundle, F0 config and framework/core identities remain immutable.

## 2. D0 — Correct the isolated-control identity before any new claim

This is a scientific bookkeeping correction, not a new experiment.

The historical isolated-Q05 run:

`885681 cycles`

came from the earlier standalone Q05 capture/input identity.

The decomposition stage created a **formal isolated member34 control from the same admitted 35-member context bundle**:

`864552 cycles`

Use the formal isolated member34 control for all same-trace comparisons against P2/P8/P34.

The old historical isolated run remains valid as a historical cross-capture result, but must not be used for direct same-trace cycle deltas.

Carry forward:

```text
FORMAL_ISOLATED_R0 cycles = 864552
P2_R0              cycles = 848511   (-1.86% vs formal isolated)
P8_R0              cycles = 835145   (-3.40%)
P34_R0             cycles = 871835   (+0.84%)
```

For the same formal trace:

```text
walks:       240 -> 15      (formal isolated -> P34)
L2-TLB miss: 731 -> 249     (-65.94%)
```

Thus full real predecessor history removes almost all walks and most L2-TLB misses, but the **net Q05 cycle effect is slightly worse than the same-trace isolated control**.

Create:

- `SAME_TRACE_BASELINE_IDENTITY_ADDENDUM.md`
- `SAME_TRACE_CONTEXT_COMPARISON.tsv`

Do not rewrite historical review packs.

## 3. D1 — Source-backed lookup-path audit

Close the accepted modeled latency contract before changing anything.

Accepted core defaults:

```text
L1 TLB lookup latency = 10 cycles
L2 TLB lookup latency = 80 cycles
PWC lookup latency    = 1 cycle
```

Accepted P34 natural telemetry:

```text
L1 lookup requesters       = 776915
L1 hits                    = 773501
L1 misses                  = 3414
L1 requester service total = 7769150 = 776915 * 10

L2 accesses                 = 3414
L2 hits                     = 3165
L2 misses                   = 249
L2 requester service total  = 273120 = 3414 * 80

MSHR-wait total             = 434431
L2 queue total              = 681
total requester latency     = 8477382
```

Derived composition for P34:

- L1 service ~= 91.65% of requester-latency sum;
- L2 service ~= 3.22%;
- MSHR wait ~= 5.12%;
- L2 queue ~= 0.01%.

Important boundary:

These are **summed requester-cycles**, not exposed GPU cycles. Do not convert the percentage composition directly into predicted speedup.

Also record:

```text
P34 L1 hit rate ~= 99.56%
P34 L2 hit rate among L1 misses ~= 92.71%
L2 misses / L1 lookup requesters ~= 0.032%
walk allocations / L1 lookup requesters ~= 0.0019%
```

This motivates lookup-path decomposition but does not prove L1 lookup is the exposed-cycle bottleneck.

Create:

`LOOKUP_PATH_SOURCE_AND_COUNTER_AUDIT.md`

## 4. D2 — Target-only latency override diagnostic

All predecessor kernels remain natural accepted F0/R0.

Only exact Q05/member34 may use latency overrides.

The diagnostic must preserve:

- existing L1/L2 TLB contents built by predecessors;
- TLB capacity/associativity;
- TLB replacement behavior;
- L1/L2 port counts and port arbitration;
- MSHR/PWQ/walker behavior;
- PWC and PTE behavior;
- lower cache/DRAM mapping;
- same SimVA->SimPA mapping;
- no reset/flush/preload at Q05 entry.

Change only lookup service latency for exact target Q05.

### Preferred implementation

Add a disabled-by-default diagnostic override to the persistent translation controller.

At the first exact-Q05 translation request:

- exact target UID is checked;
- controller must be quiescent from predecessor translation work;
- effective target L1/L2 lookup latencies are overridden;
- override is idempotent for the remainder of the final Q05 member;
- no predecessor sees the override.

Because Q05 is the final member in all contextual rows, restoration after target completion is not required for scientific execution, but the diagnostic runtime should still avoid leaking state into unrelated runs.

Accepted source already supports zero-cycle lookup service in the legacy diagnostic path via same-cycle `service_lookups()` handling. Verify this path rather than inventing a new zero-latency semantics.

Do not globally change F0 config before the prefix.

## 5. D3 — Neutrality gate

With the new diagnostic runtime present but no latency override enabled, reproduce:

```text
P8_R0_CONTROL
P34_R0_CONTROL
```

Exactly for all accepted scientific counters used in the previous stage.

Also rerun:

`P34_Q05_I0_CONTROL`

with the new diagnostic binary and require the target-I0 cycle result to reproduce the accepted prior I0 within deterministic identity.

This keeps all lookup-sensitivity points on one diagnostic runtime.

If neutrality fails, repair before proceeding.

## 6. D4 — Main latency decomposition matrix

### P34 — realism reference, full matrix

Fresh process for every row; prefix remains natural R0.

Run:

```text
P34_R0_L1_10_L2_80
P34_L1_5_L2_80
P34_L1_2_L2_80
P34_L1_0_L2_80
P34_L1_10_L2_40
P34_L1_10_L2_0
P34_L1_0_L2_0
P34_Q05_I0
```

### P8 — screening candidate, reduced matrix

Run:

```text
P8_R0_L1_10_L2_80
P8_L1_5_L2_80
P8_L1_0_L2_80
P8_L1_10_L2_0
P8_L1_0_L2_0
P8_Q05_I0
```

Do not change TLB capacity, ports or page size in this matrix.

## 7. D5 — Required telemetry for every point

Report Q05-only:

- cycles;
- active-thread instructions;
- CTA count;
- L1 TLB accesses/hits/misses;
- L2 TLB accesses/hits/misses;
- L1/L2 lookup launches/completions;
- L1/L2 lookup service-cycle totals;
- L1/L2 port stalls;
- MSHR alloc/merge/full/HWM;
- walk starts/completions;
- PWC;
- PTE requests and L2/DRAM split;
- requester latency decomposition;
- L2 data-cache accesses/misses;
- DRAM/request/command counters used in prior natural audit.

The target latency override should preserve hit/miss counts as far as ordering allows. If latency changes alter replacement/order enough to change hit/miss counts, report this explicitly; do not silently treat the run as a pure additive-latency subtraction.

## 8. D6 — Residual miss/walk-path test

Use:

```text
P34_L1_0_L2_0
vs
P34_Q05_I0
```

Interpretation:

- if these are close, most of the target-I0 sensitivity is explained by modeled L1/L2 lookup service;
- if a large gap remains, the remaining miss-path/MSHR/PTW/PWC/PTE machinery still matters even with zero lookup service.

If the residual is >3% of P34 R0 cycles, perform one additional **source-backed diagnostic only**, not a mechanism:

`P34_FORCE_L1_HIT_AT_NATURAL_L1_LATENCY`

Semantics:

- exact Q05 only;
- preserve normal L1 port arbitration and 10-cycle L1 service;
- after service, resolve identity-compatible mapping as a synthetic L1 hit;
- suppress target L2/MSHR/PTW/PWC/PTE path;
- no predecessor changes.

This optional point separates:

```text
always-paid L1 lookup service
from
all downstream miss-path cost
```

Only implement if the 0/0-vs-I0 residual makes it scientifically useful.

## 9. D7 — Analysis questions

Answer quantitatively:

1. What fraction of the P34 target-I0 cycle sensitivity is recovered by L1 latency 10->5, 10->2 and 10->0?
2. What fraction is recovered by L2 latency 80->40 and 80->0?
3. Is the P34 response approximately monotonic?
4. Does L1=0 alone approach L1/L2=0?
5. How large is the remaining 0/0 -> I0 gap?
6. Does P8 reproduce the direction and approximate normalized sensitivity of P34?
7. Can P8 now be frozen as the **screening prefix** while P34 remains the **final realism reference**?
8. Does the evidence support moving the main research focus away from PTW frequency toward the translation hit/lookup path?
9. If so, which modeled property needs the next scientific characterization:
   - L1 lookup latency;
   - L1 lookup serialization/issue interaction;
   - L2 lookup service;
   - downstream miss path?

Do not design a new architecture mechanism yet.

## 10. Claim boundaries

Allowed:

- contextual translation-path latency sensitivity;
- source-modeled lookup-path decomposition;
- same-trace baseline comparison;
- screening-prefix methodology conclusion if supported.

Not allowed yet:

- "real RTX4080 TLB hit latency is 10 cycles";
- "hardware gets 22% from faster TLB";
- "a zero-cycle TLB is implementable";
- mechanism speedup claims;
- using requester-cycle sums as GPU-cycle sums.

## 11. Durable output

Large new logs:

`/root/share/mnt164/huangrulin/awma_q05_contextual_lookup_path_decomposition_v1/`

174 local disk remains bounded scratch/source only.

## 12. Deliverables

Report:

`docs/vm_tlb/codex_handoff/awma/Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1_REPORT.md`

Review pack:

`docs/vm_tlb/review_packs/AWMA_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1/`

At minimum:

```text
README.md
SOURCE_ANCHORS.md
SAME_TRACE_BASELINE_IDENTITY_ADDENDUM.md
SAME_TRACE_CONTEXT_COMPARISON.tsv
LOOKUP_PATH_SOURCE_AND_COUNTER_AUDIT.md
TARGET_ONLY_LOOKUP_LATENCY_CONTRACT.md
DIAGNOSTIC_BINARY_RECEIPT.md
NEUTRALITY_RESULTS.tsv
P34_LOOKUP_LATENCY_MATRIX.tsv
P8_LOOKUP_LATENCY_MATRIX.tsv
P34_ZERO_LOOKUP_VS_I0.tsv
OPTIONAL_FORCE_L1_HIT.md
SCREENING_PREFIX_DECISION.md
RUN_RECEIPTS.json
RAW_DATA_INDEX.tsv
SHA256SUMS
```

Success marker:

`AWMA_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1_COMPLETE_WITH_SCOPE`

Then report -> review pack -> hashes -> commit -> push -> remote verify -> clean -> STOP.
