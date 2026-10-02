# R24 tied-weight gradient lifetime native review

Date: 2026-10-02.

Execution:
`41795817a5b86959c86cc36c6973f292be33c6a6`

Tree reported by execution:
`a9c7e256ff7b82d91f5dc24077b76feb537186dc`

Stage:
`AWMA_R24_TIED_WEIGHT_GRADIENT_LIFETIME_NATIVE_109_V1`

## Review conclusion

The empirical result is accepted with one decision-contract caveat.

Accepted empirical facts:
- exact Qwen2.5-0.5B tied input-embedding/lm_head storage identity passed;
- exact frozen TRAIN_DISCOVERY_256 input authority passed;
- B0/S1/S2 numerical qualification passed under the frozen rtol=atol=1e-2 contract;
- formal S2 never materialized a full VxH gradient/shadow;
- S2 reduced target peak allocated memory from 4,535,017,472 B (B0) and 4,558,633,984 B (S1) to 3,724,405,760 B;
- S2 therefore reduced measured target peak allocated memory by 773.06 MiB vs B0 and 795.58 MiB vs S1;
- S1 shortened the full-gradient lifetime but retained full materialization and was stably slower than B0/S2 in all three groups;
- S2 vs S1 was a stable timing benefit in all three groups;
- S2 vs B0 was mixed: G0 stable 0.60% regression, G1 stable 0.97% benefit, G2 stable 1.02% benefit;
- no NCU/NVBit/SASS/Accel-Sim/hardware work occurred.

The core scientific interpretation is therefore:

> On this one frozen real-token tied-weight target-family microstep, bounded row-tiled delayed classifier-gradient generation plus compact lookup-gradient handling eliminates the formal full dense tied-gradient materialization and produces a large measured peak-memory reduction, while TARGET_REGION time is strongly better than the simple late-full-gradient arm and mixed/near-neutral versus the strong B0 arm.

This is a scoped software/dataflow result. It is not a full-training speedup, convergence result, multi-shape/model generalization, or hardware residual.

## Decision-contract caveat

The original frozen Goal contains an internal gap.

Section 10A says `R24_TILED_DELAYED_UPDATE_NET_RESPONSE_PRESENT` requires that S2 have "no stable TARGET_REGION regression versus B0 or S1", while Section 10C defines `R24_CAPACITY_TIME_TRADEOFF` only when S2 has stable regression versus B0 or S1 in at least two groups.

The observed result has exactly one stable B0 regression group and two stable B0 benefit groups. Therefore:
- it does not satisfy a literal zero-regression reading of Section 10A;
- it does not satisfy Section 10C's two-regression-group condition;
- B/S1 and D also do not match the observed result.

The executed runner initially labeled this case `R24_CAPACITY_TIME_TRADEOFF`. After formal data were frozen, a CPU-only finalizer changed only the decision classifier and emitted `R24_TILED_DELAYED_UPDATE_NET_RESPONSE_PRESENT`, explicitly using the two-group regression rule. Formal timing/memory data were not changed and no GPU rerun occurred.

Code comparison confirms the post-formal source change only adds stable-benefit counting and changes the terminal decision branch; the measured execution path is unchanged.

Accordingly:
- preserve the execution pack's final label as its post-formal interpretation;
- do not present that label as an unambiguous preregistered PASS;
- for research decisions, lead with the empirical description above: **large causal capacity benefit, S2>S1 stable, S2 vs B0 mixed/near-neutral**.

No GPU rerun is needed to establish these empirical facts.

## Numerical scope

The frozen rtol=atol=1e-2 qualification was obeyed. S1/S2 total-gradient max absolute error was 0.0078125; next-forward loss differences were also within the frozen bound.

This is one-step numerical qualification only. It does not establish multi-step optimizer trajectory equivalence or training convergence.

## Strong-baseline boundary

B0 retained the accepted CCE first-store zero-init-removal path. Thus the R24 capacity response is not created by reverting the previously accepted CCE software optimization.

However, the next broader software validation should consider a stronger one-full-buffer comparator: compact lookup-row accumulation merged into one full classifier/total gradient, rather than the current S1 normal dense lookup-gradient path. That comparator could reduce one dense contribution buffer without adopting S2's fully tiled update. This is a future design consideration, not a reinterpretation of R24.

## Current disposition

- R24 execution: COMPLETE / STOP.
- Preserve R24 as a scoped software/dataflow capacity result with mixed-vs-B0 timing.
- Do not authorize hardware/PPA/Accel-Sim.
- Do not claim full-model training speedup or convergence.
- Any broader validation must be separately designed, with frozen independent model/shape/input roles and a stronger production-quality software comparator.
