# M5 trace-driven downstream stage review

Status: **CHATGPT/RESEARCHER REVIEW DRAFT — ISOLATED REVIEW BRANCH; DO NOT TREAT AS ACTIVE COMPUTE AUTHORITY YET**

Review branch base: `hrl/decoupled-l1-exp-m5-v0@287bc5b46849963857515d567deb9c1372bb2165`.

Purpose: review the already-approved downstream M5.0C–M5.12 and Extended-20 contracts against the new researcher direction to stop obsolete `80 SM + cap 256` execution-driven recovery, capture exact V100/NVBit traces, qualify the common DTC timing path, and then use trace-driven simulation under the frozen `80 SM + cap 10240` platform if M5.0BT passes.

This file intentionally does **not** edit `LATEST_REPORT.md`, the active M5.0BT handoff, or other compute-window mutable files while Codex owns the active worktree. Integrate the applicable amendments only after the active M5.0BT authority/capture handoff is reviewed.

---

## 1. Review verdict

The existing downstream scientific structure is sound:

`M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3 -> M5.4 -> M5.5 -> M5.6`

plus:

`M5.E1 -> M5.E2 -> M5.E3 -> M5.COMPUTE_FREEZE -> M5.12`.

However several current contracts are stale for the intended trace-driven campaign. They still encode one or more of:

- `8 SM` paper-mode assumptions;
- global lower cap `256`;
- PTX/execution-driven payload identity;
- simulator-side application-output checking as a requirement for every formal replay;
- E2 job identity keyed only by PTX;
- sequential data acquisition that creates avoidable wall-clock delay;
- no explicit trace-store / trace-I/O resource policy.

These must be reconciled before formal trace-driven Figure 4.x data are admitted.

The following items are **HARD downstream requirements**, not optional cleanup:

1. exact trace identity must replace PTX identity as the formal execution payload after `TRACE_FORMAL_PATH_VALID`;
2. the Base/IO/OO formal config family must explicitly carry `80 SM + cap 10240`, not rely on the Core default 256;
3. hardware-capture correctness and simulator-replay correctness must be separated;
4. workload launch geometry versus the 80-SM platform must be measured and reported before M5.0C PASS;
5. Figure 4.7 must retain the frozen per-configured-SM metric but add an active-SM diagnostic when the captured grid underfills 80 SMs;
6. Extended-20 must gain per-workload trace eligibility and exact-trace identities before E2 if trace-driven becomes the common formal path;
7. batch identity and scheduling must become execution-payload-aware (`TRACE` vs approved execution-driven exception).

---

## 2. Authority hierarchy after M5.0BT

Preserve the historical approvals; do not rewrite history as though the old decisions never existed.

After the active Codex window completes M5.0BT preparation, the intended precedence should be:

1. researcher-approved M5.0BT exact-trace recapture/qualification decision;
2. frozen Q2/Q3 platform decision: `80 SM`, `128 credits/SM`, global cap `10240`;
3. M5 v3 parallel-track scheduling and graphics closeout;
4. M5 v1 scientific figure definitions and the experiment matrix, **as amended by the trace transition**;
5. Extended-20 approval and formal matrix, **as amended by the trace transition**.

Old M5.0B cap-256 data remain historical mechanism/workload-recovery evidence only.

Old M5.0BF Q1 `EXECUTION_DRIVEN_REQUIRED` remains valid historical evidence for the state in which no exact trace existed. M5.0BT may supersede only the future execution-path decision after exact trace qualification.

---

## 3. M5.0BT exact trace contract — additions to check during review

The active M5.0BT handoff should be considered incomplete unless it freezes or explicitly schedules all of the following.

### 3.1 Capture build identity

Do **not** require the V100 capture executable SHA to equal the old execution-driven `sm_52` binary SHA.

Instead freeze two distinct identities:

- `RECOVERY_EXEC_BINARY_SHA` / historical PTX identity: workload-recovery evidence only;
- `TRACE_CAPTURE_BINARY_SHA`: the exact binary actually executed on the capture GPU and instrumented by NVBit.

For the preferred V100 capture route, the build recipe should target Volta explicitly (normally `sm_70`) using a pinned CUDA toolchain. Source, input, command line, algorithm, and output semantics must remain the approved canonical workload; the generated capture binary becomes a new frozen artifact identity.

