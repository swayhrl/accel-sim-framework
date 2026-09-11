# Kernel criticality / Pareto findings

`KERNEL_DELTA_RANKING.tsv` contains every nonzero exact per-kernel cycle delta,
ranked independently as improvement, regression, and absolute contribution.
`KERNEL_DELTA_PARETO.tsv` gives the cumulative Top-10/20/50 shares and the
kernel counts needed for 50/80/90% of each contribution magnitude.

## Measured distribution

| ROI | comparison | changed kernels | Top-10 absolute share | kernels to 50/80/90% | distribution |
| --- | --- | ---: | ---: | --- | --- |
| Prefill | F1 vs F2 | 583/692 | 71.6% | 1 / 50 / 151 | one dominant hotspot plus broad tail |
| Prefill | F5 vs F0 | 617/692 | 78.0% | 1 / 20 / 107 | one dominant hotspot plus broad tail |
| Prefill | F7-L5 vs F0 | 630/692 | 32.6% | 22 / 53 / 88 | distributed |
| Prefill | F7-L10 vs F0 | 629/692 | 77.5% | 1 / 23 / 107 | one dominant hotspot plus broad tail |
| Prefill | F7-L20 vs F0 | 689/692 | 40.4% | 19 / 46 / 72 | moderately concentrated, not single-kernel |
| Prefill | F8-L5/L10/L20 vs F7 | 631/579/581 | 43.6% / 13.5% / 12.9% | 13/69/72 to 50% | L10/L20 broadly distributed |
| Decode1 | F7-L5 vs F0 | 567/740 | 19.0% | 31 / 53 / 98 | distributed |
| Decode1 | F7-L20 vs F0 | 587/740 | 47.0% | 13 / 40 / 49 | moderately concentrated |
| Decode1 | each F8-Lx vs F7-Lx | 0/740 | 0% | N/A | exact all-kernel identity |

The prefill hotspot is compute index 691, a direct Embedding/Output final GEMM
with no direct layer id: it contributes +483,963 cycles in F1-vs-F2,
+700,253 in F5-vs-F0, +1,105,365 at F7-L10-vs-F0, and +4,158,904 at
F7-L20-vs-F0. It is therefore a critical measured hotspot for those specific
comparisons, not evidence that all Embedding/Output computation has the same
mechanism.

## Operator and layer interpretation

- FFN and Attention Projection are not single-hot-kernel phenomena in the
  direct-layer view. At Prefill F7-L5 and Decode1 F7-L5, all 16 direct FFN and
  all 16 direct Attention Projection layers improve. At F7-L20, all 16 layers
  in both classes regress. The largest single-layer absolute shares are below
  11.5%, and Top-4 shares are at most 42.7%; see `LAYER_ROBUSTNESS.tsv`.
- Thus, FFN/Attention Projection latency sensitivity is broadly repeated across
  the directly attributable Transformer layers, while the prefill
  Embedding/Output class has a separate final-GEMM hotspot in several
  comparisons.
- A Pareto concentration is a location of measured cycle change, not a causal
  assignment to TLB, PTW, cache, or memory behavior. The latter observables are
  retained per kernel in the ranking TSV for hypothesis generation only.
