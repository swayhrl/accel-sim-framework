# ChatGPT Scientific Review — Q30 MoE Routing-Skew Characterization V1

Date: 2026-09-20

Reviewed execution branch:

`hrl/awma-109-moe-routing-skew-20h-v1`

Reviewed final HEAD:

`ed645f3aec0fe4623e1895dee2754ece0ab063f1`

## 1. Acceptance

Stage accepted as:

`AWMA_109_MOE_ROUTING_SKEW_CHARACTERIZATION_20H_V1_ACCEPTED_WITH_SCOPE`

Accepted controls:

- exact Q30 S2/T2048 expert harness;
- natural histogram: 93 active experts, M=2048, top-k=8, 16,384 assignments;
- natural CV = 1.8867, p95=793, max=1602;
- five histogram-preserving P controls with bitwise inverse-equivalence;
- five U-active order controls under the same balanced histogram;
- beta={0.25,0.50,0.75} fixed-active-set deterministic skew controls;
- controlled expert-shape microbenchmark;
- S0/T128 independent holdout;
- bounded E1/NCU evidence.

Synthetic routing remains diagnostic only.

## 2. Main S2/T2048 trend

The skew continuum produces the following exact active-count CV values:

```text
natural    CV = 1.8867
beta=0.25  CV = 1.4154
beta=0.50  CV = 0.9437
beta=0.75  CV = 0.4722
balanced   CV ~= 0
```

Across the three recorded order/control realizations per beta, median-of-medians expert-region timing is approximately:

```text
natural    14.309 ms
beta=0.25  13.313 ms
beta=0.50  12.827 ms
beta=0.75  12.566 ms
balanced   12.077 ms
```

Descriptive reductions versus the natural median are about:

- beta=0.25: 7.0%
- beta=0.50: 10.4%
- beta=0.75: 12.2%
- balanced endpoint: 15.6%

The CV/time relation is strongly monotonic in this experiment.

Do not promote this to a general causal law yet.

## 3. Order/layout effect is non-negligible

The histogram-preserving P controls span roughly:

`13.714–14.397 ms`

with a median around:

`13.862 ms`

while the matched natural controls have a median around:

`14.309 ms`.

Therefore token/order/layout effects are at the several-percent scale.

The skew effect is larger, but histogram and assignment-graph/layout effects still need stronger separation.

## 4. S0/T128 does not reproduce the S2 benefit

Accepted S0/T128 holdout:

```text
N         10.612 ms
P         10.637 ms
U-active  10.950 ms
```

Balanced routing is slightly slower at this much smaller token population.

Therefore the performance effect is explicitly:

`TOKEN_POPULATION_AND_EXPERT_GRANULARITY_DEPENDENT`

This is an important boundary condition.

## 5. Expert-shape curve

Controlled expert-0 module medians:

```text
M=1       0.0433 ms
M=4       0.0458 ms
M=14      0.0431 ms
M=205     0.0553 ms
M=793     0.1331 ms
M=1602    0.2119 ms
```

Large expert batches have much lower time/token than tiny expert batches.

This observation alone does NOT explain why balancing the histogram speeds up the full expert region.

It implies that the next causal decomposition must separately measure:

- token grouping/index extraction;
- gather;
- expert MLP compute;
- routing-weight application;
- scatter/index_add/combine;
- per-expert execution contribution;
- residual framework/launch overhead.

## 6. Remaining confound: degree realization

Each beta target histogram is exact, but a deterministic routing graph realizes those column degrees.

A single degree realization can correlate histogram skew with:

- which token values are sent to which expert;
- gather/scatter index structure;
- token-position locality;
- expert-mask realization.

Row permutations alone do not fully eliminate this possibility.

The next stage must use multiple independently seeded exact degree realizations for each fixed beta histogram.

## 7. Timing protocol

The next stage should use randomized/interleaved condition order rather than long condition-by-condition blocks.

Purpose:

- reduce clock/thermal/drift confounding;
- separate first-use effects;
- produce paired within-block contrasts.

Native timing must remain CUDA-event based and uninstrumented.

## 8. Implementation-scope boundary

The accepted exact Q30 harness follows the frozen model implementation.

Before any architecture mechanism claim, determine whether the observed skew sensitivity is:

- intrinsic to expert GEMM/granularity; or
- strongly specific to the eager expert-loop/grouping implementation.

The next stage should audit whether an already-installed semantics-preserving grouped-MoE/grouped-GEMM backend exists.

No new package installation is authorized.

If none exists, record:

`NO_EXISTING_GROUPED_BACKEND_HOLDOUT`

rather than implementing a new optimized backend in this characterization stage.

## 9. Decision

Do NOT enter architecture mechanism design yet.

Next stage:

`AWMA_109_MOE_CAUSAL_CLOSURE_AND_SCALE_PHASE_DIAGRAM_20H_V1`

Required closure:

1. independent degree realizations at fixed histogram;
2. randomized/interleaved timing;
3. M={128,256,512,1024,2048} scale phase diagram;
4. component/per-expert timing decomposition;
5. bounded implementation-backend scope audit;
6. deterministic cross-layer holdout if authority can be produced without changing runtime;
7. preserve S0 as independent natural small-M boundary.

After that stage, decide whether the mechanism opportunity is primarily:

- routing modification;
- semantic-preserving expert scheduling;
- grouped-GEMM/kernel selection;
- gather/scatter/indexing;
- or no robust mechanism opportunity.
