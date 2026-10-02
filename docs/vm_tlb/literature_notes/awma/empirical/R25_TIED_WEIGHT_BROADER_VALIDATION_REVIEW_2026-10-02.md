# R25 tied-weight broader software validation review

Date: 2026-10-02.

Execution:
`2581b6592e79691c4c3e57fe31a339eba9f6b7dd`

Reported execution tree:
`5d1df1251b45f2030e37c136c1534c72897ae7f4`

Stage:
`AWMA_R25_TIED_WEIGHT_BROADER_SOFTWARE_VALIDATION_109_V1`

## Accepted conclusion

Accept:
`R25_TILED_CAPACITY_TIME_TRADEOFF`.

The result closes the R25 frozen decision table without a post-formal classifier change.

### Authority / holdout

D0 is the R24 Qwen discovery point.

H0 uses:
- `meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`;
- the pre-existing future-use authority `ADOPTED_LLAMA_S0_T128_V1`, created 2026-09-14;
- no R25-time re-tokenization or performance-selected replacement.

The old historical S0 binding remained unrecovered; the adopted future-use authority does not rewrite that history. This does not invalidate R25 holdout use because the adopted token authority predates R25 and was frozen before R25 performance.

Implementation freeze records that H0 performance was not inspected before freeze.

### Strong comparator identity

C1 is a materially stronger comparator than R24 S1:
- compact sorted unique lookup rows;
- no dense lookup W.grad;
- one complete classifier/total VxH gradient only;
- same AdamW consumer.

S2:
- same compact lookup path;
- no complete VxH gradient;
- deterministic 32 MiB FP32 gradient-tile budget.

Source inspection confirms these identities.

### Numerical qualification

Both D0 and H0 pass:
- one-step qualification;
- four consecutive same-batch optimizer/dataflow trajectory qualification;
- frozen rtol=atol=1e-2;
- W/m/v/step/next-loss checks.

This remains a short trajectory check, not convergence evidence.

### Capacity

S2 vs C1:
- D0: -535.777 MiB target peak allocated, -19.220%;
- H0: -1350.030 MiB, -22.944%.

Both points satisfy the preregistered causal-capacity criteria and every formal S2 sample lies below the corresponding C1 group median.

The capacity result therefore survives:
1. removal of the obvious dense-lookup buffer from the comparator; and
2. an independent Llama model/input lineage.

### Timing

Primary S2 vs C1 TARGET_REGION:

D0:
- C1 median 25.9072 ms;
- S2 median 25.6655 ms;
- ~0.933% lower time;
- 3/3 stable-benefit groups;
- point class BENEFIT.

H0:
- C1 median 38.7123 ms;
- S2 median 38.7625 ms;
- ~0.130% higher time;
- 3/3 stable-regression groups under the frozen 3x-MAD classifier;
- point class REGRESSION.

Independent recomputation from all 90 formal samples matches all six S2-vs-C1 group directions.

Important interpretation:
the H0 regression is directionally stable under the engineering classifier but very small in magnitude (~0.05 ms, 0.13%). Therefore the correct conclusion is not "S2 is materially slow on Llama"; it is "S2 does not establish a cross-model non-regression/speed benefit relative to the stronger C1 comparator."

C1 itself is strong:
- it lowers peak memory vs B0 on both points;
- it is a timing BENEFIT vs B0 on both points.

S2 also remains faster than B0 on both points; the R25 tradeoff arises only against the stronger C1 production comparator.

## Research interpretation

R25 establishes a reusable software/dataflow result:

> Compact lookup-gradient handling is broadly useful, while removing the final full tied-weight gradient via tiled late generation provides a large additional capacity reduction. That extra capacity benefit generalizes across Qwen and Llama, but its timing effect is implementation/shape dependent rather than uniformly favorable.

This supports two software modes:
- C1-like one-full-buffer path as a strong general software baseline / speed-oriented path;
- S2-like tiled path as a capacity-oriented opt-in path when memory headroom is valuable.

Do not tune S2 on H0 to erase the 0.13% regression: H0 is the independent holdout and has already served its purpose.

## Claim limits

No:
- full-training throughput;
- all-parameter training;
- convergence;
- universal LLM claim;
- hardware residual;
- PPA/Accel-Sim.

No additional R25 tile/model/input sweep is justified from this result.

## Next decision boundary

The next useful step is not another microbenchmark sweep.

If continuing, move toward production-integration validation:
1. integrate compact lookup handling plus the two memory policies behind opt-in software controls;
2. demonstrate that the capacity mode changes an actual memory-feasibility boundary or batch/context headroom in a realistic training configuration;
3. keep C1 as the speed-oriented comparator;
4. retain S2 only if the extra capacity is actually useful under realistic memory pressure;
5. run a limited multi-step training-quality check before making optimizer/training claims.

That is a separate future authorization, not launched by this review.