Record at least:

- source repo/commit/path/hash;
- build script hash;
- `nvcc --version`;
- CUDA toolkit path/version;
- `-arch` / code-generation options;
- executable hash;
- kernel names/ABI observed on hardware;
- input hashes;
- command line/environment;
- output checker and PASS evidence.

### 3.2 Tracer identity

The active Framework `util/tracer_nvbit/install_nvbit.sh` currently pins NVBit `v1.8`. The capture handoff must freeze the exact Framework tracer source SHA and NVBit release/version actually used rather than saying merely "NVBit".

Freeze:

- Framework tracer commit/SHA;
- `tracer_tool.so` SHA-256;
- NVBit version;
- trace-format/parser version;
- post-processing binary/script SHA;
- capture GPU model and compute capability;
- driver version;
- CUDA runtime/toolkit version.

### 3.3 Complete trace-set identity

A formal trace is not identified by `kernelslist.g` alone.

Create a deterministic trace-set/root identity over at least:

- `kernelslist`;
- `kernelslist.g`;
- every required raw `kernel-*.trace` if retained as provenance;
- every replayed `kernel-*.traceg`;
- `stats.csv`;
- capture correctness log;
- capture environment record.

Recommended fields:

- `TRACE_BUNDLE_ID`;
- `TRACE_MANIFEST_SHA256`;
- `KERNELSLIST_G_SHA256`;
- `TRACEG_SET_SHA256` (stable ordered manifest/root hash);
- `RAW_TRACE_SET_SHA256` where raw traces are archived.

Base/IO/OO formal runs of one workload must reference the **same immutable trace bundle**.

### 3.4 Full execution only

No fractional CTA, kernel subset, or shortened dynamic range is formal Paper-10 evidence unless explicitly approved for a directed diagnostic.

Formal capture requires every relevant kernel invocation and the complete approved workload command/input. `DYNAMIC_KERNEL_RANGE` is allowed only for discovery/diagnostic use unless it provably still covers the complete formal workload.

### 3.5 Trace storage budget

Before capturing the whole set, record:

- expected/projected dynamic instruction count;
- pilot bytes per traced instruction or empirical trace growth;
- free capture-host storage;
- free replay-host storage;
- archive compression ratio;
- transfer method and checksum verification.

Use a rolling capture/offload policy if needed. Never discover after several workloads that the capture disk cannot hold the remaining exact traces.

Raw traces may be archived off the hot simulation filesystem after an archive and its hashes are independently verified; formal replay requires the immutable processed trace set, not duplicated per-job copies.

---

## 4. New formal result identity contract

The current M5 matrix and batch policy key formal results on PTX-oriented tuples. After M5.0BT `TRACE_FORMAL_PATH_VALID`, the common formal tuple should become payload-aware.

Recommended canonical tuple:

`{core_sha, framework_sha, config_sha256, execution_payload_kind, workload_source_sha, input_sha256, payload_identity, parser_schema}`

where:

### TRACE payload

`execution_payload_kind = TRACE`

and `payload_identity` includes at least:

`{trace_bundle_id, trace_manifest_sha256, kernelslist_g_sha256, traceg_set_sha256, tracer_sha, trace_format_version}`.

Capture binary/toolchain/GPU/driver provenance belongs in the workload trace manifest and is transitively bound by `trace_manifest_sha256`.

### Execution-driven exception

`execution_payload_kind = PTX_EXEC`

and `payload_identity` includes the existing executable/PTX/runtime identities.

Never compare Base/IO/OO inside a formal triplet if they use different payload kinds or different trace bundles.

This change must propagate to:

- result registry;
- `JOB_MANIFEST.tsv`;
- `RAW_LOG_INDEX.tsv`;
- review-pack `FORMAL_ANCHOR.md`;
- M5/E2 job manifest template;
- parser output metadata.

---

## 5. Correctness contract under trace replay

Current documents often require "application output/self-check" from each simulator run. That is appropriate for execution-driven PTX but must be split for trace-driven simulation.

### Capture-time application correctness — HARD

On the V100 capture host require:

