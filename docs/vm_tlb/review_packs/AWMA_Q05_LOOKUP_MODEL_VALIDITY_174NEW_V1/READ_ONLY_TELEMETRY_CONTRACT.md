# Read-only telemetry

`peek()` checks valid/key only. It does not consume a port, update LRU/touch, modify counters, ready cycles, fills or invalidations. Aggregate target-only transition counters are disabled by default. P8/P34 10/80 controls exactly reproduce accepted metrics.
