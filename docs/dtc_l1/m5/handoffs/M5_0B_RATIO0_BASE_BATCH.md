# M5.0B corrected ratio-zero Base batch

Status: **ACTIVE RECOVERY — no formal outcome claimed**

## Purpose

After R5DV closed M5-T005, this batch resumes Paper-10 Base recovery under the
researcher-approved conventional-L1 policy.  It does not alter the frozen
16 KiB, 128 B-line, four-way geometry, write-through/allocation semantics, or
any DTC/pending-write/scoreboard assertion.

## Common identity

| field | value |
| --- | --- |
| Core source anchor | `22db16b8feb007a405634588b6bec97c935d2ecb` |
| Core runtime SHA-256 | `f115144d6009bab4af6d8ab0d86b69e54e8449a4c76a3809561571d32075a453` |
| Framework config anchor | `81c75b5d315a29607412a3e28a07c83a2e0a1486` |
| PAPER_BASE config SHA-256 | `993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366` |
| policy | explicit `-gpgpu_l1_cache_write_ratio 0` |
| source/build | existing M5 PolyBench/GPU anchor in `implementation/M5_COMPUTE_WORKLOAD_MANIFEST.md` |

## Corrected job set and state

| Paper workload | executable | state | isolated run directory |
| --- | --- | --- | --- |
| bicg | `bicg` | `OUTPUT_CLEAN_STRICT` | `/tmp/dtc-l1-m5-0b-ratio0-base-bicg-20260904` |
| atax | `atax` | `RECOVERY_24H_ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-atax-recovery24h-20260904` |
| gemv | `gemver` | `RECOVERY_24H_OUTPUT_CLEAN_STRICT` | `/tmp/dtc-l1-m5-0b-ratio0-base-gemver-recovery24h-20260904` |
| mvt | `mvt` | `RECOVERY_24H_ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-mvt-recovery24h-20260904` |
| syrk | `syrk` | `RECOVERY_24H_ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-syrk-recovery24h-20260904` |
| gesu | `gesummv` | `RECOVERY_24H_OUTPUT_CLEAN_STRICT` | `/tmp/dtc-l1-m5-0b-ratio0-base-gesummv-recovery24h-20260904` |
| syr2k | `syr2k` | `RECOVERY_24H_ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-syr2k-recovery24h-20260904` |
| 2mm | `twomm` | `RECOVERY_24H_ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-twomm-recovery24h-20260904` |
| conv2d | `twodconv` | `RECOVERY_24H_OUTPUT_CLEAN_STRICT` | `/tmp/dtc-l1-m5-0b-ratio0-base-twodconv-recovery24h-20260904` |

All jobs carry their binary/PTX/config/runtime identity in `run_identity.txt`.
They use isolated output directories and the M5 runner; no live process is
shared or reused.  Source-defined output verdicts and strict summaries are
created only after a natural terminal state.

### BICG terminal evidence

The corrected BICG run reached normal simulator exit at `2026-09-04T06:43:14Z`.
Its source-defined CPU/GPU verdict is zero mismatches beyond the 0.50% threshold,
and the strict summary is
`generated/m5_0b_bicg_base_ratio0.json` (`gpu_tot_sim_cycle=51041920`,
`gpu_tot_sim_insn=184803328`).  Final PIB and lower outstanding are zero;
lower acquire/release closes exactly at `19186845/19186845`.  Raw log SHA-256:
`f93222e8d227d869eecc70c88a0036f67c3d49499f9fb02f3621e427bcc69a5a`.
The identity is registered as `M5-949124579bf220d2`.

The first automatic checker result was a tool mapping false negative:
`bicg` was incorrectly assigned the `Number of misses` format even though the
canonical BICG source emits the common `Non-Matching CPU-GPU Outputs` verdict.
`verify_m5_polybench_output.py` now assigns BICG to that comparison format;
the repaired checker passes the preserved raw log.  This does not alter the
workload, source, simulator runtime, or result.

## Observed worker-pool envelope

The M5.0A one-process value was an initial VecAdd calibration, not a bound for
the representative corrected Base wave.  At `2026-09-03T18:26:55Z`, the
already-running nine-job wave was remeasured without launching a further job:
the host had 512 CPUs and 120,471,716 KiB `MemAvailable`; every ratio-zero
worker had zero private `VmSwap`, with RSS 524,288--1,196,032 KiB (median
1,003,520 KiB; p95 1,196,032 KiB).  The host's pre-existing 2 GiB swap pool
was nearly full (72 KiB free), so no additional work is admitted merely from
aggregate-memory arithmetic.

