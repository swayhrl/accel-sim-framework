# AWMA Discussion Reference — Per-Access VM Coverage Gate

Date: 2026-09-19

## 1. The GLOBAL stream itself is deterministic

The formal Q05 trace is not changing with lookup latency.

Generation-time canonical comparison shows identical:

- trace instruction identity;
- active mask;
- lane addresses;
- coalesced transaction output.

So the previous apparent GLOBAL stream variation was an observation artifact at the later VM boundary.

## 2. But the artifact exposed a real coverage mismatch

The same qualification reports:

```text
GLOBAL generation = 2,182,656 accesses
VM translated/READY = ~0.78M to ~0.86M
```

This means the old VM observation point did not see every generated coalesced access.

Source inspection shows why this may be architectural-model undercoverage rather than only telemetry:

```text
memory_cycle:
  translate only current back access

then:
  L1D queue loop can pop several accesses
```

Only the first access has necessarily been translated.

## 3. Why identity mapping hid the problem

For the accepted ordinary mapping:

`SimPA == SimVA`

An untranslated access still carries its original address into the lower cache path, so functional data addressing can appear correct.

But it has skipped:

- L1 TLB lookup;
- possible L2 TLB;
- MSHR;
- PTW/PWC/PTE;
- translation latency.

Therefore translation characterization can be materially wrong even when application completion and data-cache addressing look normal.

## 4. Why lookup-latency sensitivity must be requalified

Legacy P34:

```text
10/80 translated fraction relative to GLOBAL generation ~=35.6%
0/80  translated fraction relative to GLOBAL generation ~=39.6%
```

Changing lookup latency changes how often the pipeline returns to `memory_cycle()` before the downstream multi-pop path drains the queue.

That can change the fraction of accesses that actually pay translation.

This is a much stronger explanation for the previous lookup-sensitivity coupling than fill races or changing coalescing.

Until repaired, the measured 10->5/0 speedups cannot be interpreted as a clean lookup-latency opportunity.

## 5. The repair is correctness, not a mechanism

The repair does not make the TLB faster or larger.

It only enforces:

> every VM-eligible coalesced access must finish exactly one translation before it is admitted downstream.

This may naturally reduce effective memory-issue throughput under a one-port TLB. That is part of the currently modeled translation architecture, not an added optimization.

## 6. Why we do not immediately replay everything

First qualify the repair on:

- synthetic multi-access cases;
- P34 natural;
- optionally repaired target-I0 if exact semantics remain clean.

Only then decide the minimum historical results worth replaying.

Older P1/P2/P4/P16 context rows and mechanism-like diagnostics should not be rerun automatically.

## 7. node109 result in context

The native RTX4080 reconnaissance did not yield a clean pure-TLB latency value.

The `cg` targeted surface is mostly flat in location count:

- around 293 cycles/load at 4KiB stride;
- around 293-300 at 64KiB;
- around 298-302 at 256KiB;
- around 303 at 2MiB.

These are end-to-end dependent global-load measurements, not pure TLB lookup latencies.

So native evidence does not justify patching simulator 10/80 at this point.

## 8. Research direction after repair

If the repaired model still shows substantial contextual translation sensitivity, the next step should broaden from Q05 to the representative kernel families already captured:

- Prefill GEMM Primary;
- Prefill Flash;
- Decode GEMV Primary;
- Decode Flash Primary-1;
- Primary-2 only as a tiny structural control.

But that expansion must wait until per-access translation coverage is correct.
