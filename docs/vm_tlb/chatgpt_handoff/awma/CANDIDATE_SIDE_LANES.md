# AWMA Candidate Side Lanes

Date: 2026-09-20
Status: FROZEN CANDIDATE REGISTRY

This file separates promising research candidates from the active AWMA mainline.

## Candidate A — Q30 MoE routing-skew / expert-granularity

Accepted anchor:

`hrl/awma-109-moe-routing-skew-20h-v1`

`ed645f3aec0fe4623e1895dee2754ece0ab063f1`

Accepted evidence includes:

- exact Q30 expert harness;
- N/P/U-active controls;
- natural 93-expert histogram;
- deterministic skew continuum;
- expert-shape curve;
- S0/T128 holdout;
- bounded NCU evidence.

Current interpretation:

- S2/T2048 shows a strong skew/timing relation;
- S0/T128 does not reproduce the same benefit;
- effect is token-population / expert-granularity dependent;
- synthetic routes do not support a model-quality claim.

Status:

`HIGH_VALUE_RESEARCH_CANDIDATE / SIDE_LANE_FROZEN`

### Active causal-closure continuation

The subsequently launched stage:

`AWMA_109_MOE_CAUSAL_CLOSURE_AND_SCALE_PHASE_DIAGRAM_20H_V1`

is not admitted as mainline.

User reports C2 has frozen a 10-block x 22-condition randomized interleaved schedule and started background serial execution.

New status:

`PAUSE_REQUESTED_FOR_AWMA_MAINLINE`

Already completed C2 blocks/conditions remain valid partial candidate evidence if their receipts are intact.

Do not discard them.

Do not continue launching new blocks after the smallest safe checkpoint.

Future reactivation question, if approved:

> Is the skew effect robust after independent degree realizations/interleaving, and which semantic-preserving component causes it?

## Candidate B — Raw/AWQ shape-dependent implementation policy

Accepted anchors include:

- `56096d32bd5cd783286e1b5e5e612b6019f926d0`
- `c766a9d8ede59ef4b81ffd151ac49c839495a115`

Accepted evidence includes:

- cross-shape output-oracle invalidation;
- frozen AutoAWQ source/runtime;
- M1023/M1024 QUANT_GEMM -> DEQUANT_MATMUL transition;
- raw/AWQ M1/M256 timing;
- same-qweight A/B/C decomposition;
- isolated NCU protocol evidence.

Current interpretation:

quantized GEMM vs dequantize+matmul has a shape-dependent tradeoff; a fixed runtime threshold is an implementation policy, not a universal quantization speedup law.

Status:

`HIGH_VALUE_RESEARCH_CANDIDATE / SIDE_LANE_FROZEN`

Future continuation requires explicit approval.

## Candidate C — MoE/AWQ mechanism work

Not yet authorized.

Examples:

- router modification;
- expert scheduling mechanism;
- grouped-GEMM optimization;
- custom quantized kernel;
- hardware-aware routing;
- architecture support.

Status:

`NOT_AUTHORIZED`

## Mainline relationship

Candidate results may later serve as:

- workload-class evidence;
- representative target-selection evidence;
- a separate paper direction;
- future mechanism motivation.

They do not redefine the AWMA mainline until explicitly promoted by scientific review.
