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

## Active job set

| Paper workload | executable | isolated run directory |
| --- | --- | --- |
| bicg | `bicg` | `/tmp/dtc-l1-m5-0b-ratio0-base-bicg-20260904` |
| atax | `atax` | `/tmp/dtc-l1-m5-0b-ratio0-base-atax-20260904` |
| gemv | `gemver` | `/tmp/dtc-l1-m5-0b-ratio0-base-gemver-20260904` |
| mvt | `mvt` | `/tmp/dtc-l1-m5-0b-ratio0-base-mvt-20260904` |
| syrk | `syrk` | `/tmp/dtc-l1-m5-0b-ratio0-base-syrk-20260904` |
| gesu | `gesummv` | `/tmp/dtc-l1-m5-0b-ratio0-base-gesummv-20260904` |
| syr2k | `syr2k` | `/tmp/dtc-l1-m5-0b-ratio0-base-syr2k-20260904` |
| 2mm | `twomm` | `/tmp/dtc-l1-m5-0b-ratio0-base-twomm-20260904` |
| conv2d | `twodconv` | `/tmp/dtc-l1-m5-0b-ratio0-base-twodconv-20260904` |

All jobs carry their binary/PTX/config/runtime identity in `run_identity.txt`.
They use isolated output directories and the M5 runner; no live process is
shared or reused.  Source-defined output verdicts and strict summaries are
created only after a natural terminal state.

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
