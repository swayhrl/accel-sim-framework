# AWMA Q05 Contextual Lookup-Path Decomposition 174-new V1

Status: `AWMA_Q05_CONTEXTUAL_LOOKUP_PATH_DECOMPOSITION_174NEW_V1_COMPLETE_WITH_SCOPE`

Same-trace comparison uses formal isolated member34 (864552 cycles), not the older standalone capture. P34 natural is 871835 cycles despite 240→15 walk reduction from formal isolated, so real predecessor history removes cold walk activity without automatically improving net cycles.

## P34 target-only lookup matrix

| L1/L2 latency | Q05 cycles | Delta vs R0 |
|---|---:|---:|
| 10/80 | 871835 | 0 |
| 5/80 | 778598 | -93237 |
| 2/80 | 771796 | -100039 |
| 0/80 | 748102 | -123733 |
| 10/40 | 904750 | +32915 |
| 10/0 | 878836 | +7001 |
| 0/0 | 657110 | -214725 |
| Target I0 | 674121 | -197714 |

Target L1 lookup shortening has a strong positive modeled sensitivity. L2-only shortening is non-monotonic and changes L2 miss counts, so it is not an additive latency subtraction. P34 zero/zero is 17011 cycles below I0; no positive residual >3% remains, so force-L1-hit was not run.

P8 has the same directional L1 sensitivity (835145→737845 at 5/80; →672014 at 0/80; →661123 at 0/0). P8 is therefore supported as screening-only; P34 remains the final realism reference.

No architecture mechanism is designed or evaluated. STOP after this diagnostic stage.
