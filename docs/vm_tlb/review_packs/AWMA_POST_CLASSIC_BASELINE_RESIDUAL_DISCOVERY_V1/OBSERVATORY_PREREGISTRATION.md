# Strong-reference Observatory preregistration

Recorded after the fixed 0/80 causal diagnostic established a material but
non-monotonic L1-hit-latency response, and before any strong-reference
Observatory result was generated.

## Purpose

Provide the complementary accepted Bottleneck Observatory Level-1 view on the
same four preregistered targets. This is a behavior-neutral observer replay,
not a new baseline, mechanism, or performance sample.

Targets and accepted WARP-reference signatures:

| target | expected cycles | expected instructions | expected CTAs |
|---|---:|---:|---:|
| T0 | 488559 | 368696302 | 224 |
| T1 | 619514 | 369131520 | 384 |
| T2 | 94034 | 43357696 | 1216 |
| A2 | 115700 | 34883072 | 224 |

The binary, source, grouping, config, 10/80 timing, trace, and all service
semantics remain the accepted Lane-B reference. The only additional setting is
`GPGPUSIM_AWMA_BOTTLENECK_OBSERVATORY=1`.

## Neutrality gate

Every run must exactly match the accepted cycles/instructions/CTAs and physical
L1/L2/MSHR/PTW/PTE counts, plus all logical coverage and quiescence gates. A
mismatch invalidates the observational run and blocks its use.

## Interpretation

Level-1 aggregates/windows may distinguish translation-not-ready exposure from
cache/interconnect/DRAM/scheduler hiding. They are not additive cycle
decompositions. Level 2 is not run unless Level 1 plus the already completed
0/80 contrast cannot locate the material residual.

These four replays consume the remaining Phase-C budget: total new full-kernel
diagnostic/observer replays will be eight of eight.
