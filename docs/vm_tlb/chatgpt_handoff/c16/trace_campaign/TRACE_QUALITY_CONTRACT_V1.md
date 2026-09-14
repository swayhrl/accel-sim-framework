# C16 Trace Quality Contract V1

Ownership: ChatGPT
Status: frozen selection/capture contract

## Objective

Future NVBit traces must be selected for scientific representativeness, not merely because a static memory instruction is easy to instrument.

The 3090 Route-B history is a negative lesson: Q2 produced valid address-bearing anchors, but those anchors were explicitly only anchor-local and representative selection remained blocked because important duration mass (including unresolved CUTLASS kernels) was not covered. The new campaign must close phase/operator/launch coverage before formal tracing.

## Core rule

A formal trace target is eligible only after all of the following are known:

1. exact model/revision/input/scenario identity;
2. exact phase and launch identity;
3. exact runtime function/code-object/static-map identity;
4. semantic class or explicit UNKNOWN classification;
5. phase duration share / stratum duration mass;
6. memory-opportunity evidence from static MREF and/or bounded NCU counters;
7. expected trace size / runtime bound;
8. object-map availability for later WEIGHT/KV/other attribution;
9. target is part of a declared portfolio, not claimed to represent the whole model by itself.

## Do not repeat the 3090 anchor problem

Do NOT select a target only because:

- one LDG/LDST instruction is easy to bind;
- it already produced nonzero addresses in a canary;
- it is a small index/gather kernel;
- it has a convenient static instruction index;
- it is the first target that makes NVBit work.

Canary targets prove the tracer. They do not automatically become scientific targets.

## Formal target granularity

Preferred formal NVBit unit:

> one exact kernel launch (or a tightly bounded launch set) with ALL relevant GLOBAL memory-reference instructions captured.

Do not reduce a whole kernel to one arbitrary static instruction unless the scientific question itself is specifically about that instruction.

The memory-only record should preserve at least:

```text
run_id
kernel/function identity
code-object identity
launch identity
static instruction index/offset
opcode
load/store/atomic
width
active mask / predicate execution
lane addresses
phase
decode step where applicable
```

## Portfolio coverage

Per admitted deployment, select a small portfolio rather than one kernel.

Mandatory semantic strata when present:

```text
FFN / GEMM
ATTENTION_PROJECTION
ATTENTION_CORE
KV_MANAGEMENT or decode KV-facing kernel
EMBEDDING_OUTPUT / special memory kernel
QUANT_DEQUANT (quantized deployments)
RANDOM_AUDIT / low-mass audit target
```

Strata may be merged only when runtime evidence shows the same implementation/shape class and the scientific distinction is not material.

## Duration / heavy-tail rule

Before trace selection, build a complete lightweight launch catalog for each target scenario.

Use phase-local GPU duration mass.

A candidate is a certainty unit if any of the following holds:

1. one launch or one stable launch class contributes >= 1% of phase GPU time;
2. a semantic class is scientifically mandatory (KV, quant/dequant, E/O, router/dispatch, rare implementation);
3. the stratum has <= 2 instances;
4. excluding it would prevent >= 80% phase-duration portfolio coverage.

The final trace portfolio should aim to explain >= 80% of phase duration mass through traced or explicitly represented strata, while retaining special semantic targets even if their duration is small.

Do not invent coverage for an unmapped or failed-closed kernel.

## NCU-assisted target ranking

When available, use bounded NCU on candidate kernels to record at least a small memory-counter set (exact metrics depend on RTX4080 availability):

```text
L1/TEX traffic
L2 traffic
DRAM bytes/throughput
selected memory stall/exposure metrics
```

NCU is for target ranking/context, not a substitute for address traces.

A useful candidate is one that is important by duration/semantics and has meaningful memory activity; a tiny kernel with high memory intensity but negligible phase mass is not a default representative.

## Scenario strategy for the existing Qwen historical bindings

The 7 frozen scenarios are useful because several controlled comparisons already exist:

```text
S0_TEXT        B1 T128  D4
S1_CODE        B1 T256  D16
S2_CODE        B1 T2048 D32
S2_STRUCTURED  B1 T2048 D32
S2_TEXT        B1 T2048 D32
S3_TEXT        B1 T8192 D16
S4_STRUCTURED  B4 T2048 D16
```

Use them as follows:

- main representative scenario: `S2_TEXT`;
- short-vs-long context (same CODE): `S1_CODE` vs `S2_CODE` for Prefill;
- long-context scaling (same TEXT): `S2_TEXT` vs `S3_TEXT`;
- input-content control at identical shape: `S2_CODE/S2_STRUCTURED/S2_TEXT`;
- batch scaling at identical T2048 structured input: `S2_STRUCTURED` vs `S4_STRUCTURED` (Prefill is the cleanest comparison);
- S0 is canary only unless a specific comparison requires it.

Do not trace all 7 scenarios blindly. First use native/NSYS signatures to identify which scenarios actually change implementation/launch structure.

## Decode-specific rule

For decode studies, do not capture only one arbitrary decode launch when studying KV growth.

For a decode scenario with multiple steps, preserve step identity and prefer at least:

```text
early step
late step
```

for the same semantic target when feasible.

If early/late implementations are identical and address fingerprints are proven equivalent by a bounded audit, later campaigns may reduce sampling.

## Object-map requirement

Formal traces must have a companion runtime object map sufficient for later conservative attribution.

Minimum desired labels:

```text
WEIGHT
QUANT_METADATA
KV_CACHE
UNKNOWN_RUNTIME
```

UNKNOWN is allowed and must not be force-classified.

## Trace bounds

Default per formal target:

```text
<= 4 GiB raw
OR
<= 20 min capture time
```

whichever comes first.

If exceeded, classify `BOUNDED_PARTIAL`; do not silently truncate and call it complete.

Initial RTX4080 campaign total raw budget target:

```text
<= 64 GiB
```

unless ChatGPT explicitly expands it after reviewing useful information density.

## Quality gates

Each formal target must have:

```text
TARGET_IDENTITY_PASS
PHASE_BINDING_PASS
SEMANTIC_OR_UNKNOWN_DECLARED
STATIC_MAP_PASS
LAUNCH_BINDING_PASS
MEMORY_REFERENCE_SET_DECLARED
TRACE_BOUND_DECLARED
OBJECT_MAP_AVAILABLE
OUTPUT_CHECKSUM_STABLE
TERMINAL_COMPLETE_OR_BOUNDED_PARTIAL
RAW_SHA256_CLOSED
```

## Scientific interpretation boundary

Per-kernel trace results may support:

```text
page footprint
line footprint
sector utilization
object attribution
same-object revisit
set overlap
callback-order/local chronological reuse if ordering is preserved
```

They do NOT automatically support:

```text
whole-model global cache reuse
shared-L2 global MRC
whole-phase TLB miss rate
model-wide behavior from one kernel
```

Whole-model claims require portfolio coverage and cross-target aggregation with explicit weighting/coverage.