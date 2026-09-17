# AWMA Discussion Reference — post-review decision

Date: 2026-09-17

## What the previous round established

Two independent tracks completed successfully enough to advance the science.

### 109 full frozen-workload kernel-call inventory

Accepted branch/commit:

```text
hrl/awma-qwen25-s2-census-109-v1
678d7b491d4788369ca0c22717453b20846ab195
```

The exact frozen B1/T2048/Decode32 FP16/SDPA run contains:

```text
34,677 total CUDA kernel activities
34,072 inside explicit inference ranges
408 Prefill launches
33,664 Decode launches
1,052 launches per Decode step
```

Q05 belongs to a repeated Prefill FlashAttention implementation class:

```text
10 Prefill PYTORCH_FLASH_FWD launches
all use grid 16,1,14 / block 128,1,1
Q05 duration = 159,969 ns
family median = 154,112.5 ns
family range = 146,976 .. 159,969 ns
```

Therefore Q05 is accepted as representative within this same Prefill FlashAttention family, with an upper-tail-duration caveat.

It is not representative of the whole model. In particular:

```text
Prefill CUBLAS_GEMM     = 66.48% of Prefill GPU time
Prefill FlashAttention  = 14.31%

Decode CUBLAS_GEMV      = 49.76% of Decode GPU time
Decode FlashAttention   =  9.87%
```

Decode FlashAttention uses different launch shapes, so Prefill Q05 cannot be assumed to represent Decode.

The census does not prove Transformer-layer mapping or Q/K/V semantic role. Do not infer those from launch order.

### 174-new complete Q05 structural/natural-completion analysis

Accepted branch/commit:

```text
hrl/awma-q05-full-translation-174new-v1
6415d3f1
```

Complete selected-kernel trace:

```text
224 CTA
896 warps
13,361,600 warp-instruction records
971,824 memory-instruction records
29,564,416 lane-address events
228 unique offline 64 KiB VPN
```

Natural R0 replay completes at:

```text
885,681 cycles
224 / 224 CTA issued
368,696,302 completed active thread-instructions
```

The trace-file order is structural only and is not a cross-CTA simulator-cycle timeline.

10k and 50k each have 70/224 issued CTA = 31.25% CTA-issued coverage. No valid frozen-telemetry numerator exists for cycle-keyed warp-instruction, memory-instruction or unique-page coverage, so these were correctly left unavailable.

The current classification is:

```text
MIXED
```

with one strong structural signal:

```text
125 miss requesters = 19 new translation allocations + 106 merges
max waiter depth = 35
```

Thus outstanding-translation fanout is real.

However, the previous stage did not answer the central dynamic question because current frozen telemetry cannot associate each translation key with request/fill/post-fill cycles.

The following remain unresolved:

- exact first-touch fraction;
- how many repeated misses occur before the corresponding translation fill;
- post-fill L1/L2 hit behavior;
- post-fill revisit interval;
- cycle-keyed unique-page growth;
- whether the 10k/50k windows are mainly cold-front-loaded or already representative of a warm region.

## Scientific interpretation now

The evidence does not support a simple story such as:

> FlashAttention has a low L2-TLB hit rate, therefore TLB capacity is the bottleneck.

That interpretation is too strong because:

1. only 19 independent translation allocations underlie 125 miss requesters in the 10k window;
2. translation MSHR capacity is not saturated;
3. L2-TLB port throughput was already causally downgraded by P2;
4. the full structural footprint is only 228 64 KiB pages and is highly skewed;
5. we still do not know whether same-page requests arrive before or after fill.

The strongest current hypothesis remains:

```text
long translation completion
x
high requester fanout
```

but the cold/warm/streaming decomposition must now be measured directly.

## Why the next 174-new stage is telemetry closure, not mechanism testing

The missing information is observable from the simulator if a small amount of diagnostic-only, cycle/key-aware telemetry is added.

This is preferable to immediately sweeping TLB latency or PTW modes because a mechanism sweep before knowing whether pressure is cold-first-touch, pre-fill fanout or persistent post-fill reuse risks optimizing the wrong thing.

The instrumentation must be:

