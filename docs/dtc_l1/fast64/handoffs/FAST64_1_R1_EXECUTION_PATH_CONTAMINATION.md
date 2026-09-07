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

## Root-cause audit (2026-09-08)

The root cause is classified:

`ROOT_CAUSE_PROBABLE_ACTIVE_SCRIPT_MUTATION`

This is strong controller-path evidence, not a claim about DTC mechanism
semantics.  It is not marked *confirmed*, because no retained instantaneous
read trace establishes precisely which unbuffered Bash bytes produced the
historical `d` command.

| evidence | observation |
| --- | --- |
| launch snapshot | `037f008b330eb230353b60edf126d6be9f45afdc` carried runner blob SHA-256 `6f0783149bc7882dd792f3c25a25b15aafbcadc04a77cf5dfb730534bdc00188` |
| later live-path mutation | commit `4144983b8fbd7bc5e47edab0430bcbea5dcce26f`, committed at `2026-09-07T19:30:46+08:00`, changed the same path; its runner SHA-256 is `14635253a97027e2766d31b104be069fdb6d37b5b01ff347cd77335d9c5cf30c` |
| read-only `/proc` observation | all seven live r1 Bash wrappers started at `2026-09-07 16:49:17`; their fd `255` resolves to the live worktree path, inode `35261121`, device `9c`, size `2892`, SHA-256 `146352…` |
| contaminated parent continuity | `3657929` remained the parent across both epochs; its current child chain is `3657929 -> 57419 (/usr/bin/time) -> 57420 (accel-sim.out)` and the second child began at `2026-09-07 22:47:13` |
| harmless `/tmp` reproduction | an in-place `apply_patch` mutation while Bash waited for `sleep` made Bash resume without either old or new trailing statement.  It did not recreate the exact `d` diagnostic, but proves that this update class can alter later long-lived Bash control flow. |

Therefore the relevant answer to the retained-evidence alternatives is **A**:
the long-lived wrappers were still reading the live worktree runner later
modified in place, rather than a preserved/deleted inode.  The exact malformed
continuation remains not reconstructible, so the conservative classification
above applies.

## Immutable future recovery contract

`run_fast64_trace_v2.sh` is now a future-only immutable-attempt runner.  Before
any recovery execution, its exact bytes must be SHA-addressed, copied to
`/tmp/fast64-runners/<runner_sha>/run_fast64_trace_v2.sh`, SHA-verified, made
non-writable, and executed from that path.  A v2 namespace contains one
atomic creation witness plus `RUN_START.tsv` and `RUN_TERMINAL.tsv` receipts
with one matching UUID.  The strict validator's single-epoch rule is
calibrated against the three clean NN rows (one perf stream, one initialization
marker, one natural-exit marker per row).

The controller also separates the frozen scientific/config snapshot
(`037f008b330eb230353b60edf126d6be9f45afdc`) from runner/controller SHA and
from parser/validator identity.  The v2 `/bin/true` controller test passed
receipt creation, immutable-path/SHA binding, natural exit-0 recording, and
fail-closed rejection of a duplicate namespace.  It is not a simulator result.

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
- Recovery is prepared only, under
  `util/dtc_l1/prepare_fast64_1_r2_recovery.sh`, for the distinct absent
  namespace `fast64_1r2_bicg_oo_cap8192_a1`.  It has no default launch mode;
  its guarded launch path requires a fresh explicit resource audit and the
  contaminated epoch's natural terminal receipt before it can start.  The
  companion `collect_fast64_1_r2_recovery.sh` composes clean unaffected r1
  rows with the r2 replacement without changing the historical collector.
  Only natural exit-0, exact immutable-receipt, strict validator, accounting,
  and cap-comparator evidence may restore FAST64.1 eligibility.
