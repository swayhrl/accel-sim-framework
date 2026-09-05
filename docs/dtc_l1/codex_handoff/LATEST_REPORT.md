# Latest Codex Report

Stage: `M5.0B_WORKLOAD_RECOVERY`

Status: **M5-T005 CLOSED — M5.0B WORKLOAD RECOVERY RESUMED**

## Active corrected Paper-10 Base batch

M5.0B is active, with five strictly validated ratio-zero `PAPER_BASE` results:
canonical SpMV (R5DV), BICG, GEMVER, GESUMMV, and 2DConv.  Five isolated jobs
remain live: ATAX, MVT, SYR2K, 2MM, and SYRK.  They retain the frozen config
SHA-256 `993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366`
and runtime SHA-256
`f115144d6009bab4af6d8ab0d86b69e54e8449a4c76a3809561571d32075a453`.
They are `SLOW_BUT_PROGRESSING`, with live simulator counter evidence and no
runtime assertion/fatal/deadlock/output-mismatch signature.  No live job has
been terminated, restarted, or registered as a result.  The checkpoint
`m5/handoffs/M5_0B_PROGRESS_CHECKPOINT.md` is the compact result identity,
accounting, live-PID, E1, and graphics record; the batch detail remains in
`m5/handoffs/M5_0B_RATIO0_BASE_BATCH.md`.  M5.0B is not PASS and M5.0C is not
authorized.

The obsolete external `timeout 86400` supervisors on the five demonstrably
progressing recovery jobs were safely detached after a disposable topology/FD/
observer proof.  The simulators retained their PIDs, process groups, log FDs,
and source-backed simulator progress; no supervisor deadline remains armed.
See `m5/handoffs/M5_0B_TIMEOUT_GUARD_RECOVERY.md`.

M5.0BF is now a mandatory pre-M5.0C execution-path, SM-count, and global
lower-cap fidelity gate.  It is authorized now in an isolated worktree/build/
output namespace while M5.0B jobs continue untouched.  M5.0C remains a join
barrier requiring both M5.0B natural-terminal workload/provenance closure and
an accepted M5.0BF frozen execution-path/platform outcome.  See
`m5/handoffs/M5_0BF_EXECUTION_PATH_LOWER_CAP_FIDELITY_GATE.md`.
Its researcher-confirmed scaling anchor is thesis `2 SM + cap 256` (128
credits/SM), with 80 SM primary and 64 SM sensitivity formal candidates;
current `80 SM + cap 256` is diagnostic-only `CURRENT_INVALID_SUSPECT`.
If Q1 validates the trace semantic contract, trace-driven Accel-Sim becomes
the default remaining formal performance path; workload-local trace gaps use
explicit execution-driven exceptions rather than reverting the campaign.

`m5/handoffs/M5_0BF_Q1_Q2_STATIC_AUDIT.md` records the source-backed common
trace-to-DTC path and the SM7/QV100 origin of the inherited 80-SM platform.
The static path is plausible for the Paper-10 cacheable-global LD/ST contract,
but no exact provenance-compatible completed-Paper trace is locally available
and this host has no visible NVIDIA device for fresh NVBit tracing. A single
isolated, explicitly **nonformal** BICG `PAPER_BASE` trace
transport/lifecycle smoke is active under `/tmp/dtc-l1-m5-0bf-nonformal-trace-bicg-base-20260905`.
Its archived source/ABI mismatch means it is excluded from every formal result
registry/performance table and cannot decide Q1 or Q3; it only tests whether a
real trace frontend reaches and can close the common DTC path. No platform
freeze or M5.0C advancement has occurred. The
formal Q1 pilot remains blocked on an admissible trace artifact/execution
environment. An isolated M5.0BF trace simulator is now built at
`/tmp/dtc-l1-m5-0bf-build/accel-sim.out` (SHA-256
`5b26b8a1e6390596eb449ddcefc4c5a2fbad0ddd1bb85b8396bf90b3ae2fb2c6`) against
Core `12097864`; the auxiliary ignored pybind11 dependency is frozen in the
audit. A later full-trace search found BICG/GESUMMV/2DConv candidates, but
their `gpu-app-collection@dad09cb` source hashes and kernel ABIs differ from
the completed M5 anchors; the local SpMV trace also has a different matrix
input. They are explicitly rejected rather than replayed. The five M5.0B jobs
remain untouched.

For the later Base-only Q3 cap decision, Framework BF commit
`01a2f91f41d008faaa295e3e9cbd471ea50520e3` adds the separate read-only
`util/dtc_l1/parse_m5_0bf_q3.py` extractor. It combines terminal DTC/Base
metrics with perf-counter `chiplet_queue_full_*` and
`L2_dram_queue_full_*` aggregates, so native downstream pressure cannot be
silently omitted. Its only completed replay is a parser smoke over the old
M5.0B BICG raw artifacts; that data remains unregistered and may not be
reused as a formal Q3 result.

