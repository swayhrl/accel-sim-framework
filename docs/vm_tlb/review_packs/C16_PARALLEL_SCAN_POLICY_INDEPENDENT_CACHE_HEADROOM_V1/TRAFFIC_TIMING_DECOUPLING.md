# Cache traffic and timing decoupling

PASCAL v1 separates cache traffic from timing. Its Theorem 6 makes cache-mediated catch-up conditional on pipeline depth, wait/consume costs, latency bounds and sustained service imbalance; the paper's depth-4 example changes traffic from about 1.00 to 5.58 fill-equivalents while normalized time stays about 424-425 ns.

The C16 evidence shows both directions:

1. **Traffic and timing co-move in uncontrolled ROW split1.** GROUP_FULL_M reduces the finite fill-equivalent count from 8.908422 to 1.0 at K3072 and from 9.030064 to 1.0 at K4096; median timing improves by 27.631% and 33.073%. Cache traffic is exposed on this path, but the matched classical mapping already captures it.
2. **Timing changes without a TEX read-side miss gap in the residual M sweep.** Split1 and split8 both report hit fraction 1.0 for M1/M16/M32/M64, yet their timing ordering changes with CTA supply and reduction cost. That gap is scheduling/parallel decomposition, not replacement-policy traffic.
3. **Split8 ROW/GROUP is already close to one unique weight fill.** Mapping changes timing only 1.407%/2.564% at K3072/K4096 and does not reduce L2 miss sectors. Replacement headroom is small at these points.

No C16 artifact binds PASCAL's pipeline parameters `(d, alpha, beta, lambda_hit, lambda_miss)` or historical `sigma_E`; `G_d` and the catch-up certificate remain UNKNOWN rather than being fitted post hoc.
