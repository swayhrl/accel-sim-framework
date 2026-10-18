# Frozen before new performance

Let a=K0_32x4, b=K0_64x8, c=K1_32x4, d=K1_64x8 whole-run core cycles. All refer to new strict-accepted runs on one exact binary/observer/input contract; historical controls are calibration references only.

| Quantity | Formula | Unit/direction |
| --- | --- | --- |
| K main effect | ((c−a)+(d−b))/2 | cycles; negative means fewer cycles underK1 |
| Tag main effect | ((b−a)+(d−c))/2 | cycles; negative means fewer cycles with64×8 |
| additive interaction Δ | (d−b)−(c−a)=a+d−b−c | cycles; complete difference-of-differences, no extra factor2 |
| Q32 | c/a | K1/K0 cycle quotient at32×4; >1 means slowerK1 |
| Q64 | d/b | K1/K0 cycle quotient at64×8; >1 means slowerK1 |
| T0 | b/a | large/small Tag atK0 |
| T1 | d/c | large/small Tag atK1 |
| multiplicative interaction I | Q64/Q32=T1/T0=ad/(bc) | >1 means larger relativeK1 cycle penalty with largeTag |
| log(I) | ln(a)+ln(d)−ln(b)−ln(c) | natural log, dimensionless |
| K speed ratios | a/c and b/d | >1 means fasterK1; explicitly reciprocal ofQ |
| K cycle changes | 100×(c/a−1),100×(d/b−1) | percent; positive means more cycles |

Retain integer numerators/denominators; compute from unrounded values, display rounding never enters strict verdicts. Missing/unaccepted/incomparable required points make comparisons UNAVAILABLE, not0. A zero denominator is UNDEFINED_ZERO_DENOMINATOR; nonpositive cycles invalidate performance observations. No imputation, replacement cells, best-Tag selection, repetitions or significance claims.

Typed comparable counts and conditional service means can be displayed with analogous descriptive differences, retaining their own units and denominator populations. Map-loss completed-interval sums/counts exclude censored allocations and may change population underK1. Post-ready sum/retired can rise while whole-run cycles fall; both signs must be retained. These are not additive whole-GPU causal contributions.

Interpret only source-request invalidation-policy×Tag interaction. Neither c−a norΔ identifies a precise cross-kernel retained-reuse contribution. W per-address/same-SM/line+generation reuse remains UNAVAILABLE. Actual sourceE or mapping-change0 is retained as a negative or unexposed model result; no change to source predicates may be made to force an effect.
