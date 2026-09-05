# M5.0B Paper-10 Base progress checkpoint

Status: **ACTIVE — CHECKPOINT ONLY; NOT M5.0B PASS**
Snapshot: `2026-09-05T08:53:10+08:00`

This checkpoint records the state of the existing ratio-zero `PAPER_BASE`
wave without launching, stopping, replacing, or otherwise affecting a
simulator process.  The formal identity is Core
`22db16b8feb007a405634588b6bec97c935d2ecb`, Framework
`81c75b5d315a29607412a3e28a07c83a2e0a1486`, config SHA-256
`993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366`,
runtime SHA-256
`f115144d6009bab4af6d8ab0d86b69e54e8449a4c76a3809561571d32075a453`, and
explicit `-gpgpu_l1_cache_write_ratio 0`.  Every full binary/PTX/input hash
below is also the immutable identity in `m5/generated/result_registry.json`.

## Completion accounting

Paper-10 contains **10** workloads.  **Five** Base results are fully validated
now; **five** are still live.  The R5DV path supplied only canonical SpMV.
The current corrected M5.0B recovery batch supplied BICG, GEMVER, GESUMMV,
and 2DConv.  No live row is a result, and no M5.0C work is authorized by this
checkpoint.

| origin | completed | count |
| --- | --- | ---: |
| R5DV | canonical Parboil JDS SpMV `PAPER_BASE` ratio-zero | 1 |
| corrected M5.0B Base recovery | BICG, GEMVER, GESUMMV, 2DConv | 4 |
| still running | ATAX, MVT, SYR2K, 2MM, SYRK | 5 |

## Validated Base results

`natural` means normal simulator exit, not an elapsed-time inference.  `PASS`
in the output column is the workload's source-defined checker; every parser
column is a strict `dtc_l1_summary_v1` parse.  `PIB/lower` reports
admit/retire, final PIB occupancy, acquire/release, and final lower
outstanding respectively; all five drain exactly to zero.

| workload / provenance | registry identity and source/input/PTX identity | natural / output / parser | final accounting | compact evidence |
| --- | --- | --- | --- | --- |
| canonical SpMV (R5DV) | `M5-eaf5eb9173dbad12`; workload `08f834ff68e9e092db1f988974ddb8491bba06c176037e862aa81b839ec5900c`; PTX `8e74fe5310962f413d7e29bfb205571a13cb9c7739cd86ebb3b7b1ed51ba39bf`; matrix/vector `abbe1909f57d6fc17fc800446bac326bd0c5343305cf193b3aa1bc8f40c82ec9` / `d155de2b9615cae3c2bb8b60a9e82a7d26be7e80de772a5f1c0cb830d2e49061` | natural; official checker PASS, 11,948 elements; strict PASS | `741200/741200`, `0`; `3844406/3844406`, `0` | `m5_r5dv3_spmv_base_ratio0.json`; `M5_R5DV_DIRTY_VICTIM_VALIDATION.md` |
| BICG (M5.0B) | `M5-949124579bf220d2`; workload `db1cc9246ee97389b32396d3b20294a3c8a89139067cabcda93ec87d0ed1f84b`; PTX `8a0f2ab72a5ac679037e17cfd2f748e7e53ce119c03648948fe8771058c98485`; no external input | natural; zero CPU/GPU mismatches beyond 0.50%; strict PASS | `3145984/3145984`, `0`; `19186845/19186845`, `0` | `m5_0b_bicg_base_ratio0.json`; `M5_0B_RATIO0_BASE_BATCH.md` |
| GEMVER (M5.0B) | `M5-f24650643302f0ac`; workload `04d6c9b931988faf7f715eeda40f7688e0fee98b4b114a0c86d4a0f6da2dce5d`; PTX `83a82a7ab281ef3edfa4afe535b7a25c63cb9b9146b0dbf6ed41d61406ae277f`; no external input | natural; `Number of misses: 0`; strict PASS | `6292096/6292096`, `0`; `22065010/22065010`, `0` | `m5_0b_gemver_base_ratio0.json`; `M5_0B_RATIO0_BASE_BATCH.md` |
| GESUMMV (M5.0B) | `M5-e648006f1b9cf5f4`; workload `32da3ab10c6b0cdb0a7e9af569899e51ebb302a19602f9d37e3377469ab6447e`; PTX `484a2f76bcd03e27ff8cdcd7920a9ea2f36a755116e07ed057302432a1f936f2`; no external input | natural; zero CPU/GPU mismatches beyond 0.05%; strict PASS | `4194688/4194688`, `0`; `34327761/34327761`, `0` | `m5_0b_gesummv_base_ratio0.json`; `M5_0B_RATIO0_BASE_BATCH.md` |
| 2DConv (M5.0B) | `M5-0dbd48dfa4816277`; workload `8ade2d6153cdaa9816cb6c4bc4d65320fe12c0b4fa9f18f90db7d50fd4831bc1`; PTX `270310ce224577d6d5804a416cd5f2a0ef86b054ae9d1dd594792c781cfcf8fd`; no external input | natural; zero CPU/GPU mismatches beyond 0.05%; strict observer and parser exactly match | `5240320/5240320`, `0`; `14042618/14042618`, `0` | `m5_0b_conv2d_base_ratio0.json`; `M5_0B_RATIO0_BASE_BATCH.md` |