Q3 has now started only its minimum source-exact, execution-driven BICG
Base-only primary comparison on the isolated BF namespace: explicit 80-SM
cap-256, cap-10240, and cap-1048576 configurations are each `RUNNING` in
separate `/tmp/dtc-l1-m5-0bf-q3-bicg-*` directories. They have no external
timeouts and their initial simulator cycle/instruction counters advance with
no assertion/fatal/deadlock/output-mismatch signature. These live diagnostics
are not results, do not freeze a platform/cap, do not start the 64-SM
sensitivity or any IO/OO/Extended work, and do not alter the five M5.0B jobs.
The Q1 trace smoke remains active; the formal trace path stays
provenance-blocked by the absent exact Paper trace/GPU tracer environment, so
the Q3 BICG rows are explicitly execution-driven rather than a trace-result
substitute.

Q3 source audit then found that the prior Core terminal report provided peak
but no time-weighted lower-outstanding average.  The current three live BICG
diagnostics are consequently **pre-instrumentation and non-decisive**: they
remain untouched and may naturally close as health/structural evidence, but
they cannot freeze the cap.  The isolated BF Core has a statistics-only
per-core-cycle occupancy sum/sample counter and the BF extractor requires it;
after an isolated rebuild, the minimum Base-only diagnostic must be repeated
before Q3 can close.  No lower-credit admission/release, scheduling, timing,
or assertion behavior changes, and the M5.0B jobs remain untouched.
The isolated CMake Release build of Core `3f23c4aa` has completed at
`/tmp/dtc-l1-m5-0bf-metrics-build` (`libcudart.so` SHA-256
`d39481291fe688f18a3867ecec0c21b8ee3d8a800d351848a0b075b67cca7a9c`).

## Active recovery — approved ratio-zero conventional-L1 policy

The M5-T005 researcher-decision boundary is resolved.  The paper-facing
LEGACY/PAPER_BASE/PAPER_IO/PAPER_OO configuration family now explicitly uses
`-gpgpu_l1_cache_write_ratio 0`; the frozen 16 KiB, 128B-line, four-way
geometry and all write-through/allocation/scoreboard semantics are unchanged.

- Framework `81c75b5d315a29607412a3e28a07c83a2e0a1486` records the four
  ratio-zero formal configurations.  The 32/128 KiB ratio-25 controls and all
  pre-decision evidence remain `DIAGNOSTIC_PLATFORM_POLICY`.
- Core `22db16b8feb007a405634588b6bec97c935d2ecb` adds a source-level CUDA
  dirty-set regression.  Under LEGACY ratio 0 it completes with application
  `PASS`, six L1D misses and zero reservation failures; the log has five
  lower global writes, one global read, and zero `L1_WRBK_ACC` events.
- A fresh Release build and all three DTC CTests PASS.  LEGACY/Base/IO/OO
  VecAdd ratio-zero sentinels PASS at `5562/5708/5545/5533` cycles.  The
  same four M4 Store/Atomic/architectural-`.cg` mixed sentinels PASS.
- Canonical Parboil JDS SpMV medium ratio-zero LEGACY and PAPER_BASE both
  completed naturally in `/tmp/dtc-l1-m5-r5dv3-{legacy,base}-ratio0-20260904`.
  The independent official-output checker passed all 11,948 elements for both.
  LEGACY completed at 1,343,406 cycles / 121,342,000 instructions; PAPER_BASE
  completed at 3,202,814 cycles / 121,342,000 instructions.  PAPER_BASE has
  balanced PIB admit/retire (`741200/741200`) and lower acquire/release
  (`3844406/3844406`) with zero final PIB occupancy and lower outstanding.
  The compact registry IDs are `M5-f43a919958f43224` (LEGACY) and
  `M5-eaf5eb9173dbad12` (PAPER_BASE).  See
  `m5/handoffs/M5_R5DV_DIRTY_VICTIM_VALIDATION.md`.

## Historic stop record — frozen 16 KiB conventional-L1 dirty-set deadlock

Before the researcher resolution, canonical Parboil CUDA JDS SpMV reproduced a real
deadlock in both PAPER_BASE and LEGACY with the frozen 16 KiB, 128B-line,
four-way L1 geometry. The LEGACY control excludes DTC PIB/Tag behavior.

- Corrected source-reachable `cudaFuncCachePreferL1`/`PreferShared` variants
  now use the same frozen 16 KiB geometry; the exact corrected replay still
  fails, so that earlier configuration-fidelity omission is not causal.
