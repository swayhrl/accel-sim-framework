# Complete-solver discovery decision

`R20R3_ACTIVE_WORLD_NO_MATERIAL_GAIN`

The source-semantic contract was first qualified on 32/32 fresh B0-only replays and six directed negatives. The unchanged 304-worker S1 then passed all four discovery-entry correctness comparisons. Formal complete `solver.solve()` timing followed the preregistered 3 paired groups, each arm/entry/group with two warmups and five samples; all 120 formal samples independently passed effective-output and source-stop checks. The full 168-sample wall/event table is on node164 and compact per-entry medians/MADs are in `DISCOVERY_TIMING.tsv`.

| Group | B0 four-entry wall sum | S1 four-entry wall sum | S1 change vs B0 |
| --- | ---: | ---: | ---: |
| 0 | 2.688487 ms | 4.475653 ms | +66.47% slower |
| 1 | 2.687506 ms | 4.478590 ms | +66.64% slower |
| 2 | 2.686931 ms | 4.476625 ms | +66.61% slower |

Median relative *improvement* is `−66.607%`; every group is slower, with slowdown much larger than the predeclared aggregate MAD estimates. Summed CUDA-event medians are likewise about 2.659–2.661 ms for B0 versus 4.448–4.452 ms for S1. Thus the selected software organization is stably worse at the complete local solver boundary; the ≥5% MATERIAL gate is not met. No holdout was opened.

S1 genuinely changes the selected stage's launch organization: its H-update and blocked-Cholesky first world-grid dimension is 304 rather than 1024, with online ascending active IDs and the original within-world math. Post-run niter histograms show active-ID counts shrink (e.g. t128: 1024→983→876→673→404→180→50→15→2), but those counts are **derived analysis**, not future information supplied to S1. They are not a utilization measurement or speedup ceiling; H may have zero changed rows and Cholesky may skip unchanged worlds. Without new profiling (forbidden in this Goal), the exact share of slowdown from list construction, serial worker processing, and other costs is unresolved. The result supports only this fixed candidate's local complete-solver negative, not full physics-step/RL performance or a hardware conclusion.