2DConv is specifically the current canonical ratio-zero `PAPER_BASE` result:
its registry/config/runtime identity above, recovery directory
`/tmp/dtc-l1-m5-0b-ratio0-base-twodconv-recovery24h-20260904`, and raw-log
SHA-256 `2278ba0ec95dda577845ef72e63d33e7de7b221b1a3bd6d5d54bceef6dcadc0f`
separate it from every older M4 or obsolete 2DConv run.  It completed at
`10215552` cycles / `855179376` instructions; its summary SHA-256 is
`125dc4916bb1acb979344324c8bbcc5fa9a5558ad72f5b1db59e06ec7ce5150c`.

## Live Base jobs: read-only health snapshot

The five PIDs below are the intended live `PAPER_BASE` processes in their
isolated recovery directories.  `gpu_sim_cycle/gpu_sim_insn` comes from the
latest appended perf-counter member; it is a live simulator-level signal, not
terminal `gpu_tot_*` accounting.  `gpu_completed_cta` was zero in each last
record, so it is not claimed as a completion marker.  The two samples at
`08:51:19` and `08:53:10+08:00` (111 seconds apart) show nonzero
cycle/instruction deltas in every row.  CPU time close to elapsed is supporting
evidence only, not the sole basis for the classification.

| workload | PID | output directory | elapsed / CPU | state / RSS | latest live simulator evidence | scan / classification |
| --- | ---: | --- | --- | --- | --- | --- |
| ATAX | 3572276 | `/tmp/dtc-l1-m5-0b-ratio0-base-atax-recovery24h-20260904` | `22:41:01` / `22:38:22` | `Sl`, 839,680 KiB | `gpu_sim_cycle=32,791,000` (`+86,000`); `gpu_sim_insn=266,508,704` (`+688,896`); completed CTA `0` | no runtime assertion/fatal/deadlock/output-mismatch signature (only config's deadlock-detect declaration); `SLOW_BUT_PROGRESSING` |
| MVT | 3572277 | `/tmp/dtc-l1-m5-0b-ratio0-base-mvt-recovery24h-20260904` | `22:41:01` / `22:38:34` | `Sl`, 753,664 KiB | `gpu_sim_cycle=35,112,500` (`+84,500`); `gpu_sim_insn=285,185,184` (`+680,896`); completed CTA `0` | same scan result; `SLOW_BUT_PROGRESSING` |
| SYR2K | 3572296 | `/tmp/dtc-l1-m5-0b-ratio0-base-syr2k-recovery24h-20260904` | `22:41:01` / `22:38:31` | `Sl`, 1,519,616 KiB | `gpu_sim_cycle=11,563,500` (`+23,000`); `gpu_sim_insn=106,241,920` (`+202,752`); completed CTA `0` | same scan result; `SLOW_BUT_PROGRESSING` |
| 2MM | 3572310 | `/tmp/dtc-l1-m5-0b-ratio0-base-twomm-recovery24h-20260904` | `22:41:01` / `22:38:24` | `Sl`, 1,347,584 KiB | `gpu_sim_cycle=14,101,500` (`+27,000`); `gpu_sim_insn=1,061,379,552` (`+1,955,872`); completed CTA `0` | same scan result; `SLOW_BUT_PROGRESSING` |
| SYRK | 3572311 | `/tmp/dtc-l1-m5-0b-ratio0-base-syrk-recovery24h-20260904` | `22:41:01` / `22:38:28` | `Sl`, 1,269,760 KiB | `gpu_sim_cycle=12,234,500` (`+23,000`); `gpu_sim_insn=134,615,552` (`+228,896`); completed CTA `0` | same scan result; `SLOW_BUT_PROGRESSING` |

All five have the common config/runtime identity stated above; their exact
binary/PTX hashes remain in each directory's immutable `run_identity.txt`.
No raw log, binary, build tree, trace, or live output directory is committed by
this checkpoint.

## Extended E1 and graphics boundary

The approved Extended-20 portfolio remains frozen.  CUDA SDK 4.2 has recovered
the source/parameter/build/PTX/output-contract evidence for all eight selected
members, but their simulator output smokes and final input/output formalization
remain pending.  Rodinia and Parboil retain source/launcher/checker audits;
their build/PTX/input/smoke freeze is incomplete where documented.  E2 remains
gated by M5.2, and no Extended formal simulation has started.  This is only a
summary of the already committed E1 record in `M5_E1_EXTENDED20_FORMALIZATION.md`.

`GRAPHICS_SOURCE_BACKED_UNAVAILABLE@ed36abb8f98372dbd1fef11d5b0e8780fb8bf17d`.
M5.9--M5.11 remain skipped; this checkpoint does not reopen graphics work.

## Gate

M5.0B remains **ACTIVE**, not PASS.  There is no new HARD failure and no new
researcher-decision boundary in this checkpoint.  The next action after a
natural live-job terminal state is the existing output-check, error-scan,
strict-parse, registry, and accounting-closeout sequence; no M5.0C action may
start beforehand.
