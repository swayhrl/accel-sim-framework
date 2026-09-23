# C16 E1 Coverage Scaling Under Fixed L2-Protection Budget — Current State V1

## Accepted upstream hardware closure

Targeted persistence producer:
`hrl/c16-e1-l2-persistence-intervention-109-v1@4c0e6b998528e425578cacf5912bbcc4ff3bfaf6`

Independent persistence consumer:
`hrl/c16-e1-l2-persistence-intervention-consumer-174new-v1@1dcab9c8d932973399c5811dc817802bfb3b9dfe`

Shared-residency producer:
`hrl/c16-e1-shared-residency-feasibility-109-v1@1e701f013fc174b5b4df9febb5c33500f9ea586e`

Shared-residency design/consumer prep:
`hrl/c16-e1-shared-residency-design-review-174new-v1@547e9263a8d0c12bb34d96e27134a120b83fb6d0`

Latest shared consumer hardening:
`hrl/c16-e1-shared-residency-consumer-hardening-v2@87998e7fcdcc1422ca87e8814bf054cb65161657`

## Frozen prior states

These remain frozen and are not overwritten by the new stage:

- producer-scoped state:
  `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`
- strict persistence-consumer state:
  `TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`
- divergence:
  `METHODOLOGICAL_OPERATIONALIZATION`
- shared-hardware producer stage:
  `SHARED_RESIDENCY_LOCAL_ONLY`

## What the shared-hardware stage actually established

Under one fixed full-qweight persisting-L2 budget:

- SHARE2_UP:
  - L0 up local D3 timing benefit ~42.5%
  - L14 up ~43.0%
- SHARE2_L0:
  - L0 up ~31.25%
  - L0 down ~10.96%
- SHARE3:
  - L0 up ~36.25%
  - L14 up ~35.44%
  - L0 down ~5.48%

At least two selected targets remain materially faster in every shared condition.

However stable D1-D3 full decode improves only:

- SHARE2_UP: ~0.347%
- SHARE3: ~0.381%
- SHARE2_L0: approximately neutral

This does not mean the local benefit fails to reach the full decode.

Direct decomposition of the accepted producer medians shows that in SHARE3:

- the three measured targets occupy only ~1.74% of a stable decode step;
- their summed local time saving is ~0.42-0.47% of the decode step;
- the observed whole-decode saving realizes roughly 79-89% of that summed local saving.

Therefore the key unresolved question is now **coverage**, not whether local residency works.

## Prior simulator-line evidence relevant to coverage

The accepted historical C12 operator-aware analysis is not direct evidence for qweight residency, but it is relevant motivation:

- direct FFN and Attention Projection responses were broadly repeated across directly attributable layers;
- the effect was not generally concentrated in one or two layers;
- in representative Decode comparisons, hundreds of kernel markers changed rather than a single hotspot dominating.

This prior must be used only as a qualitative reason to test broader layer coverage.
It must not be used to predict the quantitative benefit of qweight persistence.

## Simulator platform status

No simulator run is part of this coverage-scaling stage.

For any later mechanism experiment, the currently accepted platform authority is:

- Core code authority inspected for L2 mapping:
  `swayhrl/gpgpu-sim@57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- RTX4080 configuration:
  `RTX4080_ADA_ACCELSIM_BASE_V1`
- config:
  `configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config`
- platform requalification:
  `RTX4080_ADA_PLATFORM_QUALIFIED`
- config SHA256:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`

The configuration is scoped to memory/translation/cache mechanism studies; it is not claimed as universally cycle-accurate RTX4080 fidelity.

## Next scientific question

> With the total persisting-L2 budget held fixed, how does local retention and full-decode benefit scale as the protected up_proj coverage expands from a few layers to the full 28-layer model?

This stage deliberately measures the Amdahl/coverage curve before authorizing simulator mechanism implementation.
