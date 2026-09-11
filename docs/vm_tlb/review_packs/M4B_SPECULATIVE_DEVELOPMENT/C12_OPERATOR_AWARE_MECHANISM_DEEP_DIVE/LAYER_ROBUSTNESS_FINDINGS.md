# Layer robustness findings

Only `DIRECT_PARAMETER_RANGE` kernels whose parameter names directly provide
layer 0–15 are included. Attention Core, Other Compute, and the terminal
Embedding/Output kernels are not given inferred layer ids.

## Broad direct-layer response

- Prefill F7-L5: all 16 direct FFN, Attention Projection, and Norm layers
  improve. Median deltas are -170,804.5, -36,740, and -9,404.5 cycles.
- Prefill F7-L10: all 16 FFN and Norm layers improve; Attention Projection has
  15 improve and one regress. At F7-L20, all 16 layers in all three classes
  regress.
- Decode1 F7-L5 and F7-L10: all 16 direct FFN, Attention Projection, and Norm
  layers improve. At F7-L20, all 16 FFN and Attention Projection layers
  regress, while all 16 Norm layers continue to improve.
- F8 reproduces the same layer-sign patterns as F7 in Decode because their
  same-Lseg kernel cycles are identical. Prefill F8 differs only modestly in
  layer magnitudes, not in the broad L5-versus-L20 phase reversal.

No reported direct-layer summary meets the predeclared 35% single-layer
absolute-share outlier signal: the largest share is 11.5% and Top-4 shares are
at most 42.7%. Therefore the FFN and Attention Projection Segment conclusions
are robust across the 16 directly attributable layers rather than artifacts of
a few layers. This conclusion does not extend to Embedding/Output, whose
important terminal kernel has no direct 0–15 layer id.

`LAYER_OPERATOR_SUMMARY.tsv` provides F0 cycles, trace-derived Weight refs and
unique pages, exact translation totals, Segment activity, and F7/F8 deltas.
`LAYER_ROBUSTNESS.tsv` gives the full improve/regress/tie, median/P25/P75,
range, concentration, and outlier diagnostics.
