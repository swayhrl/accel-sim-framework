# AWMA Discussion Reference — Contextual Translation Lookup Path

Date: 2026-09-18

## 1. Two different effects are now established

Real predecessor history has two opposing effects on Q05.

### Translation warmup

The same-trace isolated member34 has:

```text
240 walks
731 L2-TLB misses
```

P34 has:

```text
15 walks
249 L2-TLB misses
```

So real history dramatically warms the translation hierarchy.

### Other inherited state

Yet same-trace cycles are:

```text
formal isolated = 864552
P34             = 871835
```

P34 is slightly slower overall.

Therefore "warmer translation state" and "faster Q05" are not equivalent.

## 2. Why the old 885681 isolated result is no longer the primary denominator

The historical standalone Q05 trace remains valid evidence for that standalone capture.

But the formal context bundle was collected in a different same-run execution with its own address/context identity.

The new formal isolated member34 control uses exactly the same target trace identity as the contextual rows.

This is the correct control when asking what predecessor state changes.

The old 885681 number remains useful for cross-capture reproducibility/context sensitivity, but not for the primary contextual cycle delta.

## 3. The surprising residual translation sensitivity

Even under P34:

```text
L1 hit rate ~= 99.56%
L2 hits among L1 misses ~= 92.71%
walk starts = 15
```

Yet target-only I0 gives:

```text
871835 -> 674121
```

a 22.68% cycle sensitivity.

That means the remaining modeled opportunity cannot be described as "too many page walks".

## 4. The accepted model charges lookup service even on hits

The accepted translation model assigns:

```text
L1 lookup service = 10 cycles
L2 lookup service = 80 cycles
```

P34 records:

```text
776915 L1 lookup requesters
3414 L2 lookups
```

so the summed requester service composition is dominated by L1 service.

This does not mean 7.77 million L1 requester-cycles appear directly on the critical path. Many requesters overlap.

The correct way to measure exposed sensitivity is to change only target lookup latency and observe total Q05 cycles.

## 5. Why target-only latency changes are mandatory

Changing F0 lookup latency for the whole prefix would alter predecessor timing and the state delivered to Q05.

That would recreate the context-confounding problem.

Therefore:

```text
predecessors = natural 10/80
Q05          = selected diagnostic latency
```

The persistent TLB contents remain inherited from the real prefix.

## 6. The matrix answers a decomposition question, not a mechanism question

The next points are diagnostics:

```text
L1 10 -> 5 -> 2 -> 0
L2 80 -> 40 -> 0
combined 0/0
I0
```

They ask how sensitive the accepted model is to each part of lookup service.

They do not claim that a zero-cycle TLB can be built.

## 7. How to interpret 0/0 versus I0

If zero L1/L2 lookup service nearly reaches I0, the residual contextual translation sensitivity is mainly in lookup service.

If a large gap remains, MSHR/walk/PWC/PTE miss-path work still contributes meaningfully.

This is the cleanest bridge from characterization to deciding what kind of architecture question is worth studying.

## 8. P8 and P34

P8 and P34 have similar target-I0 sensitivities:

```text
P8  = 20.46%
P34 = 22.68%
```

but their natural cycles differ substantially.

The next latency matrix determines whether they respond similarly to the same lookup-path perturbations.

If so, P8 can be frozen as a fast screening prefix while P34 remains the final realism reference.

## 9. No mechanism claim yet

Only after this decomposition should the project decide whether to study:

- faster L1 translation hit path;
- L1 lookup scheduling/overlap;
- L2 service;
- miss-path/PTW.

Do not decide from walk counts or cumulative requester latency alone.