- disabled by default;
- timing/functionality neutral in simulated state;
- bounded to logging/counters only;
- validated against the accepted R0 10k run before any scientific use.

The neutrality gate is mandatory. If adding telemetry changes any accepted scientific counter or execution progress, stop for review rather than explaining away the difference.

## Required dynamic translation view

Use the simulator's actual translation key semantics. Do not assume VPN alone if the implementation key contains ASID, page size, epoch or another tag.

For each translation key, obtain enough information to derive:

```text
first request cycle
first miss cycle
outstanding-translation allocation cycle
merge cycles / waiter growth
walk start/complete
translation resolution/fill cycle
first post-fill request
post-fill L1 hit count
post-fill L2 hit count
post-fill miss count
last request cycle
```

At minimum distinguish:

```text
first touch
repeated requester before fill
post-fill revisit
```

The key scientific quantities are:

```text
requests_before_fill / all requests
requests_after_fill / all requests
first-touch fraction
post-fill hit ratio
translation lifetime
fanout distribution
unique-page growth by simulator cycle
```

## Coverage closure

The previous 31.25% CTA-issued coverage is useful but insufficient.

The next stage should add same-unit diagnostic counters only if source semantics can be proven.

Preferred closure targets:

```text
completed/consumed warp-instruction records
completed/consumed memory-instruction records
unique translated-page keys touched
```

At natural completion, a valid warp/memory numerator must close against the complete structural denominator before being used for 10k/50k percentages.

Do not use `gpu_sim_insn / trace records` because `gpu_sim_insn` counts completed active thread-instructions rather than warp trace records.

## Why target selection should proceed in parallel

The full kernel census shows that Q05 is a good target for one repeated Prefill FlashAttention class, but it is not sufficient for a broader AI-workload translation claim.

The next likely simulation targets should come from families that dominate other parts of execution:

```text
Prefill: CUBLAS_GEMM
Decode:  CUBLAS_GEMV
Decode:  a representative FlashAttention shape distinct from Q05
```

The next 109 task is only to select deterministic candidate occurrences from the existing census. It must not capture them yet.

Selection should use:

- exact implementation recurrence;
- launch shape recurrence;
- launch count;
- accumulated GPU time;
- duration distribution;
- deterministic function-occurrence identity;
- existing Native-target alignment if available;
- capture feasibility.

Do not invent high-level operator labels such as Q/K/V projection unless the existing evidence proves them.

## Why the old `UNKNOWN` label must be interpreted carefully

In the first census summary, many launches were under semantic category `UNKNOWN` because high-level operator-role attribution was not proven.

However, the normalized implementation-family table already identifies major classes such as:

```text
CUBLAS_GEMM
CUBLAS_GEMV
COPY_KERNEL
```

Therefore `UNKNOWN` does not mean the kernel implementation itself is unknown; it means its high-level model operator role was not proven.

This distinction must be preserved in later reports.

## Next-stage decision tree after telemetry closure

After the 174-new timeline closes, ChatGPT should decide among at least these paths.

### Case A — cold/front-loaded + strong post-fill reuse

Focus on reducing first-translation completion latency and fanout exposure. Capacity is unlikely to be the first mechanism target.

### Case B — continuous new-page growth + weak revisit

Investigate translation reach/page-size/streaming behavior before fanout mechanisms.

### Case C — substantial post-fill reuse but long lookup-path cost remains

Causally separate lookup service latency from PTW/PTE completion latency.

### Case D — pre-fill duplicate lookup dominates while fill latency remains large

Early outstanding-translation detection/coalescing may become a secondary mechanism, but only after showing that avoiding repeated lookup work affects critical progress rather than merely event counts.

### Case E — behavior differs materially across selected kernel families

Do not force a single Q05-derived mechanism story onto all AI kernels. Use a small representative set and formulate the mechanism around the common bottleneck or explicitly scope the claim.

## Explicitly rejected for the current stage

Do not yet run:

- L2-TLB lookup-latency sweep;
- PTW fixed-latency experiment;
- walker-count sweep;
- TLB-capacity sweep;
- page-size sweep;
- Segment;
- early outstanding-translation mechanism;
- new simulator-native kernel capture.

First close the Q05 cycle/key timeline and finish candidate selection.
