# Latest Codex Report

## FAST64.1 five-row immutable-R2 continuation authorized (2026-09-08)

The researcher superseded the bootstrap two-worker ramp and authorized an
immediate five-row continuation wave, while preserving the two live cohort-1
R2 process trees and all existing SHA-pinned controllers unchanged. A new,
future-only one-shot dispatcher has a separate continuation lock and a fixed
five-row scope; it cannot touch the two existing namespaces. It verifies the
same immutable-v2 runner, Core/runtime/A1 observer/scientific-config identity
tuple, frozen config bytes, fresh namespace absence, unique UUID, atomic
receipts, and topology-aware explicit CPU placement.

The fresh 60-second cgroup audit at
`/tmp/fast64-r2-continuation-resource-audit-20260908T123617Z.tsv` passed full
five-worker admission: 12.822 useful core equivalents under a 384-core quota,
zero throttling/swap-out/OOM/memory-PSI, 252 distinct physical-core candidates,
18,647,875,584-byte 5+1 RSS requirement versus 203,603,755,008-byte cgroup
headroom, and 67,846,701,056 output-free bytes. Host loadavg is supplemental,
not a mixed-scope cgroup rejection. See
`fast64/handoffs/FAST64_1_R2_FULL_WAVE_CONTINUATION.md`. Admission is
authorized; dispatch receipts determine the next execution-state update.

The dispatch succeeded at `2026-09-08T12:41:22Z`: all five fixed future-only
rows received fresh immutable START receipts, so the complete R2 wave is now
**7/7 LIVE**. The rows are BICG OO@8192, BICG IO@1048576, BICG OO@1048576,
GESUMMV IO@8192, and GESUMMV IO@1048576, pinned to topology-selected CPUs
5/6/7/8/10. Their runner/Core/runtime/A1/scientific-config tuple exactly
matches cohort 1. The original Base@8192 and IO@8192 rows were neither opened
nor altered. A short follow-up found all seven direct simulator children in
state `R` at about 99% CPU, no growth in swap-out or OOM totals, zero memory
PSI and zero cgroup throttling. The two cohort-1 perf streams had progressed
to 82.0M and 88.0M cycles; new rows are live, not yet terminal results.

The existing autorefiller observed seven namespaces and recorded
`FAST64_R2_AUTOREFILL_DISPATCH_COMPLETE` at `2026-09-08T12:42:26Z`; it did not
create duplicates. The untouched strict closeout controller remains waiting
for 7/7 terminal receipts. FAST64.1 is still stage-gated pending natural
terminal/strict collector/comparison evidence. Compact per-row UUID/PID and
follow-up evidence is in `fast64/handoffs/FAST64_1_R2_FULL_WAVE_CONTINUATION.md`.

## FAST64.1 R2 dispatch-lock inheritance recovery (2026-09-08)

The first two immutable R2 supervisors inherited the dispatcher's advisory
lock descriptor.  Read-only `fuser` and `/proc/<pid>/fd/9` evidence ties the
lock to both live supervisor/process trees; this is an execution-controller
lifetime defect, not a simulator, DTC, configuration, or scientific-identity
defect.  The live rows are preserved untouched: there is no safe in-place FD
closure that does not perturb production processes, so the current lock will
release only when those rows naturally reach their terminal state.

The future-only dispatcher now closes FD 9 before `setsid` creates a detached
supervisor.  A disposable lock/sleep topology regression proves that the child
remains live while a second dispatcher can acquire the advisory lock; the
existing namespace mkdir, immutable SHA binding, UUID, receipts, and
single-epoch validator are unchanged.  This removes the issue for all rows
launched after the two live rows.  Status is
`FAST64_1_R2_RESOURCE_ADMISSION_PENDING` solely for this bounded lock lifetime;
FAST64 Goal execution remains active.  On either natural terminal event, take
a fresh resource audit and admit the next frozen-priority missing R2 row.
A low-frequency host-only `monitor_fast64_1_r2_autorefiller.sh` is active in
the `fast64-r2-autorefiller` persistent tmux controller: it holds a separate monitor lock, pins the reviewed
dispatcher SHA, waits for the live dispatch lock to disappear, performs the
same 60-second read-only audit, and invokes the dispatcher only for a fresh
`YES` admission.  It exits fail-closed on dispatcher-source drift and does not
inspect, signal, alter, or collect an existing R2 namespace.

A separate `fast64-r2-closeout` persistent tmux controller now waits only for
all seven fixed R2 terminal receipts.  It is SHA-pinned to the existing
fail-closed R2 collector, invokes that collector only after all seven rows are
terminal, and atomically publishes an external collector-pass marker only on
strict success.  It never launches or alters a simulator, and a collector
failure remains a retryable evidence failure rather than a stage promotion.

## FAST64.1 topology-aware R2 admission is ready (2026-09-08)

The remote review supersedes the former fixed/exclusive `74-80` pool rule:
host CPU placement is scheduling metadata, never a FAST64 scientific identity.
The dispatcher now uses `lscpu -p=CPU,CORE,SOCKET,NODE` and live affinity data,
prefers distinct physical cores, excludes only singleton/narrow pinned
simulator affinity, and ranks remaining candidates by current scheduler
occupancy.  A broad `Cpus_allowed_list=0-511` is soft host contention, not
exclusive ownership of every CPU.  R2 remains explicitly `taskset` pinned;
all immutable-v2, SHA, UUID, namespace, receipt and strict-validator guarantees
are unchanged.

`audit_fast64_r2_resources.sh` remains read-only but now publishes the
required `FAST64_R2_RESOURCE_AUDIT_V1`, including topology candidates, realistic
live p95 RSS and historical-R1 output footprint, cgroup/swap/OOM/PSI/I/O
deltas, and autonomous `safe_to_launch` / `authorized_workers` N_safe decision.
It never launches a process.  A passing audit authorizes the dispatcher to
admit the frozen-priority missing R2 rows without waiting for historical R1
termination; a conservative one-to-two worker ramp remains the policy.

