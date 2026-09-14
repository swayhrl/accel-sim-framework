# C16 Capture Campaign Strategy V1

Ownership: ChatGPT
Status: planning baseline

## Immediate objective

Once Pipeline V1 qualifies, collect the highest-value RTX4080-admitted multi-model traces within a few hours, while avoiding the 3090 failure mode of technically valid but scientifically weak instrumentation points.

## What the 3090 history teaches

The historical Route-B campaign obtained valid Q2 dynamic address anchors, but the evidence explicitly warned that these were anchor-local rather than phase-wide. Representative selection remained blocked because substantial phase duration was tied to unresolved CUTLASS rows; Prefill mapped-exact lower-bound duration coverage was only about 61.8%, Decode about 71.9%, and the failed CUTLASS rows accounted for about 38.2% and 28.1% respectively.

Therefore the new campaign must select from a phase-wide launch catalog first, then trace a portfolio of important semantic/implementation strata.

## RTX4080 likely campaign tiers

Do not treat this as admission authority; live admission decides.

### Tier A: highest priority / likely fit

```text
Llama-3.2-1B
Qwen2.5-0.5B-Instruct
Qwen2.5-7B-Instruct-AWQ
```

### Tier B: admission test, do not force

```text
Qwen2.5-7B-Instruct raw
Qwen3-8B
```

### Tier C: expected external larger-GPU work unless live evidence proves otherwise

```text
DeepSeek-V2-Lite
Qwen3-30B-A3B
```

No CPU offload or hidden precision change is allowed to turn a Tier-B/C model into an RTX4080 result.

## Scenario efficiency policy

Use cheap native/NSYS across enough scenarios to detect implementation changes, but reserve NVBit for selected windows.

Primary scientific axes from existing Qwen bindings:

```text
Context:
S1_CODE B1 T256  -> S2_CODE B1 T2048
S2_TEXT B1 T2048 -> S3_TEXT B1 T8192

Content at identical shape:
S2_CODE / S2_STRUCTURED / S2_TEXT

Batch:
S2_STRUCTURED B1 T2048 -> S4_STRUCTURED B4 T2048

Canary:
S0_TEXT B1 T128
```

For dense models, if NSYS proves the three S2 input classes have the same implementation/launch signature, do not collect three redundant full NVBit portfolios. Keep one main (`S2_TEXT`) plus one audit input.

## First formal NVBit portfolio per deployment

Target 4–6 trace windows, chosen after census:

```text
Prefill FFN/GEMM heavy
Prefill Attention Projection or Attention Core
Decode FFN/GEMM
Decode Attention/KV-facing target
Deployment-specific special target
Random audit target
```

For AWQ, the deployment-specific slot should prioritize quant/dequant/repack/meta-access behavior if present.

For decode KV behavior, prefer early + late instances of the same target rather than unrelated arbitrary decode kernels.

## Trace content

Preferred trace is memory-only and launch-bounded:

```text
all relevant GLOBAL memory instructions in the selected launch
not one convenient LDG instruction
```

Record PC/static identity, opcode, width, active mask and lane addresses.

## Formal ordering

After Pipeline V1 PASS:

```text
1. Qwen2.5-0.5B S2_TEXT portfolio
2. Qwen2.5-7B-AWQ S2_TEXT portfolio
3. Context/batch audit windows for those deployments
4. Qwen2.5-7B raw only if RTX4080 resource admission PASS
5. Llama high-quality portfolio if needed to replace/augment the old canary-only evidence
```

This ordering maximizes early usable cross-model data.

## Stop / escalation logic

If one target exceeds 4 GiB or 20 minutes:

```text
BOUNDED_PARTIAL
```

and move to the next target; do not let one kernel consume the campaign.

If one model is not RTX4080-admitted:

```text
DEFER_RESOURCE
```

and continue other models. Do not burn hours trying to force it.

## First-campaign success definition

A few-hour campaign is considered successful if it yields:

```text
>= 2 distinct admitted model deployments
Prefill + Decode coverage
FFN + Attention + KV/special coverage
one quantized deployment
controlled context/batch audit windows
hash-closed Pipeline V1 artifacts
analysis-ready object-map companions
```

The goal is information density, not maximum trace volume.