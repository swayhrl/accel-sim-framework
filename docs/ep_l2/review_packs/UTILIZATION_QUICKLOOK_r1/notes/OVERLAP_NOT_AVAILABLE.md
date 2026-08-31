# Overlap audit — not available from this frozen output family

The frozen B0 CSVs contain per-slice occupancy summaries and the scalar
`overlap_detected` interval-attribution flag.  The WBUF=8 blocking CSV contains
exclusive primary blocker counts.  Neither artifact records a timestamped joint
blocker state, a blocker-bitmask histogram, or pairwise joint counts at the same
eligible demand-miss admission event.  Therefore a simultaneous-overlap matrix
(for example, SET_ASSOC + MSHR_META) cannot be derived without inventing data.

No overlap heatmap is published in this quicklook.

Minimum telemetry required for a future overlap figure: at every eligible
frontend demand-miss admission event, record the complete blocker bitmask before
exclusive-primary tie-breaking, plus the event denominator and the same
Core/Framework/config/trace provenance as the primary-blocker table.  Aggregated
pair and full-mask counters would then permit a valid overlap analysis.