- natural application exit;
- exact approved input/command;
- source-defined checker/reference PASS;
- complete trace generation/post-processing;
- no tracer error/fatal;
- trace kernel/invocation inventory consistent with the workload.

Status field example:

`CAPTURE_APP_CORRECTNESS_PASS`.

### Replay-time simulator correctness — HARD

Trace replay must require:

- immutable trace identity match;
- parser success;
- all expected kernel records consumed;
- no simulator fatal/assert/deadlock except an explicitly expected M5.4 resource deadlock;
- request/dependency/PIB/lower/inflight/ref conservation and final drain;
- Base/IO/OO use identical trace payload;
- mode-specific DTC counters exercise the expected path.

Do not invent an application-output value from trace replay if the trace simulator does not functionally reconstruct host output.

Review packs should carry both capture-time correctness evidence and replay-time simulator correctness evidence.

---

## 6. M5.0C — platform/config fidelity amendments

The existing M5.0C definition is mostly correct but requires the following explicit additions.

### 6.1 Formal config family

Create/freeze a new Base/IO/OO family in which every unrelated byte is identical and every mode has an **explicit** lower-cap option:

- 80 SM;
- global lower cap = 10240;
- ratio-zero policy;
- 16 KiB Base/logical geometry as appropriate;
- same L2/MC/NoC/DRAM platform;
- only DTC-mode/mechanism-specific approved fields differ.

Do not reuse `PAPER_IO_16KB.config` / `PAPER_OO_16KB.config` as formal simply because they are old named configs: those files currently omit an explicit lower-cap override and therefore inherit the Core default 256.

A diagnostic BF Base config is not by itself a three-mode formal config family.

### 6.2 Execution-path freeze

M5.0C handoff must state explicitly:

- `FORMAL_EXECUTION_PAYLOAD_KIND`;
- trace frontend/parser SHA;
- trace bundle manifest version;
- runner command shape;
- trace store root policy;
- execution-driven exception policy if any.

### 6.3 Launch geometry / 80-SM utilization audit — HARD

This is the largest downstream fidelity gap not fully resolved by the existing BF platform audit.

For every Paper-10 exact captured workload record:

- every kernel `gridDim` and `blockDim`;
- total CTA count;
- number/fraction of configured 80 SMs that can receive at least one CTA in each kernel;
- approximate CTA waves relative to 80 SMs;
- occupancy/resource limits where available;
- whether the workload is `FULL_80SM`, `PARTIAL_80SM`, or `THESIS_2SM_FULL_ONLY` for the relevant kernels.

The archived trace audit already demonstrates why this is necessary: historical BICG/GESUMMV traces had only a 16-CTA grid for their main kernels, whereas the formal simulator platform is 80 SM. Exact recapture must measure the current launch rather than assume full utilization.

Do **not** silently change source/input/block geometry merely to fill 80 SM. If an approved canonical workload underfills 80 SM, preserve it and classify the platform difference. Any deliberate workload-scale change is a researcher decision and must remain pre-performance.

### 6.4 Downstream provisioning interpretation

Report native NoC/L2/DRAM pressure both globally and relative to the number of actually active/request-generating SMs. An 80-SM platform with a 16-CTA kernel is materially less loaded downstream than an 80-SM fully populated kernel; that fact must not be hidden by the platform label.

---

## 7. M5.0D — metrics/instrumentation amendments

The existing Figure-4.2 and Figure-4.7 definitions should remain scientifically frozen, but add trace-aware audit fields.

### 7.1 Figure 4.7

Retain the approved formal metric:

`avg_concurrent_misses_per_sm = sum(live_miss) / (configured_num_sm * sampled_kernel_cycles)`.

Do not silently change its denominator after seeing workload occupancy.

Add mandatory diagnostics:

- `active_sm_count_cycle_sum` / active-SM sample cycles if feasible;
- `avg_concurrent_misses_per_active_sm`;
- active-SM fraction;
- CTA waves / occupancy class from capture manifest.

Reason: an underfilled 80-SM grid can mechanically dilute the formal per-configured-SM value even when active SMs experience strong miss concurrency. The diagnostic prevents incorrect causal conclusions without rewriting the frozen formal metric.

