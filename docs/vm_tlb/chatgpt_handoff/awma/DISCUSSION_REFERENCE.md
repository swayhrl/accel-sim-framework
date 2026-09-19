# AWMA Discussion Reference — Global Access Determinism

Date: 2026-09-19

## 1. The surprising result has moved upstream of translation

The previous stage showed that shorter target lookup timing increases the number of GLOBAL `mem_access_t` objects reaching VM translation.

This is not:

- a post-READY retranslation effect;
- a LOCAL-memory remapping effect;
- a PARAM_LOCAL effect.

Therefore the investigation must move to trace identity and access generation.

## 2. Why this should normally be deterministic

For a trace-driven GLOBAL memory instruction, the trace supplies:

- PC;
- active mask;
- per-lane memory addresses.

The trace-driven instruction copies those values directly.

GLOBAL addresses are not remapped based on SM/CTA placement.

The coalescer then deterministically groups those lane addresses into memory transactions under the fixed GPU coalescing configuration.

So, for the same canonical trace instruction input:

`same input -> same coalesced output`

is the expected source contract.

## 3. Aggregate equality is not enough

The previous stage only established:

```text
same total GLOBAL dynamic_insts
same total active lanes
different total GLOBAL generated accesses
```

Those totals could hide one of several cases:

1. different trace instruction instances are being bound/executed;
2. per-instruction active masks differ but totals happen to match;
3. per-lane addresses differ;
4. identical inputs somehow produce different coalescing outputs;
5. access objects are regenerated/duplicated;
6. the previous VM-boundary telemetry misses or reclassifies generation-time objects.

The next stage distinguishes these explicitly.

## 4. Runtime inst_uid cannot be the canonical join key

Runtime instruction UID is assigned by issue order, which changes with timing.

Cross-run comparison therefore needs a trace-native identity:

```text
trace thread-block coordinates
trace warp id
trace instruction ordinal
```

The parser already reads these fields.

That makes the comparison independent of CTA scheduling order and simulator timing.

## 5. Generation-time instrumentation is stronger than memory-cycle observation

The prior telemetry first observes a `mem_access_t` when it reaches `memory_cycle()`.

The next stage records immediately around:

`generate_mem_accesses()`

This directly measures the coalescer input and output before cache/translation retry behavior.

Then it checks conservation from generation to VM boundary.

## 6. Why this is now a correctness gate

If identical canonical trace input produces different GLOBAL coalesced output under different TLB latency:

- that is not an architecture opportunity;
- it is a simulator state-coupling/correctness issue.

If canonical inputs themselves differ:

- the trace instance/binding or execution stream is timing dependent;
- that also must be understood before mechanism evaluation.

Either way, the project should not optimize the TLB against a stream whose identity is not closed.

## 7. Interaction with node109

109's native reconnaissance remains useful, but it answers a different question.

109:
> what native translation-related timing/reach knees can be observed on RTX4080?

174:
> is the simulator feeding the same GLOBAL memory transaction stream when only lookup timing changes?

Both are necessary; neither substitutes for the other.