Accordingly, `N_safe=9` is the observed envelope for this **current corrected
Base-only batch**: all nine independent remaining M5.0B jobs are already
admitted, continuously consume CPU, and retain isolated output paths.  This
is scheduling evidence only, not a simulator-performance metric.  Any later
IO/OO, Extended-20, or changed-runtime wave must remeasure its own RSS and
headroom before admission.

## Diagnostic separation

Older active jobs with config hashes `5ca33d...` or `0f037e...`, and older
runtime `c5710...`, are preserved as diagnostic raw evidence.  They must not
be relabeled, deleted, or used as formal ratio-zero data.

## Long-run diagnostic

The first full-load PolyBench kernels are long-running.  At the batch's
wall-clock diagnostic threshold all nine ratio-zero simulator processes remain
live, have no deadlock/assertion/fatal signature, and each advanced Linux
user+system CPU ticks during a two-second observation (`9/9`).  The simulator
log is quiet while a large kernel executes, so lack of new bind lines is not
by itself no progress.  Under `M5_PROBLEM_RESOLUTION_POLICY.md` this state is
`SLOW_BUT_PROGRESSING`, not a performance outcome or `NO_PROGRESS_DEADLOCK`.
The live jobs are preserved; any later terminal state will be classified from
its exact raw log and identity.

## Eight-hour terminal classification

At `2026-09-04T02:09:18Z`, the existing `timeout 28800` guards had ended all
eight remaining worker processes.  The guards were allowed to expire; no
process was manually stopped or restarted.  Before that threshold, each of the
eight processes advanced Linux CPU time during the two-second progress sample,
and each continued at approximately one CPU core through the final monitor
sample.  None of the preserved logs contains normal simulator exit, the
source-defined output verdict, a simulator deadlock report, an assertion, or a
fatal/error signature.  Therefore every row is
`TIMEOUT_SLOW_BUT_PROGRESSING`, not a correctness result, deadlock, or
performance point.

| workload | raw `m5_run.log` SHA-256 |
| --- | --- |
| atax | `0f278782128b765c0d241154043246b309c04870beb8968d836eadde5be055c3` |
| gemver | `4b77163a6bf775b250ac5664943ab73570aeed892007bacea53e92fb4eb8d3ce` |
| gesummv | `3e6cdb00ce35496767bdc2e314bee552538cb66d4b248795f1b52fc7fcb5f748` |
| mvt | `31e68de230a9c4117bff867f1c490e3b4eb1fc2790fdebb7c721476b33aa819c` |
| syrk | `d3cf7c63711546e452b0e96f2f6bc0df20d2771224dd070958128604ad181c1c` |
| syr2k | `ba359d5da634394a8a44bc24d3324aa267bbc45b2d9b923ba67acd1e13811437` |
| twomm | `31c4e55174e13c85bd882a8405f9300ab93b6ee3c94bc4ea9de30e7262f1a995` |
| twodconv | `c8e004d4a1cf7a8f43929dd7c049ce3838856ef96fcb40f50589f85703735937` |

All directories and their `run_identity.txt` files remain in `/tmp`.  They
share the frozen ratio-zero `PAPER_BASE` config SHA-256
`993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366` and
runtime SHA-256 `f115144d6009bab4af6d8ab0d86b69e54e8449a4c76a3809561571d32075a453`.
The next action is a documented bounded-timeout recovery that preserves the
canonical source/algorithm and full-load criterion; no timed-out log may be
strict-parsed or registered as a formal result.

## Recovery wave

The source headers used for the timed-out wave fix the relevant PolyBench
dimensions at 4096 (and 1024 for the standard 2MM header) across their
dataset-label branches.  A `SMALL_DATASET`/`LARGE_DATASET` rebuild would
therefore not yield a distinct source-defined full-load dataset.  The recovery
keeps the exact executable/PTX pair, ratio-zero `PAPER_BASE` configuration and
runtime above, and changes only the externally imposed allowance from 28,800
seconds to a bounded 86,400 seconds.

At `2026-09-04T02:12Z`, eight new isolated directories named
`/tmp/dtc-l1-m5-0b-ratio0-base-<workload>-recovery24h-20260904` were launched
through the same runner.  All eight application processes were live in the
initial two-second check.  The older directories remain immutable timeout
evidence; a recovery result will be output-verified, strict-parsed and
registered only after normal simulator termination.

