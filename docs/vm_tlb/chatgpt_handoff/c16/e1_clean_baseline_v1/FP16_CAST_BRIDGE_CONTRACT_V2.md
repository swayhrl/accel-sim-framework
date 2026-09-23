# C16 E1 FP16 Cast Bridge Contract V2

## Status

This document **supersedes only** the earlier requirement that canonical BF16 activation or RAW weights must satisfy:

`BF16 -> FP16 -> BF16 bitwise equal`

That gate is removed.

All other E1 clean-baseline contracts remain unchanged.

## Why

The clean baseline is explicitly studying dtype/backend/implementation interaction.

A deterministic BF16 -> FP16 cast may legitimately incur representational rounding for BF16 values that are not exactly representable in FP16, especially at very small magnitudes.

Observed node109 characterization:

- q_proj M1: 1 / 3,584 activation elements changes after BF16 -> FP16 -> BF16 round-trip;
- all BF16 and FP16 values remain finite;
- no FP16 infinities;
- no zeros introduced;
- absolute max remains 1.8515625.

This is a representational cast effect, not evidence of model/GPU corruption.

## New bridge authority

Canonical BF16 activation remains the immutable semantic source.

For each role/shape:

1. Start from the frozen canonical BF16 tensor.
2. Cast once under the frozen runtime using the ordinary PyTorch BF16 -> FP16 conversion.
3. Freeze the resulting FP16 tensor bytes and SHA256.
4. Use **that exact FP16 tensor** for both:
   - RAW_FP16
   - AWQ_FP16_INPUT

The primary same-input gate is therefore:

> RAW_FP16 and AWQ_FP16_INPUT must consume byte-identical FP16 activation tensors.

No numerical tolerance is allowed for this identity check.

## Required cast audit

For every activation cast, record:

- source BF16 SHA256;
- destination FP16 SHA256;
- element count;
- finite/nonfinite counts before and after;
- count/fraction of values changed after FP16 -> BF16 round-trip;
- maximum absolute round-trip difference;
- maximum relative round-trip difference when denominator is nonzero;
- number of zeros introduced by cast;
- number of sign changes excluding signed-zero representation;
- source/destination min/max absolute value.

For RAW dense weights/bias cast to FP16, record the same audit.

Do not require zero changed elements.

## Scientific interpretation

### RAW_BF16 vs RAW_FP16

This comparison measures the deployed dense dtype/backend effect, including any deterministic representational rounding caused by BF16 -> FP16 conversion.

Do not call it a pure kernel-only comparison.

### RAW_FP16 vs AWQ_FP16_INPUT

This remains the cleanest primary low-bit deployment comparison because:
- activation values/bytes are exactly identical FP16;
- semantic operator and shape are fixed;
- weight representation and implementation differ.

It remains an implementation-level comparison, not pure quantization causality.

## Stop gates retained

STOP only if:
- casting introduces NaN/Inf not present in source;
- FP16 cast is nondeterministic under the frozen runtime;
- RAW_FP16 and AWQ cannot consume the exact same FP16 activation bytes without changing the accepted AWQ backend;
- RAW_FP16 requires semantic changes beyond dtype casting;
- canonical BF16 activation authority itself fails regeneration.

A small or large finite rounding count is evidence to report, not by itself a STOP condition.

## Consumer update

The 174-new consumer must replace the old gate:

`raw_bf16_to_fp16_to_bf16_bitwise_equal_required=true`

with:

- `deterministic_fp16_cast_receipt_required=true`
- `RAW_FP16_and_AWQ_same_FP16_activation_SHA_required=true`
- cast-distortion metrics independently audited and reported.