If implementing active-SM cycle counters would alter timing or requires invasive Core work, a source-backed static/dynamic CTA-residency proxy is acceptable as DIAGNOSTIC only; the formal metric stays unchanged.

### 7.2 Dynamic-operation identity

For TRACE triplets, freeze trace-level operation/instruction identity from the same trace bundle and require Base/IO/OO to consume the same dynamic trace stream. Keep simulator retired-instruction totals as a sanity field, not the primary source of workload identity.

### 7.3 Output-check fields

Parser schema must distinguish:

- `capture_app_correctness`;
- `trace_identity_status`;
- `replay_accounting_status`;
- `replay_terminal_status`.

Do not overload one `output_pass` boolean across capture and replay.

---

## 8. M5.0E, M5.1 and M5.2 — reduce redundant formal runs

### 8.1 M5.0E pilots may become reusable

Because M5.0E occurs after M5.0C/D, its trace-driven Base/IO/OO pilot rows may be marked `PILOT_FORMAL_REUSABLE` **only if**:

- exact Core/Framework/config/trace/parser identities remain the final M5.1/M5.2 anchor;
- all M5.0E hard acceptance checks pass;
- no behavior/timing or required-counter change occurs afterward.

Otherwise keep them diagnostic and rerun.

### 8.2 M5.1/M5.2 data acquisition overlap

After M5.0E PASS, it is safe to enqueue the full ten-workload Base/IO/OO main matrix under the same frozen anchor rather than waiting for all ten Base jobs to finish before launching every IO/OO job.

Scientific handoff order remains:

`M5.1 PASS -> M5.2 PASS`.

Operational acquisition may overlap:

- Base rows feed Figure 4.2 / M5.1;
- matching IO/OO rows can execute concurrently in isolated jobs;
- M5.2 cannot close until M5.1 has passed and all triplets are valid.

This saves wall clock without changing scientific dependencies.

### 8.3 Main matrix reuse

M5.2 Base rows are the exact M5.1 Base rows. Never rerun a matching Base identity.

M5.2 must pair every triplet with the same `TRACE_BUNDLE_ID` and record trace-level dynamic-operation identity.

---

## 9. M5.3–M5.5 sensitivity execution/reuse plan

These sweeps are scientifically independent after M5.2 freezes the common anchor. Their **simulation acquisition** may run concurrently under separate experiment IDs and worker-pool quotas; handoff/analysis closure can remain M5.3 -> M5.4 -> M5.5 -> M5.6.

Do not serialize hundreds of independent trace replays merely because the analysis chapters are numbered sequentially.

### M5.3 logical sensitivity

Primary DTC family: logical 16/32/64 KiB, physical 80 KiB, IO/OO.

Reuse the 16-KiB IO/OO rows from M5.2 when identities match. Therefore the primary DTC logical sweep requires only the 32/64-KiB new rows after M5.2.

Optional Base capacity control:

- reuse Base 16-KiB rows from M5.1/M5.2;
- run only new Base 32/64-KiB rows.

### M5.4 physical sensitivity

Keep the thesis compute-only points:

`16.5, 24, 32, 40, 48 KiB`, IO/OO, logical 16 KiB.

Expected IO resource deadlock remains a mechanism result, not a trace failure. Deadlock classification must use simulator resource/no-progress evidence, not capture-time behavior or wall-clock timeout.

### M5.5 PIB sensitivity

Keep physical 32 KiB and PIB `32,64,128,192` for IO/OO.

Reuse M5.4's `OO, physical=32KiB, PIB=128` row if every identity matches. Do not rerun it merely because it appears in Figure 4.10.

M5.4's IO 32-KiB row normally uses the IO default PIB=256 and therefore does **not** replace the Figure-4.10 IO-128 normalization row.

### Rough unique-run accounting after reuse

Excluding M5.0E pilots and optional Base logical control:

- M5.2 main matrix: at most 30 rows, with M5.1 Base contained within it;
- M5.3 new DTC rows after 16-KiB reuse: 40;
- M5.4 physical sweep: 100;
- M5.5 new rows after one OO-128/32KiB reuse per workload: about 70.

