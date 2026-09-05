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

- State: `OBSERVED -> REPRODUCED -> ROOT_CAUSE_CLASSIFIED -> RESEARCHER_DECISION_RESOLVED -> R5DV_VALIDATION_ACTIVE -> CLOSED`.
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

- R5DV closure: the canonical medium (`bcsstk18`) ratio-zero LEGACY and
  PAPER_BASE replays both reached normal simulator exit with the deadlock
  detector enabled and `parboil_spmv result: PASS`.  The independent official
  output checker passed all 11,948 elements for both outputs (identical output
  SHA-256 `94148cba6fbed65468efb4317ee255e8f90fec37e1b6a31c706337a02d785127`).
  LEGACY completed at 1,343,406 cycles / 121,342,000 instructions under config
  `e49453b37d2bc430abf9bc56caf1f1a10e7d665cd5b9d24f7e919fd65f1f1970`.
  PAPER_BASE completed at 3,202,814 cycles / 121,342,000 instructions under
  config `993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366`;
  it drained exactly `741200/741200` PIB admits/retires and
  `3844406/3844406` lower acquires/releases with final PIB occupancy and lower
  outstanding both zero.  Strict summaries/registry records are
  `M5-f43a919958f43224` and `M5-eaf5eb9173dbad12`.  Raw-log SHA-256 values and
  complete identities are preserved in
  `m5/handoffs/M5_R5DV_DIRTY_VICTIM_VALIDATION.md`; raw outputs remain outside
  Git.  This closes M5-T005 without changing frozen DTC or conventional-L1
  semantics.

## M5-T006 — M5.0D preflight finds unexported Figure-4.2/Figure-4.7 fields

- State: `OBSERVED -> SOURCE_CLASSIFIED -> QUEUED_FOR_M5.0D`.
- Scope: this is an instrumentation-completeness item for the later M5.0D
  metric lock; it does not invalidate or alter the currently running M5.0B
  source-recovery Base jobs.
- Source evidence: `cache_reservation_fail_reason` already distinguishes
  `LINE_ALLOC_FAIL`, `MISS_QUEUE_FULL`, `MSHR_ENRTY_FAIL`, and
  `MSHR_MERGE_ENRTY_FAIL` (`gpu-cache.h`).  `cache_stats` exposes those
  reasoned counters through `get_aggregated_fail_stats`, but the current
  Paper-Base M5 emission in `gpgpu_sim::shader_print_dtc_l1_stats`
  (`shader.cc`) exports only the two MSHR reasons.  It must not substitute
  `DTC_L1_primary_stall_tag_bank` for the missing true Tag/cacheline category:
  that event remains a separate diagnostic channel.
- Source evidence for Figure 4.7: lower-request acquire/release and current
  outstanding state are exact and asserted (`gpgpu_sim::dtc_l1_try_acquire_*
  / release_*` in `gpu-sim.cc`), but the current anchor records only final
  current/peak values.  It lacks the frozen active-kernel cycle sum and sample
  denominator needed for the required per-SM average live-miss metric.
- Authorized automatic resolution after M5.0C: export all four conventional
  failure-reason counters without changing cache decisions; sample the common
  lower-request live state at the source-defined active-kernel boundary; add
  directed cases for each reason and create/complete closure; extend strict
  parser fields; prove sentinel timing is unchanged apart from an explicitly
  repaired behavior.  This is ordinary Goal work, not a researcher-decision
  boundary.  The current ratio-zero M5.0B runtime and its live processes stay
  untouched until their natural terminal state.

## M5-T007 — BICG output checker selected the wrong source-defined verdict format

- State: `OBSERVED -> SOURCE_CLASSIFIED -> REPAIRED -> REGRESSED -> CLOSED`.
- Evidence: the natural corrected ratio-zero BICG completion at
  `/tmp/dtc-l1-m5-0b-ratio0-base-bicg-20260904/m5_run.log` ends with
  `Non-Matching CPU-GPU Outputs Beyond Error Threshold of 0.50 Percent: 0`
  and normal simulator exit.  The old checker classified `bicg` with the
  unrelated `Number of misses` expression and therefore falsely reported zero
  source verdicts.
- Root cause: the checker workload map, not BICG source or simulator output.
  The canonical source's emitted comparison is the common CPU/GPU mismatch
  count, matching ATAX/MVT/SYRK/GESU/SYR2K/2MM/Conv2D format.
- Repair/regression: move `bicg` to `COMPARE_WORKLOADS` in
  `util/dtc_l1/verify_m5_polybench_output.py`; rerunning the repaired checker
  on the preserved raw log prints
  `PASS workload=bicg source_comparison_mismatches=0`.  The strict summary
  `m5/generated/m5_0b_bicg_base_ratio0.json` passes with final PIB/lower
  occupancy zero and exact `19186845/19186845` lower acquire/release closure.
  No simulator behavior, workload, config, or assertion changed.

