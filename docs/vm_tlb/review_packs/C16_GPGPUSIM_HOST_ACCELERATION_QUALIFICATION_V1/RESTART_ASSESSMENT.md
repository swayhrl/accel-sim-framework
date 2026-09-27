# Current-primary restart assessment

Snapshot UTC: `2026-09-27T03:49:09Z`.

- R0 baseline: 589/1565 kernels complete (37.636%), PID 250086, CPU490.
- M1 B16: 592/1565 kernels complete (37.827%), PID 250087, CPU440.
- M1 diagnostic: 221/1565 kernels complete (14.121%), PID 266910, CPU360.
- Common formal-primary completion: 589/1565 (37.636%).

Measured provisional combined speedup was negative: -16.99% versus the current authority binary and -9.68% versus pristine same-build. Consequently the restart break-even is **not finite**: restarting would discard completed work and run more slowly. No primary process, binary, config, output, affinity, priority, or controller was modified, paused, restarted, or signaled.

Recommendation: continue the current R0/M1 runs unchanged. Keep this negative qualification as the default for B8/B24/BFULL; revisit only with a new host candidate that clears exactness and a repeatable >=5% end-to-end gate.