The first formal immutable R2 ramp was admitted at `2026-09-08T04:06:56Z`
from `/tmp/fast64-r2-resource-audit-launch-v2.tsv`: `safe_to_launch=YES`,
`authorized_workers=2`, 384 cgroup quota cores, 249 available distinct
physical-core candidates, 9 pre-launch simulators, p95 RSS 8,925,478,912
bytes, 139,714,740,224 bytes MemAvailable, zero swap-out/OOM/throttling/PSI/iowait and
45,600,477,184 bytes output free.  The sample's 30-page swap-in without swap-out or PSI
is recorded but is not active pressure.  The new live rows are BICG
Base@8192 (`fast64_1r2_bicg_base_cap8192_a1`, CPU 0, UUID
`0c84f039-346e-4d28-9d0f-b7a4e04ee8b0`) and BICG IO@8192
(`fast64_1r2_bicg_io_cap8192_a1`, CPU 3, UUID
`81a1e97c-af78-417d-a38a-440a0a43ccd7`).  Both have immutable runner SHA
`bf9a84…`, exact Core/runtime/A1/scientific-config provenance and published
`RUN_START.tsv`; neither is terminal or promotable yet.

## FAST64.2 forced lower-create stress decision resolved (2026-09-08)

The one high-cap BICG/PAPER_IO diagnostic has naturally terminated with a
clean single execution epoch, exit 0, exact lower create/issue/response
conservation, and drained final state.  It is **not** FAST64.2 PASS: its
source-coupled entries-one overlay recorded
`DTC_L1_io_lower_create_queue_full_stalls = 0`.

Frozen-Core source sequencing explains why the former high-cap positive retry
was invalid:
PAPER_IO produces at most one candidate per SM cycle, and the following
cycle's pre-memory-stage issue routine removes it whenever the high global cap
has credit.  The NoC-full path only retains a separate unbounded issue queue.
Hence the former high/non-binding-cap plus natural queue-full requirement was
incompatible with this PAPER_IO path.  Researcher-authorized Option 2 now
classifies the completed row as `FAST64_2_HIGH_CAP_NEGATIVE_CONTROL` and
prepares an immutable NN/IO `cap=512, PIB=1` source-reachable coupled positive
stress.  The run remains resource-gated; no Core change or new simulator run
was made.  See `fast64/handoffs/FAST64_2_FORCED_STRESS_SEMANTIC_GATE.md`.
The FAST64 Goal is active again; FAST64.1 immutable R2 remains the first
formal-closeout priority whenever a fresh resource audit is safe.

## FAST64.1 immutable R2 recovery preparation (2026-09-08)

At this recovery checkpoint FAST64.1 was stage-gated by an execution-path
failure; no stage promotion and no R2 simulator launch had occurred.  Current
authority is `GOAL ACTIVE; FAST64.1 STAGE_GATE_PENDING`, rather than a global
Goal-blocked state.  Read-only `/proc` evidence resolves the
historical controller issue as
`ROOT_CAUSE_PROBABLE_ACTIVE_SCRIPT_MUTATION`: all live r1 Bash wrappers still
read fd `255` from the mutable worktree runner, whose SHA changed from the
launch snapshot's `6f078314…` to `14635253…`; the contaminated BICG OO parent
survived both observed epochs.  A second BICG OO@1048576 row has independently
produced the same two-epoch footprint and `line 74: d: command not found`.
The exact malformed continuation cannot be
reconstructed, so this is deliberately not labeled confirmed.

