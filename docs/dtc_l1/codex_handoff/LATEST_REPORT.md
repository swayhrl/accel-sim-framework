# Latest Codex Report

Stage: M5.0BT exact trace capture and qualification.

## Current capture-storage authority (2026-09-06)

SYR2K has reached remote ARCHIVE_PASS with an exact 57,694,970,930-byte
working bundle, exceeding the old 55,353,177,980-byte 2DConv-based aggregate
projection. Future capture uses the researcher-authorized serial-streaming
admission floor of 61,516,599,357 bytes: the maximum measured complete SYR2K
bundle + archive + measurable scratch footprint. The old ten-bundle/twofold
multiplier is superseded because proof-bound streaming offload is now required.
SYR2K local immutable validation, remote eviction and live-gate PASS remain
pending; SpMV has not started. 2MM is HEAVY_SIZE_UNKNOWN and may start only
under the recalibrated gate. See
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
  candidates only.  Historical sm52 builds remain provenance-only and no SDK
  row can capture before its own clean V100/sm70 build, checker/input freeze
  and dynamic contract.  See
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