This is roughly 240 Paper-10 primary/sensitivity replay identities before retries, not counting any M5.0E rows that can be reused. The worker-pool/storage policy therefore matters even after trace-driven acceleration.

---

## 10. Extended-20 trace transition

The current Extended approval/formal matrix/handoff contract are PTX-centric and need a trace-aware amendment before E2.

### 10.1 E1 remains source/build/input formalization

Do not discard already recovered source/executable/PTX evidence. It remains valuable provenance and supports deterministic capture builds.

Add per workload:

- `trace_eligibility`;
- `trace_semantic_risk`;
- `trace_capture_binary_sha`;
- `trace_bundle_id`;
- `trace_manifest_sha`;
- `kernelslist_g_sha`;
- `traceg_set_sha`;
- hardware correctness status;
- capture GPU/toolchain/tracer identity.

### 10.2 Trace eligibility classes

Suggested classes:

- `TRACE_FORMAL_ELIGIBLE` — deterministic source/input path; trace contains semantics needed by DTC timing model;
- `TRACE_ELIGIBLE_WITH_REVIEW` — atomics/order/cache-control or timing-sensitive behavior needs explicit source/trace audit;
- `EXECUTION_DRIVEN_EXCEPTION_REQUIRED` — trace cannot preserve a scientifically material dynamic semantic.

Do not revert all Extended workloads to execution-driven because one row is ineligible. Conversely, do not force trace mode on a timing-dependent atomic/control workload merely for speed.

### 10.3 E2 job manifest

The existing `M5_E2_JOB_MANIFEST_TEMPLATE.tsv` uses `ptx_hash` as the execution payload. Replace/extend it with at least:

`execution_payload_kind | payload_id | trace_bundle_id | trace_manifest_hash | kernelslist_g_hash | traceg_set_hash | ptx_hash_if_exception`.

Every Base/IO/OO triplet must use one common payload kind and exact payload identity.

### 10.4 V100 capture opportunity

If practical, use the Paper-10 V100 rental to capture Extended workloads whose E1 source/input/output contracts are already frozen and trace eligibility is clean, but:

- Paper-10 capture/qualification has priority;
- do not delay Paper-10 waiting for incomplete Rodinia/Parboil E1 rows;
- do not capture a row before its source/input/output contract is deterministic;
- E2 remains blocked until M5.2 regardless of early trace capture.

---

## 11. Parallel batch / trace-store policy amendments

`M5_PARALLEL_BATCH_POLICY.md` should become payload-aware.

### Job identity

Add:

- `execution_payload_kind`;
- trace/payload root identity;
- runner/frontend SHA.

### Trace storage

Use one immutable shared trace store per `TRACE_BUNDLE_ID`. Do not duplicate large trace trees into every output directory.

Simulation output directories remain unique and writable; trace inputs remain read-only.

### I/O-aware concurrency

For trace-driven waves calibrate `N_safe` using not only CPU/RSS but also:

- trace read bandwidth;
- page-cache footprint;
- storage queue pressure;
- trace working-set size;
- free disk space for outputs.

Introduce a scheduling weight such as `TRACE_IO_HEAVY` for very large bundles. Host wall time remains non-scientific, but avoid an avoidable I/O-thrashing worker pool.

### Cleanup

Never delete the only verified formal trace bundle. Large raw capture files may move to verified archival storage; processed formal replay inputs remain hash-addressable and available through compute freeze/review.

---

## 12. M5.6, compute freeze and M5.12 amendments

### M5.6

No scientific change. Add execution-path provenance to every causal classification so a workload-local execution-driven exception is visible rather than mixed silently with trace-driven rows.

### M5.COMPUTE_FREEZE

In addition to existing Core/Framework/config/parser anchors, record:

- formal execution-path policy;
- trace format/tracer/frontend identities;
- Paper-10 trace manifest/root hash;
- Extended trace manifest/root hash or execution-driven exception list;
- formal Base/IO/OO cap-10240 config family hashes;
- immutable trace-store/archive index.

The freeze is incomplete if a reported FORMAL trace row depends on an untracked local path without an immutable hash/archive record.

### M5.12

No graphics reopening is implied. Under the accepted graphics-unavailable closeout, final synthesis should explicitly distinguish:

