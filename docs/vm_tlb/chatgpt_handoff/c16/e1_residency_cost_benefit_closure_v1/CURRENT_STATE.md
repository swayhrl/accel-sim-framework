# C16 E1 Residency Cost/Benefit Closure — Current State V1

## Accepted upstream

Coverage producer:
`hrl/c16-e1-coverage-scaling-109-v1@18acd7dcc10118c68b450d226a8e7ca80c51ad72`

Coverage independent consumer / operator-family prep:
`hrl/c16-e1-operator-family-expansion-consumer-174new-v1@eb4e737e24c27d1908a2fdf43f465ed5e0cfc66f`

Operator-family producer:
`hrl/c16-e1-operator-family-expansion-109-v1@eae1cc4d831ae8459da558cf1358bb8daf8d76e6`

## Frozen upstream labels

- shared stage:
  `SHARED_RESIDENCY_LOCAL_ONLY`
- coverage stage:
  `COVERAGE_SCALING_POSITIVE_BUT_SUBTHRESHOLD`
- operator-family producer stage:
  `OPERATOR_FAMILY_NOT_SUPPORTED`

No upstream label is overwritten by this stage.

## Operator-family producer preliminary audit

No node109 rerun is requested.

The producer evidence is internally consistent with:

- natural FFN order:
  `gate_proj -> up_proj -> down_proj`;
- all 14 preregistered CONTROL/FAIR conditions executed;
- UP28 is the only role-only family with broad local benefit;
- GATE28 and DOWN28 do not show material selected-family benefit;
- pairwise inclusion of gate/down does not improve realization;
- GUD84 preserves broad up_proj local benefit but not gate/down benefit;
- no condition has a positive whole-decode effect beyond dispersion.

Representative medians:

### UP28
- direct up saving: ~0.562 ms
- gate+down measured change: ~-0.200 ms
- outside-FFN residual: ~-0.364 ms
- whole-decode saving: slightly negative

### GUD84
- direct measured FFN saving: ~0.464 ms
- gate: ~-0.009 ms
- up: ~+0.483 ms
- down: ~-0.016 ms
- outside-FFN residual: ~-0.436 ms
- whole-decode saving: ~0.009 ms
- material selected modules: 28/84, i.e. the up_proj family

The negative residual remains an accounting observation only.
It is not yet proven to be cache collateral slowdown.

## Why one final real-hardware diagnostic is justified

The current evidence does **not** support protecting gate/down qweights.

It does support a repeatable up_proj-local benefit.

The system-level question is now narrower:

> Can the up_proj residency benefit be made system-positive by choosing a smaller global persistence budget, and where does the offsetting ~0.36-0.44 ms go?

This is more informative than immediately implementing a simulator mechanism.

The next stage therefore:

1. keeps protection limited to all 28 up_proj;
2. sweeps the **global** persistence budget;
3. times non-overlapping top-level model components as well as all FFN projections;
4. localizes the negative residual;
5. profiles representative up_proj and self-attention points.

No simulator is run.

## Simulator authority remains frozen but inactive

If later authorized:

- Core:
  `swayhrl/gpgpu-sim@57bb71ecd015b6ec0ab32e45b0815e5beaf69172`
- Platform:
  `RTX4080_ADA_ACCELSIM_BASE_V1`
- Config SHA:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`

No RTX3080/SM86 configuration is authorized.


---

## Cost/benefit producer completed

Producer:

`hrl/c16-e1-residency-cost-benefit-closure-109-v1@86ef7dcfb49241bd87ff4a8d59b4d950d53de0a5`

Producer stage label:

`RESIDENCY_OFFSET_LOCALIZED`

Preliminary ChatGPT audit finds no node109 rerun required.

Read before 174 raw consumption:

`docs/vm_tlb/chatgpt_handoff/c16/e1_residency_cost_benefit_closure_v1/PRODUCER_PRE_RESUME_AUDIT.md`

Key producer result pending independent consumer closure:

- all four tested budgets retain all-28 up_proj local benefit;
- no budget produces a whole-decode positive effect beyond dispersion;
- top-level decomposition closes the former residual;
- full-budget offset is dominated by aggregate self-attention slowdown, with additional gate/down cost;
- representative L0 self-attention NCU does not reproduce the aggregate slowdown, so no unique kernel/cache-cause claim is authorized.

The next project-level decision is deferred until independent 174 closure.