Future-only recovery is now prepared as a complete seven-row R2 wave, not a
one-row patch.  The v2 runner requires an SHA-verified, non-writable
`/tmp/fast64-runners/<sha>/` copy, one UUID, atomic namespace creation, and
immutable START/TERMINAL receipts.  Its validator requires the receipt chain
and a single-epoch proof calibrated on the clean NN rows.  A harmless
`/bin/true` test passed immutable binding, receipts, and duplicate namespace
rejection; it is not a scientific result.  The guarded dispatcher dynamically
admits only the fresh audited number of R2 workers; old r1 diagnostics are not
a scientific wait barrier.  The whole r1 qualification wave is
`SUPERSEDED_NONFORMAL_EXECUTION_PATH_AT_RISK`; all r1 collector output is
nonformal.  See
`fast64/handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.

The earlier R2 resource snapshot was `FAST64_1_R2_RESOURCE_WAIT_ACTIVE`, not
Goal blocked.  It has since been superseded by the fresh CPU-slot-wait
observation above; the dispatcher/collector/config/identity preparation and
independent FAST64.2 diagnostic work remain authorized.  Whenever a historical
job naturally exits, take a new resource audit and admit the highest-priority
safe R2 row without a wait-for-all barrier.

## FAST64.1 r1 execution-path contamination (2026-09-07)

This historical R1 checkpoint is nonpromotable; it does not describe the
current R2 execution state.  The
BICG OO@8192 r1 namespace has two observed simulator epochs in a single
exactly-once output directory, no `simulator_exit_status`, and a controller
anomaly (`line 74: d: command not found`).  Its prior epoch reached
47,231,655 cycles, but neither epoch is formal evidence.  The cgroup's
`oom_kill=12` is retained as host-pressure evidence only; causal attribution
has not been established.  All remaining live r1 and FAST64.2 processes are
preserved untouched.  A future-only atomic-namespace runner has passed a
harmless controller test; no formal recovery row has been launched.  See
`fast64/handoffs/FAST64_1_R1_EXECUTION_PATH_CONTAMINATION.md`.

## FAST64 throughput-update checkpoint (2026-09-07)

FAST64 logical state remains **FAST64.1 ACTIVE**; no FAST64.1, FAST64.2, or
FAST64.3 PASS is claimed.  The seven formal-instrumented-Core r1 qualification
rows continue naturally and untouched.  The researcher-authorized scheduling
policy now separates strict `LOGICAL_STAGE_ACCEPTANCE` from provenance-bound
`PHYSICAL_PRECOMPUTED_ACQUISITION` (Framework `4144983b...`).

One high-cap BICG/IO lower-create stress diagnostic is live as
`PRECOMPUTED_FAST64_2_DIAGNOSTIC_PENDING_FAST64_1_ACCEPTANCE`; it uses the
formal `bbcbb5e...` Core and a source-coupled candidate-queue/PIB bound of one,
not a performance configuration.  NN/Base@8192 has naturally terminated and
strict-validated as `PRECOMPUTED_PENDING_FAST64_1_2_ACCEPTANCE` (6,985 cycles,
1,284,872 instructions, zero lower-cap-full and drained accounting).  It is
not yet an accepted FAST64.3 result.  Shared-host swap is exhausted and output
headroom is about 62 GiB, so the first controlled ramp stops pending a fresh
resource/throughput audit.  See
`fast64/handoffs/FAST64_PRECOMPUTED_ACQUISITION.md`.

Stage: M5.0BT exact trace capture and qualification — **RESOLVING_ISSUE
M5-0BT-011 (2MM SIM_HOST immutable-receipt capacity)**.

## C2P trace versus M5 ATAX host-throughput review (2026-09-07)

The requested non-invasive audit is recorded in
`m5/handoffs/M5_0BT_C2P_TRACE_HOST_THROUGHPUT_AUDIT.md`.  It establishes that
the historical C2P ATAX trace and the exact M5 NVBit trace are not the same
payload: kernel-1 ABI differs, C2P has `(16,1,1) x (256,1,1)` while M5 has
`(128,1,1) x (32,8,1)`, M5 kernel-1 has 8.95x C2P's dynamic instructions, and
the two-kernel M5 traceg set is 10.26x the C2P byte size.  C2P therefore
cannot be used as a formal M5 trace substitute, although it may later be an
explicitly nonformal host-diagnostic control.

The apparent 2,466-versus-about-280 simulated-cycles/s gap does not show a
nine-fold per-instruction host regression.  The available evidence decomposes
it into about 6.58x higher M5 simulated IPC/work per cycle and only about
1.34x lower host simulated-instruction throughput.  The live M5 process was
CPU-active with no sampled I/O wait or swap pressure; the shared legacy
observer settings and the independently equivalent A1 observer experiment
cannot explain the gap.  No active process, config, Core behavior, formal
result identity, or stage has changed.

## 2MM copyback storage admission (2026-09-06)

2MM has reached remote `ARCHIVE_PASS` with archive SHA-256
`59e918821bc54a772434acc70d2d439abefd8ccf696c055be2564b53d520863e`; this is
not yet a SIM_HOST receipt or formal result.  The fail-closed copyback gate
stopped before rsync because 36,313,600,000 local free bytes are below its
58,013,565,949-byte exact requirement (archive 3,416,630,277 + complete
bundle 50,301,968,376 + 4 GiB margin).  No payload was deleted, recaptured,
or unpacked.  Researcher-authorized archive-only rsync is now preserving the
compressed `.tar.zst` locally, but it is deliberately not a receipt: no
archive SHA, internal bundle validation, or `LOCAL_IMMUTABLE_PASS` is claimed.
`m5/handoffs/M5_0BT_2MM_STORAGE_ADMISSION_STOP.md` binds the evidence and
requires capacity provision followed by full transfer-only receipt resume;
M5.0BT remains ACTIVE.

### Background hold and rented-host disposition

At researcher direction, the live archive-only 2MM rsync and the repaired
ATAX Base/IO/OO replays continue naturally in the background while no new M5
stage work is started.  The compact handoff is
`m5/handoffs/M5_0BT_2MM_STORAGE_ADMISSION_STOP.md`.  The rented capture host
is **not yet safe to release** while this archive-only transfer is partial.
After its natural completion, a SHA-256 comparison of the compressed archive
to the recorded remote archive SHA is sufficient no-unpack proof that permits
capture-host release, while still leaving 2MM outside formal
`COPYBACK_SHA_PASS`/`LOCAL_IMMUTABLE_PASS`.  Its later formal receipt remains
gated on capacity plus internal-bundle and immutable-store validation.  This
is a provenance constraint; it does not imply an active GPU workload.

The archive-only transfer has now naturally completed.  Its local compressed
archive is exactly 3,416,630,277 bytes and direct SHA-256 matches the recorded
remote archive SHA:
`59e918821bc54a772434acc70d2d439abefd8ccf696c055be2564b53d520863e`.
`ARCHIVE_ONLY_COPYBACK_SHA_PASS` makes the rented V100 capture host safe to
release for storage purposes.  This no-unpack retention proof deliberately
does not promote 2MM to a formal immutable receipt or authorize a new M5
stage.

The researcher has authorized the interim eight-workload repaired-Core replay
batch (Paper-10 excluding `2mm` and `syrk`). Its exact scope, non-bypass ATAX
qualification gate, and dispatch order are frozen in
`m5/handoffs/M5_0BT_EIGHT_WORKLOAD_REPLAY_PLAN.md`. BICG and SpMV are retained
instead of duplicated; no new replay may bypass the live ATAX natural-terminal
parser/accounting gate.

A source audit has also confirmed a native `.traceg.xz` frontend route.  It is
an isolated `TEXT_TRACEG_XZ_DERIVED` storage candidate only, not an accepted
trace representation: byte-decompression, ordered-list, and same-bundle
Base/IO/OO differential proofs remain mandatory before formal use.  See
`m5/handoffs/M5_0BT_COMPRESSED_TRACE_STORAGE_CANDIDATE.md`.  Its first
no-write SpMV trace byte-round-trip PASS is evidence only, not a formal replay
or receipt claim.

## E1 local `sm_70` build preflight (2026-09-06)

BlackScholes has a reproducible, isolated CUDA-11.8 `sm_70` source/build/PTX
preflight with all legacy helper inputs hash-bound.  SIM_HOST has no visible
GPU, so it did not execute the source-defined `QA_PASSED` checker and has not
promoted the row beyond `SOURCE_READY`; `BUILD_READY` and
`TRACE_CAPTURE_READY` counts remain zero.  The exact candidate identities and
the mandatory real-V100 follow-up gates are recorded in
`m5/extended20/CUDA_SDK_E1_SOURCE_AUDIT.md` and
`m5/handoffs/M5_E1_V100_CAPTURE_READINESS.md`.  This is E1 preparation only;
it neither consumes V100 capture capacity nor changes the Paper-10 priority.
The canonical post-link artifact is an independently double-built,
byte-identical stripped ELF; the resolved nvcc local-symbol metadata issue is
recorded as `M5-E1-003`.

FastWalshTransform now has the same local two-build `sm_70` preflight under
its exact `-logK 11 -logD 19` source contract.  It remains `SOURCE_READY`
because no V100 output smoke or dynamic trace audit has run; E1 readiness
counts and the Paper-10 capture priority are unchanged.

VectorAdd and scalarProd have now passed the same two-build local `sm_70`
preflight with normalized ELF/PTX identities.  Neither has run a V100
source-defined output smoke or dynamic trace audit, so both remain
`SOURCE_READY`; the E1 readiness ledger remains unchanged.

Transpose, scan, and sortingNetworks have also completed their independent
two-build local `sm_70` preflights under their exact SDK 4.2 tree identities.
They remain `SOURCE_READY` pending V100 output smokes and dynamic trace audits;
the physical-capture queue and E1 readiness ledger remain unchanged.

convolutionSeparable has now completed the same isolated two-build CUDA-11.8
`sm_70` preflight from the frozen SDK 4.2 object.  Its normalized ELF and PTX
are byte-identical across both builds, but SIM_HOST did not run the real-V100
`--size 3072` L2-norm `QA_PASSED` checker or dynamic trace audit.  Its
constant-memory transfer path remains a runtime semantic gate, so it remains
`SOURCE_READY`; no readiness count, capture priority, or active V100 work is
changed.

Rodinia hotspot1 has independently passed an equivalent local CUDA-11.8
`sm_70` build/PTX reproducibility preflight from the clean 3.1 source tree.
It remains `INPUT_READY`, not `BUILD_READY`: no V100 source-defined checker,
input/runtime/launch freeze, or dynamic trace audit has run. The Paper-10
capture queue and all E1 exclusive readiness counts are unchanged.

Rodinia btree has also passed a two-build local CUDA-11.8 `sm_70` preflight,
including its two selected GPU-kernel PTX artifacts. A CUDA-11.8-compatible
compiler-driver wrapper replaces only the historical invalid quoted gencode
expansion; it changes no source, launch, or runtime semantics. btree remains
`INPUT_READY`, not `BUILD_READY`, pending its V100 checker and dynamic trace
audit; Paper-10 capture priority and readiness counts are unchanged.

Rodinia lud likewise has a two-build local CUDA-11.8 `sm_70` preflight,
preserving its source-defined `-O3 -use_fast_math` build mode and three kernel
PTX entries. It remains `INPUT_READY`, not `BUILD_READY`: the V100 verifier,
runtime/input/launch freeze, and dynamic trace audit have not run. Paper-10
capture priority and readiness counts remain unchanged.

Rodinia dwt2d has also completed a two-build local CUDA-11.8 `sm_70` preflight
with a reproducible eight-unit PTX manifest. It remains `INPUT_READY`, not
`BUILD_READY`, pending source-defined output/reference checking and dynamic
trace audit; Paper-10 capture priority and readiness counts are unchanged.

Rodinia gaussian has likewise completed a two-build local CUDA-11.8 `sm_70`
preflight while preserving its source-defined workgroup constants. It remains
`SOURCE_READY`, not `BUILD_READY`, pending a selected input/checker, V100
smoke, and dynamic trace audit; Paper-10 capture priority is unchanged.

Rodinia cfd_097k has completed an independently repeated local CUDA-11.8
`sm_70` build/PTX preflight using only the exact frozen tree's legacy
host-timer helper headers.  This source-bound dependency recovery changes no
workload source or runtime semantics.  Because CFD uses constant-memory setup,
it remains `INPUT_READY/RUNTIME_AUDIT_CONSTANT`, not `BUILD_READY`: a real
V100 checker, frozen launch/input contract, and dynamic trace-ordering audit
are still required.  Paper-10 capture priority and all readiness counts are
unchanged.

## Live audit update (2026-09-06)

The natural-terminal BICG stats-light A0/A1 comparisons and the required
independent same-placement IO confirmation are complete. Base, repaired
PAPER_IO, and repaired PAPER_OO strict-parse and match exactly in every
parser-visible scientific field, including final cycles/instructions,
DTC lifecycle/accounting, and parser-visible traffic. The same-placement
confirmation again found zero differing metrics and natural zero drain.
A1 (`gpgpu_runtime_stat=500000`, observer-overlay SHA
`2c2a6a272c129243626617e2b80ded798b30ccb09377d07a2ca453209074074e`) is now
adopted for **future, not-yet-launched** formal triplets only. Existing valid
A0 rows are neither rerun nor relabelled, and no future triplet may mix A0/A1.
See `m5/handoffs/M5_STATS_LIGHT_A1_TERMINAL_EQUIVALENCE.md`.

The repaired BICG Base replay has now naturally terminated (exit zero), strict
parsed, and reclosed the same-bundle repaired-Core T2 triplet with IO/OO.
`review_packs/M5_0BT_T2_BICG/` is now bound to Core `15cfa76e...`; the
pre-repair T2 remains diagnostic only.  The ATAX Base/IO/OO recovery triplet
remains live, so the lower-create repair gate is not yet PASS; repaired MVT
replacement and repaired GESUMMV T3 remain correctly gated by its required
natural-terminal/parser/drain closure.

The source-script capture route has been recovered and read non-invasively.
SpMV is `ARCHIVE_PASS`, has copyback SHA and local immutable validation PASS,
and is bound to exact source/input/tracer identity in
`m5/handoffs/M5_0BT_SPMV_CAPTURE_CLOSEOUT.md`.  2MM has completed its
capture/postprocess phase and is currently controller `ARCHIVE_PENDING`; it
has no archive/transfer/result claim yet. No production capture was restarted
or duplicated during the reachability recovery.

The newly immutable SpMV bundle has entered the repaired-Core SIM_HOST pool as
three isolated `PRECOMPUTED_PENDING_STAGE_ACCEPTANCE` Base/IO/OO rows.  All
three have loaded the first immutable `.traceg` through the trace frontend,
with empty stderr; no formal-result claim is made before their own natural
terminal/parser/accounting closure.

## Current capture-storage authority (2026-09-06)

SYR2K has reached remote ARCHIVE_PASS with an exact 57,694,970,930-byte
working bundle, exceeding the old 55,353,177,980-byte 2DConv-based aggregate
projection. Future capture uses the researcher-authorized serial-streaming
admission floor of 61,516,599,357 bytes: the maximum measured complete SYR2K
bundle + archive + measurable scratch footprint. The old ten-bundle/twofold
multiplier is superseded because proof-bound streaming offload is now required.
SYR2K now has copyback SHA and local immutable validation PASS: its remote
archive SHA, local resumed archive SHA, unpacked internal sums and capture
bundle have closed under receipt
`6a6b590dc7d05a10d85ab30b37c6350092aba981c65be82249c6374e3e825513`.
The proof-bound remote working-bundle eviction and fresh live gate have since
passed; only the redundant remote SYR2K working bundle was eligible, while its
archive/provenance remain retained. The ordered SpMV -> 2MM queue has been
restarted, but no SpMV capture/archive/transfer/result is claimed yet. 2MM is
HEAVY_SIZE_UNKNOWN and may start only under the recalibrated gate. See
docs/dtc_l1/m5/handoffs/M5_0BT_SYR2K_HEAVY_STORAGE_RECALIBRATION.md.

Status: M5.0BT T1, BICG/2DConv storage admission, immutable-store copybacks,
and T2 BICG same-bundle Base/IO/OO replay qualification PASS.  T3 GESUMMV
same-bundle Base/IO/OO formal replay is ACTIVE; `CAPTURE_AND_REPLAY_PIPELINED`.
**New Core recovery active:** four precomputed ATAX/MVT IO/OO rows aborted
at the bounded lower-create queue assertion.  Core
`15cfa76ed3b041fa5b78161dfba02bae1e6d7fe9` replaces that post-allocation
abort with pre-allocation retriable backpressure and retains all correctness
assertions.  Exact-bundle ATAX IO/OO recovery replays are active under the
new runtime; neither they nor any old-Core row is a formal result yet.
The existing BICG T2 and live GESUMMV T3 replays use pre-repair Core
`12097864...`; preserve them to natural termination, but treat them as
diagnostic/mechanism anchors.  Same-bundle triplets under `15cfa76e...` are
required before a repaired-identity T2/T3 formal acceptance claim.

## Live scheduling update

### Concurrent three-track checkpoint

- **Track A — T3 (pre-repair diagnostic):** GESUMMV Base/IO/OO run as
  independent sessions on the
  immutable `d8cf9b57...` bundle under the frozen 80-SM/cap-10240/ratio-zero
  identities.  The latest non-invasive counter sample was Base
  `2,446,000` cycles / `5,539,040` instructions, IO `1,809,000` /
  `24,494,688`, and OO `1,864,000` / `22,761,472`; all three processes were
  CPU-active with no fatal/assert/deadlock signature (the only `deadlock`
  text is the printed enabled-config option).  They must naturally terminate.
  Because their Core predates the lower-create-queue repair, they cannot close
  repaired-identity T3 and a new-Core same-bundle replacement triplet remains
  required.
- **Track B — V100 capture:** ATAX is `ARCHIVE_PASS` remotely and locally
  transfer-verified: archive SHA-256
  `4db328affd8a81d444bca1bc034110e1e51458fbce6ab901078a101c6beadff3`,
  internal sums PASS, controller `valid_bundle()` PASS, and checker PASS with
  zero mismatches.  It is a T4-eligible payload, not a formal performance
  result.  GEMVER has remote checker/archival PASS.  MVT has now completed
  checker/archive/copyback: archive SHA-256
  `6c537caf1e110c3804bdc943211078565580f88d9ed85ac8dfa12d685964f270`,
  bundle ID `8b96abe81eed02a614014401cb074ff9d57abd3dc6ba72260167050679ca4f3a`,
  internal sums PASS, and `valid_bundle()` PASS at preserved local root
  `/workspace/m5-trace-immutable/mvt/mvt/mvt`.  SYRK has since reached
  `ARCHIVE_PASS` with bundle
  `66957eacdb8435c12c097631460450923adf9ed39bf8bfe37464cdf868c9a09b` and
  archive SHA-256
  `b82e9ef0310778f8e3493ca555532a636a08f84e466d9e733ebea53a11b3b6a3`;
  SIM_HOST copyback is active but local immutable validation is not yet a
  claim.  The subsequent SYR2K launch was refused before capture by the
  controller's fail-closed heterogeneous-storage projection gate
  (`RuntimeError: unsafe projected heterogeneous trace storage`): no SYR2K
  state, trace, or capture process was created.  Researcher-authorized,
  provenance-preserving R1/R2 reclamation then removed only regenerable
  capture scratch and one checker-failed, non-candidate GESUMMV raw attempt;
  its compact logs/provenance were retained.  The unchanged gate subsequently
  passed (`55,478,362,112` free bytes versus `55,353,177,980` projected), and
  the single SYR2K controller resumed under the capture lock.  While SYR2K
  was actively capturing, the proof-bound R3 controller operation offloaded
  only the redundant remote ATAX working bundle (5,806,756,882 bytes); its
  remote archive and all verified SIM_HOST artifacts remain preserved.  The
  post-R3 unchanged gate passed with 59,432,751,104 free bytes.  See
  `m5/handoffs/M5_0BT_AUTODL_SPACE_RECLAMATION.md`.  None of these capture
  bundles is a formal result.  As SYR2K's live trace later consumed the
  start-gate margin, R4 used the same proof-bound controller action for MVT:
  only its redundant 5,777,441,032-byte remote working bundle was removed,
  after remote/local archive SHA and local immutable manifest validation
  matched.  Its remote archive and SIM_HOST immutable payload remain intact;
  the post-R4 unchanged gate passed with 59,907,649,536 free bytes.  SYR2K
  remained active throughout.  R5 then proof-bound-offloaded only GEMVER's
  redundant 2,647,569,402-byte remote working bundle after the same archive
  and local immutable checks; its archive and local payload remain preserved,
  and the unmodified gate passed with 59,551,346,688 free bytes.
- **Track C — SIM_HOST statistics-light A/B:** the initial BICG
  same-trace/same-binary/80-SM/cap-10240/PAPER_BASE cutoff round established
  that `gpgpu_max_cycle=2000000` is not a valid DTC observation boundary: it
  bypasses normal drain and correctly fails the terminal lifecycle assertion.
  Those outputs remain diagnostic-only.  A separately isolated natural-
  terminal A0--A3 round is active.  A0 is current observer
  settings; A1 sparse runtime CSV; A2 additionally suppresses the final PTX
  line report; A3 additionally disables generic memlatency observer stats.
  This does not alter a formal run or registry.  See
  `m5/handoffs/M5_SIM_HOST_STATS_LIGHT_AUDIT.md`; no candidate is adopted
  until terminal counter equivalence and a controlled confirmation pass.

- **Pipelined returned-trace acquisition:** researcher authorization permits
  independent replay acquisition before T3/M5.0BT logical PASS.  The fully
  validated ATAX, GEMVER and MVT immutable payloads each have a Base/IO/OO
  replay on the unchanged frozen formal configuration, recorded as
  `PRECOMPUTED_PENDING_STAGE_ACCEPTANCE` in
  `m5/handoffs/M5_0BT_PRECOMPUTED_REPLAY_QUEUE.md`.  These live rows are not
  a stage result and must close all terminal/parser/accounting gates before
  later exact-identity reuse.

- **Lower-create queue recovery:** the frozen 80-SM/cap-10240 pool exposed
  the same source-reachable IO/OO assertion for ATAX and MVT.  The failed
  evidence is preserved, excluded from the registry, and documented in
  `implementation/M5_PRECOMPUTED_LOWER_CREATE_QUEUE_FAILURE.md`.  The Core
  repair exports explicit queue-full stall counters, passes the three DTC
  CTests in an isolated Release build, and has an isolated trace frontend
  runtime.  ATAX IO (PID `1045897`) and OO (PID `1045896`) now replay the same
  immutable bundle/config in a separate recovery namespace.  At 101 s both
  exceeded their old 83.81 s / 84.96 s abort window with empty stderr and no
  assertion/fatal/deadlock/error signature.  They must still close natural-
  terminal/parser/accounting gates before any post-repair formal reuse; MVT
  remains queued behind that evidence.  This is a HARD recovery gate, not a
  stage advance.

- **Repaired-identity replay pool:** isolated runtimes built from Core
  `15cfa76e...` now run ATAX Base/IO/OO and BICG Base/IO/OO on their existing
  immutable bundles/configs.  ATAX uses Framework `2bb015a8...`; BICG uses
  Framework `dc7836c4...`; each triplet is internally source-identical.  The
  BICG triplet is the post-repair T2 replacement, not a duplicate formal result.  The
  dynamically calibrated pool has 18 live simulator workers, including the
  four stats-light diagnostics; MemAvailable remains about 101 GiB with zero
  swap I/O, so further dispatch is frozen pending a natural exit or fresh
  calibration.  See `m5/handoffs/M5_REPAIRED_CORE_REPLAY_POOL.md`.

- BICG Base remains a verified trace-driven replay, not a PTX/execution-driven
  payload: its live argv uses immutable BICG `kernelslist.g`, loads both
  ordered `.traceg` invocations through the trace frontend, and has no trace
  corruption/fatal/assert/deadlock/output-mismatch signature. Its immutable
  bundle ID is `ae7f9dbd07e2da471b6e218d160b7446c710872cd85797e54bd58b42708e8a33`.
- A 90-second read-only sample recorded `33,182,550 -> 33,316,550` current
  kernel cycles and `54,363,616 -> 54,570,624` instructions: about 1,489
  cycles/s and 2,300 instructions/s. Classification:
  `TRACE_REPLAY_HEALTHY_PROGRESSING`. Base subsequently naturally terminated
  and strict-parsed at `50,303,549` cycles / `158,601,216` instructions; the
  full same-bundle BICG Base/IO/OO qualification is now T2 PASS. Its review
  pack is `review_packs/M5_0BT_T2_BICG/`; T3 is the next logical replay gate.
- Physical V100 capture now pipelines independently. The first GESUMMV
  (`gesu`) attempt is preserved `RETRY_READY`: its checker found 1,964
  mismatches caused by the pinned CUDA source copying uninitialized host
  `tmp`/`y` into additive device accumulators. A source-copy-only repair is
  hash-constrained to those two zero initializations and records both source
  hashes/replacements in capture provenance; the frozen source and failed raw
  attempt are untouched. Its corrected replacement capture now has checker,
  immutable-bundle/archive, copyback-SHA and local bundle-revalidation PASS;
  it is a T3 payload, not yet a formal result. Framework
  `14be71c7968f0fb5bc1e021cf40eda41d8314171` corrects the controller's
  heavy-pilot admission formula and passes its no-GPU regressions. This is a
  capture-controller repair only; it changes no trace bundle, replay config,
  Core behavior, or formal result.
- See `m5/handoffs/M5_0BT_CAPTURE_REPLAY_PIPELINE.md`. Capture ahead of replay
  is a scheduling admission only; M5.0C remains prohibited until full M5.0BT
  acceptance.

## Current authoritative state

### Throughput checkpoint (2026-09-06)

- Researcher-authorized worker recovery preserved and then gracefully retired
  stats-light A2/A3 and the old-Core GESUMMV Base/IO/OO diagnostics.  The
  exact preserved namespaces, pre-signal evidence, classifications and PGIDs
  are recorded in `m5/handoffs/M5_SIM_HOST_STATS_LIGHT_AUDIT.md` and
  `m5/handoffs/M5_REPAIRED_CORE_REPLAY_POOL.md`.  No repaired-Core formal
  candidate was signaled, no raw evidence was deleted, and no `SIGKILL` was
  required.
- The real container CPU boundary is a 384-core cgroup quota with cpuset
  `0-511`, not an 18-core allocation.  Eighteen was a conservative shared-host
  scheduling limit.  After retirement, BICG repaired PAPER_IO/PAPER_OO A1
  natural-terminal observer-only confirmations started on dedicated CPUs 46
  and 47 (`1512229`, `1512240`); they retain the immutable BICG trace, Core
  `15cfa76e...`, 80-SM/cap10240/ratio-zero model and differ only by runtime
  statistics cadence.  They are not adoption/formal results pending full
  terminal equivalence.
- ATAX repaired Base/IO/OO remain live and have only exceeded the historical
  abort window; they have not completed the HARD terminal/parser/drain/lower
  accounting gate.  Consequently MVT IO/OO and repaired GESUMMV T3 are ready
  for priority dispatch but remain correctly gated, rather than being launched
  under an unqualified repaired runtime.

### Capture-storage recovery R6 (2026-09-06)

- SYRK reached archive/copyback/local-immutable PASS and was then reclaimed
  only through the proof-bound controller path.  `bundles/syrk` (27,998,390,213
  bytes) was removed; its remote archive, local immutable payload and evidence
  were preserved.  Free space increased from the last pre-controller observed
  54,673,100,800 bytes to 82,369,568,768 bytes while SYR2K continued capture.
  See `m5/handoffs/M5_0BT_AUTODL_SPACE_RECLAMATION.md` and remote
  `reclamation/R6_syrk_offload_evict.json`.
- The AutoDL control plane is again readable through the live capture-host
  route.  SYR2K is in its natural post-GPU trace-processing phase:
  application checker PASS (zero mismatches), raw trace present, and the
  controller remains live while its CPU postprocessor runs.  Its state is
  still `CAPTURING`, so neither `ARCHIVE_PASS` nor copyback is claimed.
- The next exact SpMV payload's canonical matrix/vector/reference identities
  and clean wrapper `de9cf429...` / tree `5b8b3a8...` remain verified.  Both
  SIM_HOST source bundles were copied to an isolated AutoDL staging area with
  SHA-256 and complete-history bundle verification; a clean detached
  `parboil@4e0fc548...` / tree `0bc8944...` checkout now occupies the source
  path consumed by the existing queue supervisor.  This replaces the
  prolonged non-candidate public clone without changing any capture artifact.
  The supervisor is now fail-closed only on SYR2K `ARCHIVE_PASS`, storage, and
  the capture lock before starting SpMV, then applies the same ordering to
  2MM.  See `m5/handoffs/M5_0BT_SPMV_SOURCE_TRANSFER_READY.md`.
- 2MM CPU-side preparation and isolated AutoDL source-tar transfer are both
  verified: clean `polybenchGpu@5584aaa7...` source/header hashes,
  deterministic tar identity, sm70 build, source checker and dimensions are
  frozen in `m5/handoffs/M5_0BT_2MM_CAPTURE_READY.md`.  It remains `PENDING`
  and may start only after SpMV reaches its safe archive state and the normal
  lock/storage gates pass.

### Live throughput checkpoint (2026-09-06T12:19+08:00)

- The repaired-Core BICG PAPER_OO A0 replay naturally ended with exit status
  zero and strict parser/drain/accounting PASS in its isolated output
  namespace.  It records 8,764,792 cycles / 158,601,216 instructions, lower
  create/issue/response `17,827,090/17,827,090/17,827,090`, dependencies
  `18,350,080/18,350,080`, and final OO PIB/inflight/active-ref/lower state
  all zero.  It is only a `POST_REPAIR_T2_REPLAY_CANDIDATE`: repaired BICG
  Base/IO and the required IO/OO A1 equivalence confirmations are still live,
  so no T2 re-close, stats-light adoption, or formal registry update occurs.
- The repaired-Core BICG PAPER_IO A0 member has now also naturally ended and
  strict-parsed: 9,324,397 cycles / 158,601,216 instructions, lower
  create/issue/response `17,823,985/17,823,985/17,823,985`, dependencies
  `18,350,080/18,350,080`, and final IO inflight/PIB/lower state all zero.
  No assertion, fatal, output mismatch, or non-config deadlock text was
  observed.  This leaves only repaired BICG Base A0 before same-bundle T2
  triplet reconciliation; the IO/OO A1 stats-light confirmations remain live.
- **Current-pool correction (2026-09-06T12:33+08:00):** after the BICG IO A0
  terminal transition, 13 (not 14) isolated M5 simulator processes remain
  live.  The repaired BICG IO/OO A0 rows are recorded in the replay-job
  manifest as `POST_REPAIR_T2_REPLAY_CANDIDATE`; they are not registered
  formal results and still await Base A0 plus same-mode A1 equivalence.
- At the 12:19 historical snapshot, fourteen isolated M5 simulator processes
  remained active and each continued
  to accrue near-one-core CPU time.  The dynamic limit remains `N_safe=18`;
  the unfilled capacity is intentionally protected until repaired ATAX
  Base/IO/OO close their natural-terminal/parser/drain gate, after which MVT
  IO/OO and repaired GESUMMV receive priority.  The container has cpuset
  `0-511` and a non-throttling 384-core `cpu.max` quota, but the shared host
  load is about 440 and does not support increasing concurrency from topology
  alone.
- Two non-invasive V100 SSH probes were refused during this checkpoint.  No
  remote process, queue, archive, or state file was touched, and this is not
  classified as a capture failure.  Continue local replays and resume the
  existing fail-closed `SYR2K -> SpMV -> 2MM` capture pipeline only after the
  host is reachable and its retained controller state can be read.

### Extended E1 offline provenance progress (2026-09-06)

- The six selected Parboil input sets were byte-hash and Git-blob revalidated
  in clean `parboil@4e0fc548...`; the six selected checker identities remain
  source-pinned.  The Python-3 source-predicate adapter recompiled and passed
  all six accepted/mismatch fixtures.  This closes local input/checker drift
  evidence only: CUDA builds, PTX, generated output references/smokes, payload
  eligibility and all Rodinia input recovery remain pending.  No Extended
  simulation, trace capture, result registration, or E2 launch occurred.
- The eight selected CUDA SDK 4.2 source files were independently rehashed
  straight from Git commit `b059fdae...`; all match the recorded E1 source
  identities.  This is source-only provenance confirmation: executable/PTX
  artifact revalidation, deterministic runtime I/O, source-defined smoke and
  M5.2 anchor recheck remain required.
- A conservative static source audit now classifies the six Parboil rows
  before any V100 work: BFS (atomics/textures/global barrier), CUTCP
  (stream/constant memory), Histo (atomics), MRI-Q (constant memory), and
  SAD (textures) require workload-local runtime semantic audits; Stencil is a
  static trace candidate only.  None is yet `TRACE_CAPTURE_READY`, no feature
  is presumed unsupported, and the per-row readiness table remains the
  capture scheduling authority.  See
  `m5/extended20/M5_E1_PARBOIL_STATIC_TRACE_FEATURE_AUDIT.md` and
  `m5/handoffs/M5_E1_V100_CAPTURE_READINESS.md`.
- The selected Rodinia 3.1 CUDA source scan likewise identifies CFD's
  constant-memory transfer path for a runtime audit; BTree, DWT2D, Gaussian,
  Hotspot1 and LUD are static candidates only.  Their missing deterministic
  inputs/checkers and all clean V100/sm70 builds still prohibit capture.  See
  `m5/extended20/M5_E1_RODINIA_STATIC_TRACE_FEATURE_AUDIT.md`.
- The CUDA SDK 4.2 static screen identifies convolutionSeparable's
  constant-memory transfer path; the other seven selected rows are static
  candidates only.  All eight already have recorded local CUDA-11.8/sm70
  build/PTX preflights, but no SDK row can capture before its own real-V100
  output smoke/checker, input/launch/runtime freeze and dynamic contract.  See
  `m5/extended20/M5_E1_CUDA_SDK_STATIC_TRACE_FEATURE_AUDIT.md`.
- The source-recorded Rodinia 3.1 data archive is now archive-hashed and only
  the approved input members have been materialized in an isolated local E1
  namespace.  CFD, BTree, DWT2D and Hotspot now have exact launcher-input
  hashes; LUD's source-generated `-s 256` contract is distinguished from a
  data file.  Gaussian has several source-recorded candidates and remains
  deliberately unfrozen.  No V100 capture, build, trace or formal result was
  started.  See `extended20/RODINIA_PARBOIL_E1_SOURCE_AUDIT.md`.

- One persistent Goal: docs/dtc_l1/m5/M5_TRACE_TO_FINAL_SINGLE_GOAL_CONTRACT.md.
- M5.0BT is active and gates M5.0C. No M5.0C, Extended E2, graphics work, or
  capture-host rental/start is authorized by this report.
- Formal platform is 80 SM, global lower cap 10240 (128 credits/SM), and
  ratio-zero. The 80-SM/cap-256 combination is historical diagnostic-only.
- M5.0BT has a workload-specific, source-pinned CUDA-11.8/sm70 capture
  controller, immutable bundle validation, external archive/transfer states,
  non-bypassable BICG-based storage admission, and SIM_HOST orchestrator.
- The two remote checkouts are non-interchangeable: current M5 control checkout
  runs the command; detached 0db04452ec1c47630e4b08002067d82c6811e243
  supplies tracer sources only.
- The provisioned capture host passed V100/CC7.0, CUDA 11.8, toolchain,
  writable-data-volume and pinned-source preflight. M5-0BT-001 was repaired
  before CUDA build; M5-0BT-002 then found an unrelated root-Makefile legacy
  tool after the required trace tool/postprocessor compiled. Its scoped-build
  repair and regression contract now pass. Retry-4 completed that build but
  exposed M5-0BT-003: the host identity probe used incorrect CUDA Runtime UUID
  APIs. The compact Driver-API UUID adapter passed isolated CUDA-11.8/V100
  revalidation (properties, Driver UUID and CC 7.0 agree with `nvidia-smi`).
  No application, raw trace, immutable bundle or formal result has been
  created. Retry-5 reached the BICG CUDA build and exposed M5-0BT-004: its
  selected-workload loop propagated a false final predicate as status 1 after
  a successful `nvcc` build. The explicit-success repair passed an exact V100
  BICG build retest. Frozen source, CUDA 11.8 and sm70 build contract are
  unchanged; each fresh build's executable SHA is captured as provenance.
  Retry-6 then loaded NVBit on V100 but found the installed CUDA-11.8
  `nvdisasm` absent from the application PATH (M5-0BT-005). Retry-7's PATH
  repair passed: the BICG checker passed and full raw traces were captured.
  Its postprocess exposed M5-0BT-006; retry-8 passed that legacy-layout
  adapter, application checker, raw capture and `.traceg` postprocess. It then
  exposed M5-0BT-007; its CSV repair passed on resume. Strict mapping then
  exposed M5-0BT-008; its line-preserving repair also passed. Finalization
  reached record construction and exposed M5-0BT-009: it had not materialized
  the validated manifest files before hashing them. Its write-before-hash
  repair passed: retry-8 is now an immutable, archived BICG T1 bundle. See
  `m5/handoffs/M5_0BT_BICG_T1_REVIEW.md`. The archive was SHA-verified after
  copyback, unpacked once into the immutable replay store, and internally
  revalidated against its bundle sums. The BICG admission projects
  47,591,571,552 bytes against 104,537,268,224 measured free bytes, but is
  provisional because BICG's two small-grid invocations do not bound 2DConv.
  The required exact 2DConv 65,536-CTA heavy pilot now passes its hardware
  checker, archive/copyback SHA chain and internal immutable-store sum check.
  Its conservative ten-workload/twofold-reserve projection is 55,353,177,980
  bytes below 101,566,291,968 measured free bytes, admitting the remaining
  sequential Paper queue. See `m5/handoffs/M5_0BT_BICG_ADMISSION_COPYBACK.md`
  and `m5/handoffs/M5_0BT_2DCONV_HEAVY_ADMISSION.md`.

## Required next action after a V100 host is supplied

Complete natural-terminal GESUMMV T3 qualification while the exact Paper
capture queue continues independently.  Then obtain/qualify the remaining
Paper trace bundles.  No M5.0C transition is authorized.

## HISTORICAL / SUPERSEDED — DO NOT EXECUTE

The prior execution-driven M5.0B cap-256 workload campaigns, their former
natural-terminal wait, and their five terminated recovery jobs are preserved
only as source/provenance and mechanism-validation evidence. They are not
formal performance inputs and impose no active transition condition.