- Paper-10 trace-driven execution path and capture provenance;
- any Extended workload-local execution-driven exceptions;
- graphics source-backed-unavailable evidence;
- numerical differences from the thesis that can be explained by the modern 80-SM platform, workload underfill, or other documented platform differences.

---

## 13. Critical pre-M5.0C review questions after traces return

These are the main items ChatGPT/researcher should inspect before allowing M5.0C PASS.

1. **Did the V100 capture use the exact approved source/input/command and pass the source-defined checker?**
2. **Was the capture binary explicitly frozen as a new V100/sm70 identity rather than incorrectly required to equal an old sm52 recovery binary?**
3. **Are all required kernels captured, processed and hash-addressed?**
4. **Do BICG/GESUMMV qualification Base/IO/OO runs consume the exact same trace bundle and cleanly drain DTC accounting?**
5. **Does every formal Base/IO/OO config explicitly set cap10240?**
6. **What is each Paper-10 kernel's CTA grid relative to 80 SM?** This must be known before claiming modern-platform full-load behavior.
7. **For underfilled kernels, is Figure-4.7 accompanied by an active-SM diagnostic and is downstream under-provision/over-provision interpretation explicit?**
8. **Are capture correctness and replay correctness separate fields?**
9. **Has the registry/job identity been converted from PTX-only to payload-aware trace identity?**
10. **Is the trace store large enough and immutable enough for the full M5.2–M5.5 replay campaign?**

If items 1–5 fail, M5.0C must not start.

Items 6–7 may reveal a genuine researcher-decision boundary only if the canonical exact workload is so underfilled on 80 SM that the modern platform no longer answers the intended scientific question. Do not change workload dimensions after performance observation to resolve this; first report the measured launch geometry and causal consequence.

---

## 14. Files that require later reconciliation

After active M5.0BT is reviewed, integrate equivalent changes into the active compute authority. At minimum audit/update:

- `docs/dtc_l1/m5/M5_EXPERIMENT_MATRIX.md` — stale `8 SM`, cap256 and PTX-oriented identity;
- `docs/dtc_l1/m5/M5_HANDOFF_CONTRACT.md` — insert M5.0BT and trace-aware standard fields;
- `docs/dtc_l1/m5/M5_PARALLEL_BATCH_POLICY.md` — payload/trace-store/I/O-aware job policy;
- `docs/dtc_l1/m5/M5_PROBLEM_RESOLUTION_POLICY.md` — trace capture/replay identity and correctness split;
- `docs/dtc_l1/m5/M5_EXTENDED20_FORMAL_MATRIX.md` — trace-aware E1/E2 payload contract;
- `docs/dtc_l1/m5/M5_EXTENDED20_HANDOFF_CONTRACT.md` — trace fields and exception policy;
- `docs/dtc_l1/m5/extended20/M5_E2_JOB_MANIFEST_TEMPLATE.tsv` — payload-aware columns;
- future `M5_0C_PLATFORM.md`, `M5_0D_METRICS.md`, `M5_0E_FIDELITY_PASS.md` — enforce sections 6–8 above;
- future M5.1–M5.6 handoffs/review packs — reuse and trace-provenance rules;
- future `M5_COMPUTE_FREEZE.md` — trace-root/family hashes;
- `CURRENT_STATE.md`, `CODEX_NEXT_STAGE.md`, `GOAL_START.md`, `LATEST_REPORT.md` — active-state reconciliation belongs to the compute Codex window and must not be edited from this review branch while that window is active.

Historical approval files such as `M5_V1_APPROVAL.md` and `M5_EXTENDED20_APPROVAL.md` should normally be preserved as historical decisions and superseded by an explicit trace-transition amendment rather than rewritten in place.

---

## 15. Review status

Downstream review result:

`TRACE_DOWNSTREAM_CONTRACT_REQUIRES_AMENDMENT_BEFORE_FORMAL_M5.0C+`

No current M5.0BT capture or active compute process is modified by this review branch.

Recommended integration point: after the active Codex window reports the M5.0BT authority commit, five obsolete-cap termination state, exact Paper-10 capture manifest, and V100 capture handoff. Review that output against Section 13, then reconcile the downstream active authority before formal trace qualification/main experiments proceed.