- Fatal-state evidence shows no L1D MSHR, no L1 miss-queue item, no memory or
  interconnect traffic, but an L1 latency-queue load retry with all four ways
  of its target set `MODIFIED`.
- `tag_array::probe` returns `RESERVATION_FAIL` because the inherited SM7
  `gpgpu_l1_cache_write_ratio=25` policy does not yet permit a modified victim.
  The retry remains at L1 latency-queue stage zero, so its dependent
  pending-write/scoreboard state cannot retire.

This was a source-reachable conventional-L1 policy ambiguity at the researcher-
frozen geometry.  The later researcher-approved resolution permits only the
explicit ratio-zero configuration correction.  Do not reinterpret write-through
`MODIFIED` state, enlarge the L1, disable deadlock detection, or weaken
pending-write/scoreboard assertions.

Evidence is pushed:

- Core `2f99d81422649242ae4a328767a4848de92a1c3e`
  (`debug(l1): capture fatal dirty-set deadlock state`)
- Framework `a5b1084520a8d06ef032469e538a545c8c6f8fe4`
  (`docs(m5): record frozen 16KiB L1 deadlock evidence`)
- Full causal record: `implementation/M5_ISSUE_LOG.md`, M5-T005.

The user-requested parallel ratio-25 jobs have not been interrupted; their
outputs remain diagnostic only.  R5DV is closed and M5.0B continues from its
existing workload-recovery checkpoint without redoing valid provenance work.

Core M3 checkpoint: `90cb35d5c4f9511a2eacb9e0e809a2d9c74ecb2c`

Framework M3 implementation/parser checkpoint:
`800fc95fe2b502e30e76ce1cb6de050f6069178e`.

## M3 closeout status

Whole-line OO random-access retirement, line-level Ref Count, merge/wakeup,
active reclamation, O01–O13, IO-vs-OO causal HOL, and the 4x32B sector
extension S01–S09 have passed. Real modes 2/3/4 VecAdd self-checks and strict
provenance parsers are recorded in:

`implementation/M3_OO_SECTOR_EVIDENCE.md`.

M2 recovery evidence remains authoritative historical context in:

`implementation/M2_IO_RESPONSE_RECOVERY_EVIDENCE.md`.

## M4 completion-accounting recovery closed

The first provenance-controlled 2DConv triplet exposed a source-reachable DTC
completion failure.  It was recovered under the authorized R4C procedure:

- R4C.0--R4C.2 established Category C duplicate DTC completion for UID 15888
  at PC `0x148`; no conventional pending-write consumption occurred.
- Core `a33ffa87ed4d31d9725b693ea4f822ad1ed1c330` gates IO/OO completion on
  full PIB-reference admission, carries the registered count through a
  production exactly-once ledger, and retains all pending/scoreboard asserts.
- Final-source 2DConv PAPER_IO/PAPER_OO both pass with correct output and
  strict request/dependency/credit/PIB/inflight/ref drain.
- The separate Base rerun is `SLOW_BUT_PROGRESSING`, not deadlocked.

Complete cause, source proof, final log/config hashes, and regression results
are in `implementation/M4_COMPLETION_ACCOUNTING_RECOVERY_EVIDENCE.md`.

## M4 final closeout

All active M4 HARD gates now pass under the authorized frozen-source boundary.
The review pack is `review_packs/M4_COMPUTE_BRINGUP/`.

- Five provenance-resolved Base/IO/OO compute triplets have exact matching
  source-domain Load/Store/Atomic/FENCE_OP counts.
- Store, same-address atomic, architectural `.cg` bypass, IO HOL, OO
  ready-younger retirement, lifecycle closure, parser, and CTest gates pass.
- F00A--F00D pass. F01--F03 are explicitly `SOURCE_UNREACHABLE_NA`: the PTX
  frontend cannot produce the existing dynamic proxy-fence path. No PTX fence
  support was added and `membar` was not mapped to `FENCE_OP`.

## M5.0A anchor closed

M5 now runs only on dedicated M5 branches. Branch ancestry, a Release Core
build, all three DTC CTests, and LEGACY/Base/IO/OO VecAdd sentinels pass. The
M4 LEGACY/IO/OO cycle sentinels match exactly. Runtime/toolchain/config hashes,
the resumable identity registry, safe initial concurrency, and raw-log index
are recorded in `m5/FORMAL_ANCHOR.md` and `m5/handoffs/M5_0A_ANCHOR.md`.

Active work is M5.0B recovery and source verification of all ten thesis compute
workloads. No formal paper performance figure has been claimed yet.
