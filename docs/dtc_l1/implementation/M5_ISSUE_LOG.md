# M5 Issue Log

## M5-T001 — BICG Base standard-input smoke exceeded the initial 900-second budget

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> RESOLVED -> REGRESSED -> CLOSED`
- Affected experiment: M5.0B Base smoke, canonical PolyBench/GPU BICG default
  `STANDARD_DATASET` (`NX=NY=4096`).
- First attempt: `/tmp/dtc-l1-m5-0b-base-bicg-20260903`, launched with the
  formal Base config and a 900-second diagnostic wall-clock budget.
- Evidence: the process maintained approximately one fully utilized host CPU
  core and a stable 532480 KiB RSS until `timeout` ended it; the log contains a
  `gridDim=(16,1,1), blockDim=(256,1,1)` first kernel bound to SM 0--15, and
  contains no assertion, fatal error, or simulator deadlock diagnostic.
- Classification basis: the simulator's enabled deadlock detector checks for
  unchanged committed instruction count every 50000 simulated cycles. It did
  not report a deadlock before the wall-clock diagnostic limit.  The initial
  config did not request periodic runtime-stat output, so exact intermediate
  instruction/cycle values were not emitted by that run.
- Resolution: retain the unmodified canonical standard input (there is no
  smaller distinct canonical BICG dataset in this source release), preserve the
  original run as diagnostic evidence, and rerun serially with a longer bounded
  allowance. This is a runtime classification, not a performance value and not
  a change to DTC-L1 semantics or assertions.
- Extended-run progress sample: at 2026-09-03, `/proc/<pid>/stat` advanced from
  65589 to 68079 user CPU ticks over 25 seconds while RSS remained 536576 KiB.
  The current Core's Base-mode runtime output does not expose intermediate
  queue/last-progress values; its source deadlock detector remains enabled and
  would terminate after an unchanged committed-instruction check.  This sample
  therefore supports the host-progress portion of `SLOW_BUT_PROGRESSING` while
  preserving the explicit limitation on unavailable intermediate simulator
  counters.
- Closure: the 3600-second bounded rerun completed in 2886 seconds with exit
  zero, no CPU/GPU mismatches beyond the 0.50% threshold, `gpu_tot_sim_cycle`
  6831012, `gpu_tot_sim_insn` 184803328, zero final PIB/lower occupancy, and
  exact 6311168/6311168 lower acquire/release counts. Strict parser summary
  `m5/generated/m5_0b_bicg_base.json` registered as `M5-27a653d36a4da01b`.

## M5-B001 — SpMV wrapper Makefile referred to retired Parboil `args.c`

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> REPAIRED -> REGRESSED -> CLOSED`.
- Evidence: the historical wrapper Makefile requested
  `$(COMMON_SRC)/args.c`; canonical Parboil commit
  `4e0fc54866546efa44fe93af57c9cef62f6c8eb9` has no such file and exports
  `pb_ReadParameters` from `common/src/parboil_cuda.c`.
- Resolution: `util/dtc_l1/build_m5_parboil_spmv.sh` directly compiles the
  wrapper sources and canonical `parboil_cuda.c`, omitting only the stale,
  nonexistent object. It preserves the wrapper algorithm and links with
  `-cudart shared`; the isolated rebuild produced `spmv` and matching PTX.

## M5-T002 — Parboil SpMV `large` Base smoke exceeded its bounded wall-clock allowance

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> RESOLVED -> REGRESSED -> CLOSED`.
- Affected experiment: M5.0B Base smoke, canonical Parboil CUDA JDS SpMV.
- Attempt: `/tmp/dtc-l1-m5-0b-base-spmv-large-20260903`, formal Base config,
  official `large` Dubcova3 input, and a 7200-second wall-clock allowance.
- Evidence: `timeout` returned `exit=124`; no `spmv.out` was produced.  The raw
  log has no assertion, fatal, or simulator-deadlock diagnostic.  Its
  `perf_counter_2026-09-03_15-18-00.csv.gz` grew monotonically from 552406 to
  7349400 bytes while the process retained a fully utilized host core.  The
  first JDS kernel is `gridDim=(765,1,1), blockDim=(192,1,1)` and binds shaders
  0--79.  Thus the timeout records continuing simulation work, not no-progress.
- Classification: `SLOW_BUT_PROGRESSING / INPUT_SCALE_RUNTIME_TIMEOUT`; this is
  not a DTC-L1 semantic failure and does not justify weakening a pending-write,
  scoreboard, or completion assertion.
- Resolution basis: M5's input policy requires the *smallest standard dataset*
  that gives work to all eight SMs and more than a trivial CTA wave.  Canonical
  Parboil `medium` (`bcsstk18.mtx`, 11948 rows) launches 63 CTAs with the same
  192-thread block, while the rejected M4 input launched only a trivial 42-row
  case.  The medium rerun is selected from source/work-amount evidence alone,
  not by any Base/IO/OO comparison.
- Medium diagnostic: `/tmp/dtc-l1-m5-0b-base-spmv-medium-20260903` used the
  same binary/PTX/Base config with the canonical bcsstk18 input and a
  3600-second allowance.  It ended with `exit=124` after reaching kernel 21 of
  the source-faithful 50-kernel loop; its perf-counter file reached 10742092
  bytes and no output, assertion, fatal, or deadlock record occurred.
- Extended resolution: retain the identical canonical medium input and launch
  one serial 14400-second bounded run.  This changes only the diagnostic
  wall-clock allowance.  It neither alters the 50-launch source algorithm nor
  changes any DTC-L1 mechanism, configuration, pending-write, scoreboard, or
  completion assertion.
- Closure: `/tmp/dtc-l1-m5-0b-base-spmv-medium-extended-20260903` completed
  the source-faithful 50-kernel loop in 8296 seconds with exit zero.  The
  wrapper reported PASS and the independent official-output checker passed all
  11948 elements.  Strict summary `m5/generated/m5_0b_spmv_base.json` is
  registered as `M5-9c1b7df007ca2a11`: `gpu_tot_sim_cycle=3011530`,
  `gpu_tot_sim_insn=121342000`, final PIB/lower occupancy zero, exact
  741200/741200 PIB admit/retire, and exact 3538250/3538250 lower
  acquire/release counts.

## M5-T003 — ATAX Base standard-input smoke exceeded its initial bounded allowance

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> MITIGATION_RERUN_ACTIVE`.
- Affected experiment: M5.0B formal Base smoke, canonical PolyBench/GPU ATAX
  `STANDARD_DATASET` (`NX=NY=4096`).
