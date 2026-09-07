# FAST64.1 r1 — Execution-path / exactly-once contamination

Status: **ACTIVE_HARD_EXECUTION_FAILURE; NO_FAST64_1_PASS**

This is a compact failure record, not a performance result and not a claim of
a DTC-L1 mechanism defect.  It preserves the live processes and historical
output namespace exactly as observed.

## Affected formal row

| item | value |
| --- | --- |
| row | `fast64_1r1_bicg_oo_cap8192_a1` |
| workload/mode/cap | BICG / OO / 8192 |
| frozen Core | `bbcbb5e7565417102087bc80b14c349b4e568c05` |
| dispatched Framework snapshot | `037f008b330eb230353b60edf126d6be9f45afdc` |
| runtime SHA-256 | `6a8743b4d7adc7f56d40aafdf913718c9e0ad13641e962aa8ef5e3ee35d4f041` |
| observer SHA-256 | `2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e` |
| output namespace | `/workspace/fast64-runs/fast64_1r1_bicg_oo_cap8192_a1` |

## Read-only evidence

1. The first perf stream, `perf_counter_2026-09-07_16-49-18.csv.gz`, reaches
   `47,231,655` simulated cycles.  Its final write is
   `2026-09-07T22:47:13` local time.
2. At the same timestamp, the namespace gained a second perf stream,
   `perf_counter_2026-09-07_22-47-13.csv.gz`; `simulator.stdout` and
   `resource.time` were reopened/truncated.  The current child observable
   through the inherited runner process starts at `2026-09-07 22:47:13` and
   writes to the same stdout/resource paths.  Thus the namespace contains two
   execution epochs and cannot be an exactly-once formal row.
3. The row's `launcher.log` records:

   ```text
   run_fast64_trace.sh: line 74: d: command not found
   ```

   This is an execution-controller anomaly.  The checked-in current runner
   does not contain a retry loop; this record does not infer a source
   mechanism cause from the anomalous live path.
4. `RUN_MANIFEST.tsv` has neither `simulator_exit_status` nor `terminal_utc`.
   The strict collector requires `simulator_exit_status == 0` for every r1
   row, so the row cannot be parsed, compared, reused, or promoted.
5. The cgroup reports `oom_kill=12`, but no contemporaneous kernel record
   attributes an OOM kill to this PID/row.  OOM is retained as host-pressure
   evidence only, not as the asserted causal explanation.

## Required disposition

- Classification: `INVALID_EXECUTION_PATH_CONTAMINATED`; never aggregate or
  treat either epoch as BICG OO@8192 formal evidence.
- FAST64.1 remains **ACTIVE** and its BICG OO 8192-vs-high HARD comparison is
  **UNSATISFIED**.
- Do not stop, signal, rerun, overwrite, clean, or relabel the live process or
  this namespace.  The remaining r1 rows and the FAST64.2 diagnostic remain
  observationally preserved.
- Do not launch additional precompute or repair rows while swap is exhausted
  and the contamination source has not been resolved.
- Recovery requires a source-backed explanation/fix for the duplicate epoch,
  a fresh absent namespace, and a new exact-identity BICG OO@8192 acquisition;
  only a natural exit-0 plus strict validator/comparator evidence may restore
  FAST64.1 eligibility.
