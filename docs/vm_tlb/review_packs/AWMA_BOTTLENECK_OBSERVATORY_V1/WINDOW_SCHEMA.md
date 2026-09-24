# Window schema

Level 2 and Level 3 maintain online windows of 32, 128, and 512 true simulator
cycles.  No completed-window stream or per-cycle vector is retained by Level 2.

For every metric and width the observer keeps:

- exact number and sum of completed windows;
- exact maximum;
- deterministic bounded reservoir (4096 values) for p50/p95/p99;
- exact Top-8 windows with `[start_cycle,end_cycle]` and value.

Event values are summed.  Gauge values are sample-averaged.  Empty metric windows
contribute zero, so quantiles describe the entire kernel timeline rather than
only active periods.  The final partial window is included using the same fixed
cycle-zero alignment.

Different domain records can be joined offline by width and overlapping cycle
interval.  No source-order, UID-order, or trace-file-order surrogate is accepted
as a cycle axis.

`end_cycle` is the nominal inclusive end of the fixed aligned window.  For the
final partial window it may exceed `awma_observatory_final_cycle`; offline joins
must clamp that one interval to the reported final cycle.

Level 3 separately permits two explicitly deep structures: exact progress by
cycle and a live READY UID map.  The READY entry is erased at successful
admission, so its size is bounded by resident ready-but-not-admitted work rather
than total kernel accesses.
