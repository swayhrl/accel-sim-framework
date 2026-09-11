# Segment empirical break-even findings

Only Lseg=5/10/20 measurements are used. Reported crossings linearly
interpolate between the adjacent observed points that bracket F0 and are
therefore `EMPIRICAL_INTERPOLATION_ONLY`; no setting outside 5–20 is
predicted.

## Full-ROI bracket

| ROI | family | delta @5 | delta @10 | delta @20 | bracketed break-even Lseg |
| --- | --- | ---: | ---: | ---: | ---: |
| Prefill | F7 | -2,656,019 | +880,650 | +13,640,954 | 8.755 |
| Prefill | F8 | -2,672,883 | +885,265 | +13,654,039 | 8.756 |
| Decode1 | F7 | -605,597 | -132,567 | +1,471,105 | 10.827 |
| Decode1 | F8 | -605,597 | -132,567 | +1,471,105 | 10.827 |

Within the measured setting range, positive full-ROI Segment benefit is only
observed below roughly Lseg 8.75 in Prefill and below roughly Lseg 10.83 in
Decode1. This is an empirical range target for a future controlled replay,
not a general hardware latency law.

## Direct operator brackets

- Prefill FFN crosses near 10.12 (F7) / 10.12 (F8), Attention Projection near
  10.42 / 10.46, and Norm near 10.52 / 10.56. All three improve at 5 and 10
  but regress at 20.
- Prefill Embedding/Output regresses at all observed points for F7 and F8; no
  positive break-even exists in the measured range.
- Decode1 FFN crosses near 10.38, Attention Projection near 14.81, and
  Embedding/Output near 10.74. Decode Norm improves at all three observed
  points, so a crossing is not determined in range.

These operator crossings localize exact class-cycle deltas. They do not prove
that each class experiences a separate physical lookup-latency threshold.
`SEGMENT_LATENCY_SENSITIVITY.tsv` retains finite differences and exact Segment
activity; `SEGMENT_BREAK_EVEN.tsv` contains every determined and undetermined
case.