- Evidence: `/tmp/dtc-l1-m5-0b-base-atax-20260903` ran for the complete
  7200-second allowance and ended `exit=124`.  It remained at approximately
  one host CPU core and 675840 KiB RSS; its perf-counter file continued to
  grow.  It remained in source kernel 1 (`atax_kernel1`) and emitted neither a
  simulator deadlock diagnostic nor an assertion/fatal error.
- Classification: `SLOW_BUT_PROGRESSING / STANDARD_INPUT_RUNTIME_TIMEOUT`.
  The incomplete run is diagnostic evidence only, not a DTC-L1 semantic or
  assertion failure.
- Resolution: retain the exact source, standard input, PTX, and formal Base
  configuration; rerun serially within its isolated process with an enlarged
  wall-clock allowance.  No workload reduction, mechanism change, or
  pending-write/scoreboard/completion-assertion bypass is permitted.

## M5-T004 — inherited M5 run config dynamically expands conventional L1D to 128 KiB

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> REPAIRED -> REGRESSED -> CLOSED`.
- Scope: this is a configuration-fidelity issue, not a DTC frontend or
  workload-correctness failure.  It affects the current M5.0A sentinel's
  timing interpretation and all M5.0B Base workload timing/pressure evidence
  produced with config SHA-256
  `5ca33d1948ea288f69944a6c2f33eb8f0496f07f8ee917b876a7c8579b9ad733`.
  In-flight Base jobs are deliberately allowed to finish as diagnostic
  progress evidence; they are not candidates for paper-facing formal results.
- Source/config evidence: the inherited file sets
  `-gpgpu_adaptive_cache_config 1`, `-gpgpu_unified_l1d_size 128`, and
  `-gpgpu_cache:dl1 S:4:128:64,...`.  `cache_config::init` parses that
  geometry as `{sets,line,associativity}` and computes capacity as
  `line * sets * associativity` (`gpu-cache.h`); the adaptive kernel path
  selects the zero-shared-memory option and changes the association from its
  maximum (`shader.cc`).  The completed BICG and SpMV logs both report
  `GPGPU-Sim: Reconfigure L1 cache to 128KB` (BICG
  `/tmp/dtc-l1-m5-0b-base-bicg-extended-20260903/m5_0b.log`; SpMV
  `/tmp/dtc-l1-m5-0b-base-spmv-medium-extended-20260903/m5_run.log`).
- Classification: `FORMAL_CONFIG_FIDELITY_MISMATCH`.  M5 v1 freezes a 16 KiB,
  128B-line, 4-way conventional Base L1 and requires unrelated platform
  configuration to be identical across Base/IO/OO.  A dynamic 128 KiB L1 is
  source-reachable and contradicts that frozen configuration.
- Repair and regression: committed-to-be formal config artifacts now disable
  adaptive resizing and use `S:32:128:4` (32 sets × 128B × 4-way = 16 KiB):
  `LEGACY_16KB` SHA-256 `462703a8...238702cc`, `PAPER_BASE_16KB`
  `96621d28...da90b634`, `PAPER_IO_16KB` `10d3da49...8b09e8e8`, and
  `PAPER_OO_16KB` `0005c350...c0d026dc`. Every file also gives the
  source-reachable `cudaFuncCachePreferL1` and `cudaFuncCachePreferShared`
  transitions the same fixed geometry and shared-memory allocation as its
  default L1D.  The repaired runner materializes every selected configuration
  as its simulator-required `gpgpusim.config`.
  A fresh VecAdd sentinel on all four members PASSed without a `Reconfigure L1
  cache` log line: LEGACY/Base/IO/OO cycles were respectively
  `5562/5708/5545/5533`, preserving the prior M5.0A behavior differential.
  The corrected 10-workload Base batch is active under the repaired Base
  config.  Preserve all earlier outputs and timeout observations as
  `DIAGNOSTIC` raw evidence only; do not use their cycles, pressure, or
  speedups in formal figures.  No DTC architecture, workload input, or
  pending-write/scoreboard assertion changed as part of this repair.

## M5-T005 — 16 KiB four-way conventional L1 reaches a source-defined dirty-set deadlock

- State: `OBSERVED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED -> RESEARCHER_DECISION_RESOLVED -> R5DV_VALIDATION_ACTIVE`.
- Affected experiment: M5.0B canonical Parboil CUDA JDS SpMV, medium
  `bcsstk18` input, `PAPER_BASE_16KB.config` SHA-256
  `0f037eb6d7ae5bb66ae57110f5c3e93112adfd810f9b91898957286a93259c10`.
- Evidence: isolated run
  `/tmp/dtc-l1-m5-0b-formal-base-spmv-16kb-20260903/m5_run.log` completed
  startup and bound the first 374-CTA JDS kernel, then the existing simulator
  deadlock detector reported no writeback for 84,030 cycles at simulated cycle
  `65,970 + 4,294,817,296 = 4,294,883,266` and named cores 6 and 39 as no
  longer committing.  It aborted
  through `gpgpu_sim::deadlock_check` with `SIGABRT` and wrapper `exit=1`.
  The run identity fixes canonical input hashes, PTX, Core runtime, and the
  corrected 16 KiB config; no output was produced.
- Cache-preference correction control: SpMV invokes
  `cudaFuncSetCacheConfig(spmv_jds, cudaFuncCachePreferL1)`. The first 16 KiB
  artifacts had inherited `dl1PrefL1=none`; every formal configuration was
  corrected to give that source-reachable transition the same frozen geometry.
  The exact corrected Base replay still deadlocked, so this was a separate
  configuration-fidelity defect, not the root cause below.
- Root-cause evidence: the corrected LEGACY replay (which removes Base
  PIB/Tag behavior) again deadlocked at cycle
  `27,256 + 4,294,867,296`, cores 6/26/39. At each first blocked L1 latency
  queue entry, its L1D MSHR and miss queue were empty, no memory partition or
  interconnect was busy, and the request retained `MEM_FETCH_INITIALIZED`.
  The exact retry probe returned `RESERVATION_FAIL` with `mshr_hit=0`,
  `mshr_full=0`, and `miss_queue=0/16`. Its target set had all four ways
  `MODIFIED` (for example SM6 set12: `0xc0145600`, `0xc0148600`,
  `0xc013e600`, `0xc013d600`).
- Source classification: `tag_array::probe` permits a modified victim only
  when `dirty_line_percentage >= m_wr_percent`; the inherited SM7 setting is
  `-gpgpu_l1_cache_write_ratio 25`. In this execution the affected sets are
  fully modified before global dirty occupancy reaches 25%, so the function
  returns `RESERVATION_FAIL`. The existing `L1_latency_queue_cycle` retains
  that stage-0 request for retry; because no candidate can become eligible,
  the queue cannot advance and its dependent pending writes/scoreboard
  registers never close.
- Historical disposition: this is a source-reachable conventional-L1 policy outcome at
  the frozen 16 KiB/4-way geometry, not a DTC completion-accounting failure.
  Raising/changing the inherited dirty-victim ratio or altering write-through
  `MODIFIED` semantics would change the frozen conventional-L1 policy and the
  Base/IO/OO experimental meaning. No such repair is authorized by the M5
  specification. Static 32 KiB and 128 KiB controls remain non-interrupted
  diagnostic work, but cannot replace the frozen 16 KiB result. Do not
  disable deadlock detection, enlarge the formal L1, or weaken any
  pending-write/scoreboard assertion. **RESEARCHER_DECISION_REQUIRED.**

- Researcher resolution and active recovery: the approved paper-facing policy
  is explicit `-gpgpu_l1_cache_write_ratio 0` for every LEGACY/PAPER_BASE/
  PAPER_IO/PAPER_OO 16 KiB formal configuration.  Framework commit
  `81c75b5d315a29607412a3e28a07c83a2e0a1486` changes only that option in the
  four corrected files; 32/128 KiB ratio-25 controls remain diagnostic.
  Core commit `22db16b8feb007a405634588b6bec97c935d2ecb` adds a real-path
  regression with four write-through MODIFIED same-set lines followed by a
  fifth same-set load.  Under ratio 0 it passes with zero L1D reservation
  failures and zero fabricated L1 writebacks while five global writes and one
  global read reach the lower hierarchy.  Release/CTest, four ratio-zero
  VecAdd sentinels, and four M4 Store/Atomic/`.cg` sentinels pass.  Canonical
  medium SpMV LEGACY/PAPER_BASE ratio-zero runs are active; retain every
  ratio-25 run and hash as pre-decision diagnostic evidence, never as formal
  ratio-zero data.
