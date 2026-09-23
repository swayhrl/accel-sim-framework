# C16 E1 Shared-Residency Mechanism Feasibility — Current State V1

## Accepted upstream closure

Producer:
`hrl/c16-e1-l2-persistence-intervention-109-v1@4c0e6b998528e425578cacf5912bbcc4ff3bfaf6`

Independent consumer:
`hrl/c16-e1-l2-persistence-intervention-consumer-174new-v1@1dcab9c8d932973399c5811dc817802bfb3b9dfe`

Raw evidence match:
`PASS`

## Frozen decision divergence

Both states remain valid within their own preregistered rules:

- producer scoped:
  `MECHANISM_REQUIREMENTS_READY_FOR_DESIGN_REVIEW`
- strict consumer:
  `TARGETED_PERSISTENCE_MECHANISM_PRECONDITION_NOT_SUPPORTED`

Divergence:
`METHODOLOGICAL_OPERATIONALIZATION`

Reason:
- all primary natural points show large material, target-specific timing benefit;
- no primary point passes the strict >=20% and >=4MiB DRAM gate.

This divergence is not a raw-data contradiction.

## Accepted persistence evidence

CUDA policy capability:
- L2: 67,108,864 B
- max persisting set-aside: 46,137,344 B
- max access-policy window: 134,213,632 B
- qweight region: 33,947,648 B, contiguous

Isolated positive control:
- timing benefit: ~35.9%
- DRAM reduction: ~61.5%

Natural target timing benefit vs SETASIDE_ONLY:
- L0 up D1: ~48.75%
- L0 up D3: ~46.84%
- L14 up D3: ~49.37%
- L0 down D3: ~19.36%

Natural DRAM:
- improves in several points but does not satisfy the frozen material gate;
- matched unrelated persistence can reduce DRAM as much or more;
- therefore traffic is not target-specific.

Budget:
- 8 MiB: no material timing benefit
- 16 MiB: first tested material timing budget
- 24/32/full: material timing benefit
- no tested budget passes DRAM materiality
- no exact threshold claim.

## Important whole-decode observation

Existing full-model decode-step timing shows:
- SETASIDE_ONLY itself improves stable D1-D3 decode by roughly 3% vs BASELINE;
- persisting one individual target qweight does not materially improve whole decode-step latency relative to SETASIDE_ONLY, even though the selected target module itself becomes much faster.

Therefore the next architectural question is not simply whether one qweight can be protected.

It is:

> Can a fixed total persisting budget be shared across multiple selected compressed-weight regions so that several target modules retain local timing benefits simultaneously and produce a measurable whole-decode benefit?

A second open question is:

> Why is target timing strongly target-specific while aggregate target DRAM bytes are not?

The next stage combines:
1. critical-path metric diagnosis;
2. rotating/shared persistence under one fixed budget;
3. mechanism design review and simulator mapping.

No full mechanism implementation is authorized in this stage.
