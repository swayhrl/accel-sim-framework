# ADR-001 — EP-L2 Primary Research Objective

## Context

Calibration shows that a real L2 structural blocker can be removed without immediately improving application cycles because pressure moves to a later resource. Requiring every L2 improvement to show direct end-to-end speedup would conflate L2 quality with the state of the entire memory hierarchy.

## Decision

The primary EP-L2 objective is:

> At comparable L2 storage budget and basic L2 timing, improve the L2's ability to sustain concurrent misses, pending transactions, and payload state while reducing structural blocking caused by static resource/lifetime coupling.

End-to-end performance remains a stronger outcome, but L2-local structural/service improvement is a valid separately labeled result.

## Alternatives

### Speedup-only objective

Rejected because it would discard real L2 bottleneck relief whenever L1/DRAM/lower-path resources become the new limit.

### Counter-reduction-only objective

Rejected because raw retry/block counters can be non-causal or repeatedly count one logical request.

## Evidence required

Use the three-level evidence model:

```text
L2 structural pressure
L2 service effectiveness
system performance
```

and explicitly report bottleneck substitution.

## Consequences

Future mechanism papers must separate `better L2` claims from `faster full system` claims and must not imply performance benefit from structural-block reduction alone.
