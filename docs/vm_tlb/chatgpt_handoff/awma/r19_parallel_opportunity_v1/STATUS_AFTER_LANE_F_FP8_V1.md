# R19 Lane F status after FP8 V1

Date: 2026-10-01

Execution authority:
- branch: `hrl/awma-r19-fp8-readiness-109-v1`
- commit: `63de02aa82587680baca665d09101dc8c67222a2`
- formal label: `R19_FP8_RESULT_MIXED_NEEDS_REVIEW`

## Accepted facts

- real Qwen2.5-0.5B layer0 up_proj input and real weight were frozen;
- TE v2.19.0 current-scaling FP8 path is available on RTX4080/SM89;
- TE produced native FP8 input and cached weight representations;
- final current-scaling canary was finite with cosine 0.9992078, mean abs error 0.00873995, max abs error 0.1171875 versus the original-BF16 linear reference;
- the preregistered elementwise atol=0.0675 / rtol=0.125 allclose gate failed;
- therefore A0/A1/D0 formal timing and profiler stages did not run;
- FP8 GEMM kernel identity was not independently profiled.

## Review finding

The V1 numerical gate combined two distinct effects:

1. real BF16 input/weight -> FP8 representation distortion;
2. FP8 GEMM / TE consumer execution on that representation.

TE v2.19 tests do use `quantization_tols` for quantized GEMM outputs, but the relevant TE test helper first quantizes test inputs/weights and copies the resulting representable values into the high-precision reference tensors. Thus the unit-test comparison is representation-matched; it is not evidence that an arbitrary original BF16 GEMM output must satisfy the same elementwise tolerance after input and weight quantization.

Therefore V1 is a valid preregistered STOP but should not be interpreted as:
- TE FP8 compute being numerically broken;
- Ada FP8 being unsuitable for the real Qwen shape;
- no representation-readiness performance question existing.

It is a numerical-contract decomposition issue.

## Recommended bounded follow-up — not yet authorized

R19F1 should reuse the exact same real payload, shape, TE source and current-scaling recipe.

Qualification should separate:

- `BF16_ORIGINAL`: original real BF16 input/weight linear output, descriptive format-quality reference;
- `FP8_REP_MATCHED_REF`: dequantize the exact TE-produced FP8 input and weight representation, then compute a high/BF16 reference on those represented values;
- `TE_FP8`: native TE FP8 consumer output.

First qualify `TE_FP8` against `FP8_REP_MATCHED_REF` using a source-backed numerical contract. Report `BF16_ORIGINAL` versus `FP8_REP_MATCHED_REF` separately as representation distortion, without claiming application-level quality equivalence.

If the native path qualifies, the causal performance comparison should be:

- A1: full online representation-readiness + FP8 consumer;
- D0: the same FP8 representation already ready + the same FP8 consumer, only if a public/official TE path can consume the prequantized representation.

A1 vs D0 has the same FP8 numerical contract and is the relevant readiness-residual test.
BF16 A0 remains context only; A0-A1 is a numerical-format tradeoff, not architecture headroom.

No threshold relaxation of the V1 contract is allowed; this is a new decomposition contract.

Lane G and Lane E continue independently under their existing Goals.
No R19F1 execution branch is authorized by this status file.
