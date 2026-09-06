# Latest Codex Report

Stage: M5.0BT exact trace capture and qualification.

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
  `/workspace/m5-trace-immutable/mvt/mvt/mvt`.  SYRK holds the single V100
  capture lock; none of these capture bundles is a formal result.
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

- **Repaired-identity replay pool:** a new isolated runtime built from Core
  `15cfa76e...` and Framework `dc7836c4...` now runs ATAX Base/IO/OO and BICG
  Base/IO/OO on their existing immutable bundles/configs.  The BICG triplet
  is the post-repair T2 replacement, not a duplicate formal result.  The
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