### GESUMMV terminal evidence

`gesummv` naturally terminated from its recovery directory after `32693`
seconds of simulator wall time.  Its source-defined output verdict is zero
CPU/GPU mismatches beyond the 0.05% threshold, and
`verify_m5_polybench_output.py gesu` passed.  The strict summary is
`generated/m5_0b_gesummv_base_ratio0.json` with
`gpu_tot_sim_cycle=97750749` and `gpu_tot_sim_insn=197296128`.  Termination
accounting closes `DTC_L1_pib_admits/retires=4194688/4194688` and
`DTC_L1_lower_requests_acquired/released=34327761/34327761`; final PIB and
lower outstanding are both zero.  The raw-log SHA-256 is
`7790f664ba70a2e4942714ba7fb494700727ad0bc65f7057ad5461b8054d6089`.
The exact frozen identity is registered as `M5-e648006f1b9cf5f4` under
`M5_0B_RATIO0_BASE_OUTPUT_CLEAN_STRICT`.

### GEMVER terminal evidence

`gemver` naturally terminated from its recovery directory after `37378`
seconds of simulator wall time.  Its source-defined `Number of misses` verdict
is zero, and `verify_m5_polybench_output.py gemv` passed.  The strict summary
is `generated/m5_0b_gemver_base_ratio0.json` with
`gpu_tot_sim_cycle=54960348` and `gpu_tot_sim_insn=923029504`.  Termination
accounting closes `DTC_L1_pib_admits/retires=6292096/6292096` and
`DTC_L1_lower_requests_acquired/released=22065010/22065010`; final PIB and
lower outstanding are both zero.  The raw-log SHA-256 is
`140fefea69d3e3cfc0aa637747a16c7102090cfbdd3d37f5c7ef72f89884e480`.
The exact frozen identity is registered as `M5-f24650643302f0ac` under
`M5_0B_RATIO0_BASE_OUTPUT_CLEAN_STRICT`.

### 2DConv terminal evidence

`twodconv` naturally terminated from its recovery directory.  Its
source-defined output verdict is zero CPU/GPU mismatches beyond the 0.05%
threshold, and `verify_m5_polybench_output.py conv2d` passed.  The independent
strict parser exactly matches the strict-observer summary
`generated/m5_0b_conv2d_base_ratio0.json`, with `gpu_tot_sim_cycle=10215552`
and `gpu_tot_sim_insn=855179376`.  Termination accounting closes
`DTC_L1_pib_admits/retires=5240320/5240320` and
`DTC_L1_lower_requests_acquired/released=14042618/14042618`; final PIB and
lower outstanding are both zero.  The raw-log SHA-256 is
`2278ba0ec95dda577845ef72e63d33e7de7b221b1a3bd6d5d54bceef6dcadc0f`.
The exact frozen identity is registered as `M5-0dbd48dfa4816277` under
`M5_0B_RATIO0_BASE_OUTPUT_CLEAN_STRICT`.

## Next action

For each natural completion: run the source-defined output checker, inspect
deadlock/assertion signatures, strict-parse the log with the exact identity,
and register only a correctness/fidelity-clean result.  A timeout is first
classified using progress evidence under `M5_PROBLEM_RESOLUTION_POLICY.md`; it
is not treated as a performance result or a deadlock by duration alone.

## 2026-09-05 active checkpoint

The reviewable live-PID, simulator-counter, strict-result, and completion
accounting snapshot is `M5_0B_PROGRESS_CHECKPOINT.md`.  It records five
validated Paper-10 Base members (canonical SpMV, BICG, GEMVER, GESUMMV, and
2DConv) and the five untouched live recovery jobs (ATAX, MVT, SYR2K, 2MM, and
SYRK).  This batch remains **ACTIVE**, not PASS.

## External timeout-guard recovery

The 86,400-second external supervisors were an operational allowance, not a
simulator semantic boundary.  After each live recovery job demonstrated
simulator-level progress, the obsolete supervisors were safely detached using
a disposable process-topology/FD/observer proof.  No simulator or runner was
signalled, restarted, or reconfigured.  The exact topology and post-detach
progress evidence is `M5_0B_TIMEOUT_GUARD_RECOVERY.md`.
