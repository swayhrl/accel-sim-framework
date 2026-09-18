# AWMA Discussion Reference — Context Effect Decomposition

Date: 2026-09-18

## 1. The contextual experiment changes the TLB/PTW story

The original isolated Q05 replay showed large translation sensitivity and 240 natural walks.

The full real predecessor history changes that picture:

```text
isolated walks = 240
P34 walks      = 15
```

That is a 93.75% reduction in modeled walk starts.

Yet total Q05 cycles improve only 1.56%.

Therefore the project must separate:

```text
cold-start translation activity
from
remaining translation performance sensitivity
from
non-translation predecessor-state effects
```

These are different questions.

## 2. What is now strongly supported

Real predecessor context matters.

It converts most Q05 L2-TLB misses/walk demand into warm-state hits:

```text
L2-TLB miss: 633 -> 249
walks:       240 -> 15
PWC misses:   70 -> 3
PTE req:     310 -> 18
```

So a mechanism whose motivation is primarily "Q05 launches cold and repeatedly walks pages" would be over-motivated by isolated replay.

## 3. Why total cycles remain non-monotonic

P8 is faster than P16/P34 even though its translation counters are not better.

Most clearly:

```text
P8:
cycles 835145
walks 16
L2-TLB miss 292

P16:
cycles 862623
walks 16
L2-TLB miss 241
```

The translation requester-latency sum is also lower in P16, and aggregate L2 data misses are lower.

So the P8/P16 cycle gap cannot reasonably be described as "more TLB/PTW overhead".

Some other inherited state/history is affecting execution.

The next stage first mines existing memory-system/pipeline counters rather than immediately adding new mechanisms.

## 4. Why Q05-only ideal translation is the right next counterfactual

Running the entire prefix under I0 would be scientifically wrong for this purpose.

It would change:

- predecessor timing;
- predecessor TLB/PTE traffic;
- persistent cache state;
- potentially lower-memory temporal behavior.

Then Q05 would start from a different context.

Instead:

```text
prefix = natural R0
Q05    = ideal translation only
```

This preserves the realistic predecessor-created cache/memory context and asks a direct causal question:

> If Q05's translation path disappeared at target entry, how much faster would Q05 itself become?

That is the relevant upper-bound diagnostic before designing a translation mechanism.

## 5. Why P2, P8 and P34 are chosen

P2 represents a partially warmed translation state.

P8 is the first prefix where translation-relevant page coverage is near saturated and walks collapse to 16.

P34 is the full real-context reference.

Comparing target-only I0 across these three points tests whether residual translation sensitivity changes as context becomes realistic.

## 6. P8 is not automatically the baseline

P8 has the lowest observed cycles, but that alone is not a reason to promote it.

P34 contains the complete real predecessor history.

P8 may become a useful **screening** prefix only if the next target-only ideal-translation experiment shows that its translation sensitivity is representative of P34.

Any final mechanism claim would still need P34 validation unless a later methodology stage justifies otherwise.

## 7. PTW may no longer be the dominant mechanism target

Under P34, only 15 walks remain.

If Q05-only ideal translation gives only a small additional speedup, PTW/PWC-focused mechanisms should be strongly downgraded for this workload/context.

If a substantial ideal gap remains despite only 15 walks, the residual modeled cost likely comes from the lookup/service path rather than walk frequency alone.

That would motivate a different mechanism decomposition.

## 8. Non-translation context need not be fully solved before the translation decision

The project should distinguish two questions:

1. what causes P8/P16/P34 total-cycle differences?
2. how much Q05 translation-path cost remains under P34?

Question 2 can be answered directly with Q05-only ideal translation even if question 1 is not fully attributed to one exact L2/DRAM structure.

Therefore the next stage prioritizes the target-only counterfactual and treats L2-boundary ablation as optional, source-safe diagnostics only.

## 9. No mechanism yet

Do not start L2-TLB latency, PTW, capacity, page-size, Segment or prefetch experiments until the contextual target-only ideal result is reviewed.
