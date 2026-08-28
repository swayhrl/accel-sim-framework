# Corrected L2 integrated pressure closeout

`run_integrated_pressure.sh` runs compact, trace-driven P1--P6 cases against
the production `accel-sim.out` linked to `hrl/l2-char-baseline-v1`.  It uses
the conventional QV100 sector L2 and only shrinks existing finite resources;
it does not enable an alternative L2 backend or any Decoupled mechanism.

The P1/P2/P3/P6 fixtures remain in the existing local fixture tree
(`L2_CHAR_TRACE_ROOT`) and P4 uses the FRC merge fixture
(`L2_CHAR_FRC_TRACE_ROOT`), so this clean framework branch does not import an
experimental simulator branch.  P5 is a compact local trace: one warp writes
32 dirty, direct-mapped lines separated by 128 MiB.  That stride preserves one
16-way IPOLY subpartition and set, forcing real writeback contention.

The harness records trace SHA-256 values in its manifest.  It rejects a run
unless the production terminal snapshot has zero preview/commit mismatches,
no resource or credit leak, sane blocker episodes (`cycles >= episodes >=
requests`), and each case's intended nonzero signature:

- P1: lower-request queue corrected-path activation.
- P2: immediate-response queue corrected-path activation.
- P3: nonzero data-port busy time under real fill/writeback traffic.
- P4: one-entry MSHR and MissQ each reach their exact configured capacity.
- P5: reserved writeback progress-credit use.
- P6: end-to-end corrected-path activation.

Run, after building the core and frontend:

```bash
tests/l2_char/run_integrated_pressure.sh --out /tmp/l2-char-pressure
```

The result directory contains raw logs, resolved overlays, and `summary.tsv`.
It is closeout evidence, not a workload-characterization campaign.
