# C16 E1 Operator-Family Expansion Before Simulator — Current State V1

## Accepted upstream

Shared-residency hardware producer:

`hrl/c16-e1-shared-residency-feasibility-109-v1@1e701f013fc174b5b4df9febb5c33500f9ea586e`

Independent shared closure / coverage consumer prep:

`hrl/c16-e1-coverage-scaling-consumer-174new-v1@5481d85951180dae90776442c3e0620af96a4712`

Coverage-scaling producer:

`hrl/c16-e1-coverage-scaling-109-v1@18acd7dcc10118c68b450d226a8e7ca80c51ad72`

## Frozen prior labels

These remain frozen and are not overwritten:

- persistence producer scoped:
  `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`
- persistence strict consumer:
  `TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`
- divergence:
  `METHODOLOGICAL_OPERATIONALIZATION`
- shared stage:
  `SHARED_RESIDENCY_LOCAL_ONLY`
- coverage producer:
  `COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD`

## Coverage producer preliminary audit

No node109 rerun is requested.

The coverage producer closes:

- all 84 requested FFN projections are AWQ qweight-backed;
- stable decode opportunity:
  - gate_proj ~14.76%
  - up_proj ~16.84%
  - down_proj ~15.78%
  - all FFN projections ~47.39%;
- up_proj selected coverage rises to ~16.63% at N28;
- every selected N28 up_proj layer remains MATERIAL_LOCAL;
- median local D3 benefit is ~25%;
- N28 whole-decode benefit is ~0.892%, above dispersion but below the 2% system gate;
- N14A/N14B are closely matched;
- FULLHINT_N28 changes FAIR_N28 by only ~0.079 percentage points.

The important new unresolved signal is realization loss as coverage grows.

Representative run-aligned medians:

- N8:
  - summed local up_proj saving ~0.1664 ms
  - observed decode saving ~0.0925 ms
  - realization ~0.56
- N14A:
  - local saving ~0.2834 ms
  - decode saving ~0.1034 ms
  - realization ~0.37
- N28:
  - local saving ~0.5674 ms
  - decode saving ~0.1229 ms
  - realization ~0.216

At N28 there are no non-selected up_proj modules left. Therefore roughly 0.44 ms of the measured local up_proj saving is not visible in whole-decode saving.

That residual is currently **unattributed**.

It may reflect:
- slowdown in gate/down or other model work due cache interference;
- policy-induced service-location tradeoffs;
- overlap/timing-boundary effects;
- another downstream effect not captured by selected up_proj timing.

Do not call it collateral slowdown until it is measured directly.

The next stage instruments all 84 FFN projections under the policy conditions so this residual can be decomposed.

## Why expand operator family before simulator

The measured FFN opportunity is ~47.4% of stable decode, versus ~16.8% for up_proj alone.

Therefore the next system-level question is:

> Under the same fixed total L2-protection budget, what happens when protection expands from all up_proj to all gate_proj, all down_proj, pairwise FFN families, and all 84 FFN projection modules?

This stage must separate:

1. direct saving in protected modules;
2. effects on non-protected FFN modules;
3. residual effect outside the measured FFN projection set;
4. whole-decode benefit.

This is the deciding real-hardware stage before bounded trace + simulator implementation.

## Simulator remains inactive

No simulator is run in this stage.

If a later simulator mechanism is authorized, the frozen authority remains:

- Core:
  `swayhrl/gpgpu-sim@57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- RTX4080 platform:
  `RTX4080_ADA_ACCELSIM_BASE_V1`
- config:
  `configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config`
- config SHA:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`

No RTX3080/SM86 configuration is authorized for the first residency mechanism experiment.
