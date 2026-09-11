# C13 diagnostic reference anchors

## Formal C12 execution truth

Framework closeout commit:

`a268aba0d01310294074ded5bb8017e2092394c0`

Status:

`C12_C5_FULL_ROI_COMPLETE_READY_FOR_REVIEW`

Frozen execution identity:

- functional/config anchor: `d64408a97d76a320a6d49468653d416e33677af8`
- Core: `57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- linked binary SHA-256: `2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`
- Prefill trace: 692 kernels, SHA `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`
- Decode1 trace: 740 kernels, SHA `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`
- Prefill registration SHA: `6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0`
- Decode1 registration SHA: `3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48`
- PA contract: `MODELED_DRIVER_PA / C5_MODELED_PA_HIGH_UNUSED_BIT_V1`

## Existing performance anchors

### Prefill

| point | cycles | speedup vs F0 |
| --- | ---: | ---: |
| F0 exact768 | 62,490,238 | 1.000000000 |
| F7 N8 + exact320, L5 | 59,834,219 | 1.044389633 |
| F7 N8 + exact320, L10 | 63,370,888 | 0.986103240 |
| F7 N8 + exact320, L20 | 76,131,192 | 0.820823060 |
| F5 physical PWC120 + exact656 | 63,223,313 | 0.988404989 |
| F1 Sub-entry G96 | 63,758,501 | 0.980108331 |

### Decode1

| point | cycles | speedup vs F0 |
| --- | ---: | ---: |
| F0 exact768 | 34,564,626 | 1.000000000 |
| F7 N8 + exact320, L5 | 33,959,029 | 1.017833166 |
| F7 N8 + exact320, L10 | 34,432,059 | 1.003850104 |
| F7 N8 + exact320, L20 | 36,035,731 | 0.959176491 |

These are immutable C12 measured anchors. C13 must not rewrite or reclassify them.

## Accepted Operator-aware / Deep Dive references

Operator-aware final branch:

`hrl/vm-m4b-operator-aware-v0`

Accepted deep-dive handoff:

`8801f2e9fea4e0df1d79853a5e4440c4da463486`

Deep-dive review-pack commit:

`484663a46b3810df24b31d8f97cd9cdb671ed91b`

Key measured motivation:

- Prefill F1/F2, F5/F0 and F7-L10/F0 contain a dominant final Embedding/Output GEMM hotspot at compute index 691;
- Prefill F5 regression is +733,075 cycles, of which kernel 691 contributes +700,253;
- Prefill F7-L10 full ROI is +880,650 cycles vs F0, while kernel 691 alone is approximately +1.105M cycles; the remaining kernels therefore net improve;
- Direct FFN / Attention Projection layer 0–15 response is broad rather than single-layer-hotspot driven;
- Deep Dive empirical full-ROI break-even from sparse 5/10/20 points: Prefill ~8.755, Decode ~10.827, explicitly `EMPIRICAL_INTERPOLATION_ONLY`;
- Prefill Embedding/Output regresses at all measured Segment Lseg 5/10/20 points;
- Decode F8/F7 per-kernel cycles are exactly identical across all 740 kernels at Lseg 5/10/20, so Sub-entry is not a C13 priority.

These items are motivation for C13 hypotheses. They are not substitutes for the new C13 controlled measurements.

## Required operator map identity

When C13 post-processing reuses Operator-aware mapping, it must verify the same compute-list SHA and marker order before attribution.

Do not infer layer/operator labels from execution order in C13.
