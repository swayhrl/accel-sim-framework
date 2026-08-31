# Source and parser delta

The implementation adds the default-OFF `EPL2SRV1` observation family. `EPL2MOTV1` semantics and its output fields are unchanged.

| Area | Change |
| --- | --- |
| Core `src/gpgpu-sim/cache.cc` / cache configuration | `-gpgpu_ep_l2_sector_reuse_stats` default `0`; per-slice sector tracker and `EPL2SRV1` emission only when enabled. |
| Core demand observation path | Batch-prestate classification keyed by `(slice, 128-B line, 32-B sector)`, with exact last-touch stack (depth 4096) and epoch reset. Writebacks are excluded. |
| Framework `tests/ep_l2/streaming_reuse_{off,on}.config` | Explicit default-OFF and enabled configurations. |
| Framework `util/ep_l2/run_streaming_reuse.py` | Campaign lifecycle, provenance capture, OFF/ON comparisons, and stable result roots. |
| Framework `util/ep_l2/parse_epl2_sector_reuse.py` | Strict `EPL2SRV1` parser; final cumulative per-slice snapshot selection, monotonicity checks, closure validation, and manifest fields for superseded snapshots. |
| Framework `util/ep_l2/aggregate_streaming_reuse.py` | Completed-row aggregate CSV/PNG/SVG generation; no synthetic scan row. |

Semantic rule: a first touch to a different 32-B sector within an already-seen 128-B line is `spatial_new_sector`, not temporal reuse. Only a repeat of the identical sector identity is `temporal_sector_reuse`.