## M5-E1-001 — historical FWT `11_19` label is not yet a formal source identity

- State: `OBSERVED -> SOURCE_CLASSIFIED -> SOURCE_RECOVERED -> BUILD_PTX_REPRODUCED -> OUTPUT_SMOKE_PENDING`.
- Scope: Extended-20 E1 source/build/input recovery only.  This does not
  alter Paper-10 M5.0B, and E2 remains gated on M5.2.
- Evidence: the historical CUDA-SDK launcher declares
  `fastWalshTransform -logK 11 -logD 19`
  (`accel-sim-decoupled-l2/util/job_launching/apps/define-all-apps.yml`), and
  the old pretrace records a fixed trace manifest SHA-256
  `a91e2655cd672585257294d09834e7d6647350e6c9ece7769fea5cb38fb6d6f2`.
  Those artifacts remain useful only for historical runtime planning.
- Source mismatch: the locally recoverable CUDA 11.0 sample at
  `gpgpu-workloads`-derived commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`
  fixes `log2Kernel=7` and `log2Data=23`; its `main` does not parse `-logK` or
  `-logD`.  It therefore cannot be silently relabeled as the approved
  `fastWalshTransform_11_19` workload.
- Recovery result: historical commit
  `b059fdae25c2aabf737486aada743fca114469ce` contains the exact parameter
  parser.  Its isolated CUDA-11.8 `sm_52` rebuild and PTX extraction succeed;
  the future source-defined checker remains the `L2norm < 1e-6` `PASSED`
  verdict.  Complete hashes, compatibility-helper identities, and the pending
  simulator smoke are in `m5/extended20/FWT_11_19_E1_RECOVERY.md`.  No
  historical trace/cycle result is promoted to an M5 formal result by this
  recovery.

## M5-E1-002 — selected Parboil output checkers require legacy Python semantics

- State: `OBSERVED -> SOURCE_CLASSIFIED -> REPAIRED -> REGRESSED -> CLOSED`.
- Scope: Extended-20 E1 output-check formalization only; Paper-10 M5.0B
  processes and the M5.2 gate for E2 are unaffected.
- Evidence: selected Parboil `bfs`, `cutcp`, `mri-q`, `sad`, and `stencil`
  `tools/compare-output` scripts declare `#!/usr/bin/env python` and use
  Python-2 `file(...)` and/or `print` syntax. Their exact checker and support
  module hashes are frozen in
  `m5/extended20/RODINIA_PARBOIL_E1_SOURCE_AUDIT.md`. The observed host has
  Python 3.11 and no `python2` executable. `histo` is distinct: its native
  checker is exact host `cmp`.
- Classification: `OUTPUT_CHECKER_RUNTIME_COMPATIBILITY`, not a workload,
  source-algorithm, simulator, or DTC semantic issue. The source-defined
  comparison predicates remain authoritative.
- Required resolution/regression: use an isolated source-equivalent Python-2
  runtime or an explicitly recorded Python-3 compatibility adapter. Before
  accepting any E1 smoke, demonstrate equivalence on preserved reference and
  deliberately mismatching fixtures for every affected predicate; keep the
  original scripts and identities unchanged. Do not replace a tolerance
  checker with exit-code-only, file-size-only, or omitted validation.
- Resume point: after deterministic CUDA builds/PTX and inputs are available,
  run the source-defined checker/adapter smoke for each selected Parboil
  workload, then retain the exact interpreter/adapter identity in the E1
  manifest. No E2 job may launch before M5.2 freezes the common anchor.
- Resolution/regression: add
  `util/dtc_l1/verify_m5_extended_parboil_output.py`, a Python-3 adapter that
  directly preserves each selected source checker's file format, exact/relative
  tolerance predicate, and trailing-data rule. Its fixture suite
  `test_verify_m5_extended_parboil_output.py` exercises both an accepted and a
  deliberately mismatching case for `bfs`, `cutcp`, `histo`, `mri-q`, `sad`,
  and `stencil`; `python3 -m py_compile` and all six tests pass. A real
  `histo` candidate input self-comparison also prints PASS. This closes the
  interpreter-compatibility issue only; every workload still requires its own
  source-defined output smoke after build/PTX/input recovery.

