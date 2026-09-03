# M5.0B corrected ratio-zero Base batch

Status: **ACTIVE — no formal outcome claimed**

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
| atax | `atax` | `ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-atax-20260904` |
| gemv | `gemver` | `ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-gemver-20260904` |
| mvt | `mvt` | `ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-mvt-20260904` |
| syrk | `syrk` | `ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-syrk-20260904` |
| gesu | `gesummv` | `ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-gesummv-20260904` |
| syr2k | `syr2k` | `ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-syr2k-20260904` |
| 2mm | `twomm` | `ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-twomm-20260904` |
| conv2d | `twodconv` | `ACTIVE` | `/tmp/dtc-l1-m5-0b-ratio0-base-twodconv-20260904` |

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

## Next action

For each natural completion: run the source-defined output checker, inspect
deadlock/assertion signatures, strict-parse the log with the exact identity,
and register only a correctness/fidelity-clean result.  A timeout is first
classified using progress evidence under `M5_PROBLEM_RESOLUTION_POLICY.md`; it
is not treated as a performance result or a deadlock by duration alone.
