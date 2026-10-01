# R19 status after Lane F V1 and Lane E scout

Date: 2026-10-01

## Lane F

Parent execution:
- branch: `hrl/awma-r19-fp8-readiness-109-v1`
- commit: `63de02aa82587680baca665d09101dc8c67222a2`
- formal label: `R19_FP8_RESULT_MIXED_NEEDS_REVIEW`

Review interpretation:
`NUMERICAL_CONTRACT_DECOMPOSITION_REQUIRED`

The V1 stop remains valid. The failed original-BF16 vs full-FP8 allclose must not be relaxed.

Authorized follow-up:
- handoff branch: `hrl/awma-r19f1-fp8-numeric-decomposition-handoff-v1`
- handoff HEAD: `6ac000ce411dad034eeeb1f88a8e58fb180a5ead`
- execution branch: `hrl/awma-r19f1-fp8-readiness-109-v1`
- Goal: `docs/vm_tlb/chatgpt_handoff/awma/r19f1_fp8_numeric_decomposition_v1/LANE_F_R19F1_FP8_NUMERIC_DECOMPOSITION_109_GOAL.md`

R19F1 separates:
1. original BF16 -> FP8 representation distortion;
2. FP8 consumer compute error on the represented values.

The causal readiness test is same-contract A1 online representation preparation versus D0 same represented FP8 input already ready + same FP8 consumer.

## Lane E

Parent scout:
- branch: `hrl/awma-r19-ibp-consumer-scout-174new-v1`
- commit: `bdd85bde5fe7dab1555f52ec6201f7765bbacc2d`
- tree: `2adfae2496e128e3cab6244e8efb98b67d4ff460`
- formal label: `R19_IBP_DIRECT_CONSUMER_CANDIDATE_QUALIFIED`

Accepted interpretation:
- Legion/Reddit IBP path reconstructs the selected minibatch features into a dense GPU buffer before the first GraphSAGE consumer;
- exposed wait exists at the whole producer path, but dense materialization cost is not isolated;
- broad decode+GEMM/direct-decode claims are already covered by ZipServ/tile-rANS/GEMM/nvCOMP-class work.

Do **not** launch the prepared Native test yet because the proposed direct-consumer implementation crosses sampler/trainer process boundaries and may change GraphSAGE feature reuse or FP32 aggregation order.

CPU-only follow-up:
- branch: `hrl/awma-r19e1-ibp-direct-consumer-design-174new-v1`
- HEAD: `0397946d148aa1aa79895813747e6d17140dc56b`
- Goal: `docs/vm_tlb/chatgpt_handoff/awma/r19e1_ibp_direct_consumer_design_v1/LANE_E_R19E1_IBP_DIRECT_CONSUMER_DESIGN_GOAL.md`

R19E1 selects exactly one least-invasive same-semantics diagnostic from:
- sampler-side first-layer fusion;
- tile-sized staging;
- decode-inside-first-layer custom diagnostic.

No CUDA/109/Accel-Sim work is authorized in R19E1.

## Lane G

No status change in this file.
Lane G fast-weight authority Goal continues under:
`hrl/awma-r19-fastweight-authority-109-v1`

Lane F and Lane G continue sharing:
`/data/c16/locks/c16_gpu_campaign.lock`

Lane E is CPU/source-only.