## M5-0BT-001 — traced-source tree hash dereferenced a tracked directory symlink

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> REPAIRED -> REGRESSED -> CLOSED`.
- Scope: T1 BICG capture setup only; no CUDA application, raw trace, immutable
  bundle, or formal result was produced.
- Reproduction: the clean tracer pin
  `0db04452ec1c47630e4b08002067d82c6811e243` tracks `.cursor` as a symlink
  to `.claude`.  The controller's source-tree hash iterated `git ls-files`
  then opened each resolved path, so on the capture host it attempted to read
  the directory target and raised `IsADirectoryError`.
- Classification: capture-controller provenance implementation defect, not an
  NVBit, CUDA, workload, trace, DTC, or source-identity ambiguity.
- Resolution: hash the canonical `git ls-files -s` tracked mode/object/path
  listing after the clean pinned-commit check. This retains Git object identity
  for regular files and symlinks without dereferencing links.
- Regression/resume: offline capture-contract test asserts the mode/object
  listing path; controller compilation and full no-GPU suite pass. Resume T1
  from the same BICG sources, NVBit archive, CUDA 11.8, V100 and output root;
  the two pre-build failed launcher logs remain operational evidence only.

## M5-0BT-002 — root tracer Makefile builds an unrelated incompatible legacy tool

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> REPAIRED -> REGRESSED -> CLOSED`.
- Scope: T1 capture-host tracer build only. The required NVBit trace tool and
  postprocessor both compiled; no GPU application, raw trace or bundle started.
- Evidence: root `make` built `tracer_tool/tracer_tool.so` and
  `traces-processing/post-traces-processing`, then entered
  `others/spinlock_tool`, whose legacy source fails against NVBit 1.8 with
  unresolved instrumentation API identifiers.
- Classification: unrelated auxiliary-tool build scope, not a trace tool,
  NVBit, CUDA, workload, DTC or source-identity failure.
- Resolution/regression: controller now invokes only `make -C tracer_tool`
  and `make -C tracer_tool/traces-processing`, exactly the two artifacts it
  validates and uses. The contract regression asserts this scoped build; no
  NVBit/tracer/application source, trace format or runtime semantics changed.
- Resume point: restart the same BICG T1 identity after deploying the compact
  controller repair; retain failed launcher logs as operational evidence.

## M5-0BT-003 — capture-host device probe used unavailable Runtime UUID APIs

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> REPAIRED -> V100_RETEST_PASS -> CLOSED`.
- Scope: V100/CUDA-11.8 identity preflight after the required tracer and
  postprocessor build; no CUDA workload application, raw trace, immutable
  bundle, archive, replay, or formal result has started.
- Evidence: retry-4's controller reached the probe compile and failed. Exact
  CUDA-11.8 reproduction reports that `cudaDeviceGetProperties` and
  `cudaDeviceGetUuid` are undefined. The Runtime header exports
  `cudaGetDeviceProperties`; UUID lookup is the CUDA Driver API
  `cuDeviceGetUuid`.
- Classification: capture-controller host-identity adapter defect, not a
  V100, CUDA toolchain, NVBit tracer, workload, trace-format, DTC, or source
  provenance failure.
- Repair: obtain device properties with `cudaGetDeviceProperties`, obtain the
  UUID with `cuDeviceGetUuid`, check each API result, and link the isolated
  probe with `-lcuda`. The output contract remains exactly the logical-device
  header plus the V100/UUID/CC/memory row used in capture provenance.
- Hardware retest: the isolated CUDA-11.8/sm70 probe emitted the selected
  Tesla V100-PCIE-32GB, CC 7.0 and Driver-API UUID; the values agree with the
  independent `nvidia-smi` identity query.
- Resume point: deploy this tested adapter to a new clean control checkout and
  resume the same BICG T1 identity, retaining every prior retry log and the
  already-built scratch tracer only as operational evidence.

## M5-0BT-004 — selected PolyBench build propagated a false final predicate

- State: `OBSERVED -> REPRODUCED -> CLASSIFIED -> REPAIRED -> V100_RETEST_PENDING`.
- Scope: the exact BICG CUDA application build after tracer and device
  preflight passed. No application execution, raw trace, immutable bundle,
  archive, replay, or formal result has started.
- Evidence: retry-5 invoked the fixed CUDA-11.8/sm70 BICG script; `nvcc`
  emitted the expected binary, but the script returned 1. Exact reproduction
  showed only compiler warnings and the same binary, followed by `RC=1`.
- Root cause: with `set -e`, the final unselected workload's
  `[[ selected ]] && build` predicate became the script's final status.
- Repair: use an explicit `if` for each requested workload. An unselected
  final item now completes successfully rather than changing the selected
  build's status. Source files, source SHA, CUDA version, sm70 flag and build
  command are unchanged; the contract test locks this success behavior.
- Resume point: deploy to a new clean control checkout, rerun the exact BICG
  build on V100, then resume the same T1 capture identity.
