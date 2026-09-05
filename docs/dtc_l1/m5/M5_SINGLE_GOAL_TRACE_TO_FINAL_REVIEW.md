# M5 trace-to-final single-goal review

Status: **CHATGPT/RESEARCHER REVIEW DRAFT — ISOLATED REVIEW BRANCH; NOT ACTIVE COMPUTE AUTHORITY**

Review target: active Framework authority through `e1c710dbfbab642e28d8517aa9de9371294f5aef` (`docs(m5): authorize exact Paper-10 trace capture`).

Purpose: review M5.0BT capture/qualification and every downstream stage through M5.12 for one persistent Goal that is allowed to diagnose, repair, resume, parallelize, and finish the complete task without routine human pauses. This file intentionally does not modify the active compute branch or `LATEST_REPORT.md` while the compute Codex window owns them.

---

## 1. Overall verdict

The authority transition at `e1c710db...` is directionally correct:

- the five obsolete `80 SM + cap 256` execution-driven jobs are no longer a gate;
- Q2/Q3 remain frozen at V100/SM7-style 80 SM and global lower cap 10240;
- M5.0BT exact trace capture/qualification replaces the obsolete M5.0B natural-terminal wait;
- trace-driven becomes the intended formal path only after exact-trace qualification;
- old cap-256 evidence remains historical validation/provenance only.

However the current V100 capture package is **not yet rental-ready**. It contains several hard implementation/provenance defects that would either fail immediately or produce an under-specified formal trace identity. These defects should be corrected on the active compute branch before renting the V100.

After those corrections, the downstream M5 scientific structure remains valid:

`M5.0BT -> M5.0C -> M5.0D -> M5.0E -> M5.1 -> M5.2 -> M5.3/M5.4/M5.5 acquisition -> M5.6`

with Extended:

`M5.E1 -> M5.E2 -> M5.E3`

then:

`M5.COMPUTE_FREEZE -> M5.12`.

The numbered analysis handoffs may remain ordered, but long independent trace replays must not be serialized merely because the sections are numbered sequentially.

---

## 2. M5.0BT capture-package blockers found in `e1c710db...`

### T-BLOCKER-01 — capture binary identity is tied to the obsolete sm_52 recovery executable

`PAPER10_TRACE_CAPTURE_MANIFEST.tsv` and `capture_m5_paper10_traces.sh` require each V100 capture executable SHA-256 to equal the old execution-driven `sm_52` recovery executable SHA. The build scripts themselves hard-code `-arch=sm_52`.

That is the wrong authority boundary for a V100 SASS trace campaign.

Required correction:

- keep the old executable/PTX identity as `RECOVERY_EXEC_BINARY_SHA` / historical workload-recovery evidence;
- create a distinct V100 trace-capture build identity, preferably CUDA 11.8 with explicit Volta `sm_70` code generation;
- freeze the exact executable actually run under NVBit as `TRACE_CAPTURE_BINARY_SHA`;
- preserve the same canonical source, source commit, input, command line, algorithm, output checker and cache/preference semantics;
- record compiler/linker versions and full build recipe.

The formal trace identity is the immutable trace bundle generated from the approved source/input/capture binary. It is not required to equal the old PTX recovery binary hash.

### T-BLOCKER-02 — current PolyBench capture error scan will reject valid runs

The capture script ends each workload with a generic case-insensitive scan for `(fatal|assert|error)` in `capture.log`.

The approved PolyBench checker itself expects the normal source verdict text:

`Non-Matching CPU-GPU Outputs Beyond Error Threshold ...: 0`

Therefore every valid PolyBench run containing the word `Error` is liable to be rejected by the generic scan.

Required correction:

- do not grep the application+tracer combined log for generic `error`;
- either separate tracer stderr from application stdout or match only source-backed fatal/CUDA/tracer signatures;
- keep application correctness determined by the source-defined checker, not by a generic word scan.

### T-BLOCKER-03 — `2dconv` capture invokes the output checker with an unsupported workload key

The capture loop uses internal key `2dconv` and passes it directly to `verify_m5_polybench_output.py`.

That checker accepts `conv2d`, not `2dconv`.

Required correction:

- add an explicit capture-key -> checker-key map;
- regression-test all nine PolyBench rows with the checker command before V100 rental.

### T-BLOCKER-04 — `CAPTURE_TIME_REQUIRED` manifest fields are not actually frozen by the script

The handoff says capture-time kernel names/ABI and launch geometry are written into immutable per-workload evidence. The script currently copies the TSV containing `CAPTURE_TIME_REQUIRED`, produces raw `stats.csv`/`kernelslist`, writes only line counts, and never emits a resolved capture-result manifest.

Required correction:

Produce a deterministic `CAPTURE_RESULT_MANIFEST.tsv` (or equivalent JSON/TSV) with one row per workload and at minimum:

- trace workload ID;
- source commit/path/hash;
- trace-capture binary SHA;
- exact arguments/input hashes;
- checker/reference identity and PASS status;
- GPU UUID/model/CC;
- CUDA/NVBit/tracer/postprocessor identities;
- observed kernel invocation sequence;
- kernel ABI/name;
- per-invocation gridDim/blockDim if available from the trace metadata;
- raw kernel count;
- grouped kernel count;
- `kernelslist` SHA;
- `kernelslist.g` SHA;
- stable ordered `TRACEG_SET_SHA256`;
- stable ordered raw-trace root hash when raw traces are retained;
- trace-format/version;
- final workload trace-bundle ID.

No `CAPTURE_TIME_REQUIRED` placeholder may remain in a PASS workload row.

### T-BLOCKER-05 — tracer source provenance is asserted but not verified

The handoff requires NVBit 1.8 and tracer source at Framework `0db04452...`, but the capture script accepts an arbitrary `--tracer-so` and records only its binary hash. It does not prove that the supplied tool was built from that source commit/tree.

Required correction:

- either add `--tracer-src` and require its Git commit/tree to match the pinned authority, or build the tracer inside the capture bundle from a pinned checkout;
- record `TRACER_SOURCE_COMMIT`, tracer source-tree/root hash, `tracer_tool.so` hash, NVBit archive/version/hash and postprocessor hash;
- reject a prebuilt tracer with unknown source provenance.

### T-BLOCKER-06 — V100 device check is not bound to the selected CUDA device

The script greps global `nvidia-smi` output for `V100`, which can succeed when a different system GPU is V100 while `CUDA_VISIBLE_DEVICES` points elsewhere.

Required correction:

- require exactly one capture GPU selection;
- record physical GPU UUID, model and compute capability for the actual selected CUDA device;
- verify the selected device is V100/Volta before capture;
- record driver and runtime versions.

### T-BLOCKER-07 — all-ten one-shot capture is not resumable and wastes rented-GPU time on one local failure

The script is fail-closed across the entire invocation. Any workload-local build/checker/postprocess issue aborts the remaining nine captures.

Fail-closed evidence is correct; global abort behavior is not optimal for a persistent Goal on a rented V100.

Required correction:

- make capture state per workload: `PENDING`, `CAPTURING`, `PASS`, `RESOLVING_ISSUE`, `RETRY_READY`, `FAILED_HARD`;
- give each attempt an isolated output directory;
- never overwrite a PASS trace bundle;
- continue unrelated workloads while diagnosing a workload-local issue;
- add `--workloads` / `--resume` support or an outer persistent capture controller.

### T-BLOCKER-08 — no storage-budget or transfer gate exists

Exact instruction traces can be much larger than executables or PTX. The current package does not estimate full Paper-10 trace volume before launching all ten.

Required correction:

- capture one representative pilot first;
- record raw and grouped trace bytes, dynamic traced instructions and compression ratio;
- estimate remaining Paper-10 storage;
- verify capture-host and replay-host free space before full wave;
- define archive, checksum, transfer and post-transfer verification;
- use a shared immutable replay trace store; never duplicate trace files per simulator job.

### T-BLOCKER-09 — trace qualification requires cap-10240 Base/IO/OO configs that do not yet exist as a complete formal family

The current named `PAPER_BASE_16KB.config`, `PAPER_IO_16KB.config`, and `PAPER_OO_16KB.config` omit an explicit `-gpgpu_dtc_l1_lower_outstanding_cap` and therefore inherit the Core default 256. Only the BF Base diagnostic config explicitly carries 10240.

M5.0BT qualification itself requires Base/IO/OO under 80 SM + cap 10240, so this cannot be deferred until after qualification.

Required correction before replay qualification:

Create and freeze a complete qualification/formal config family with explicit cap 10240 for Base, IO and OO. Prove all unrelated platform bytes are identical and only approved mode/mechanism-specific fields differ.

### T-BLOCKER-10 — the superseded live checkpoint remains internally contradictory

`M5_0B_LIVE_REVIEW_CHECKPOINT.md` now begins with the correct superseding aborted-cap256 closeout, but later retains historical sections that still say the five jobs are live and that M5.0C requires their natural-terminal completion.

Required correction:

- preserve historical text only under an unmistakable `HISTORICAL SNAPSHOT — SUPERSEDED` heading, or move it into a historical appendix;
- ensure no mandatory-read/current-state paragraph can be interpreted as requiring those jobs to resume or finish.

---

## 3. One persistent Goal: host roles

The cleanest one-Goal architecture is to keep the large CPU simulator server as the **controller/replay host** and treat the rented V100 as a temporary **capture worker**.

Preferred setup:

- `SIM_HOST`: current server, large CPU/RAM, owns active Framework/Core branches, result registry, trace qualification and all M5 replay waves;
- `CAPTURE_HOST`: rented V100, only builds/executes approved capture binaries, captures/postprocesses traces, runs hardware application checkers and returns immutable bundles.

If possible, configure passwordless SSH/rsync from `SIM_HOST` to `CAPTURE_HOST` so one Codex Goal on `SIM_HOST` can orchestrate remote capture, transfer, replay qualification and all downstream stages without switching control windows.

If one cross-host SSH controller cannot be established, use the same state machine and immutable handoff files across the two machines, but do not let both windows write the same active branch/worktree concurrently.

---

## 4. Persistent-Goal execution policy

The Goal is not allowed to stop on an ordinary problem.

For every recoverable issue it must execute:

`OBSERVE -> REPRODUCE -> CLASSIFY -> INVESTIGATE SOURCE/TRACE -> REPAIR/RECONSTRUCT -> REGRESS -> INVALIDATE STALE IDENTITIES -> RESUME`.

Examples that must normally be solved without human pause:

- CUDA/NVBit build dependency failure;
- tracer build/runtime failure;
- one workload capture failure;
- missing trace metadata field;
- postprocess/parser error;
- corrupt/incomplete transfer;
- simulator assertion with source-correct repair available;
- counter/parser gap;
- workload-local trace semantic incompatibility;
- timeout while progress exists;
- poor/negative DTC speedup;
- one failed batch row;
- unexpectedly low/high pressure;
- one sensitivity point deadlocking as the approved mechanism predicts.

A pause is allowed only after exhausting source-backed recovery and only for a true researcher boundary:

- the only fix changes frozen DTC architecture semantics;
- formal workload/trace identity can only be preserved by choosing between scientifically different source interpretations not resolved by evidence;
- a proxy/approximation would be required for a formal result;
- a proposed platform/input change alters approved experiment meaning and is not covered by a pre-approved rule;
- storage/hardware failure makes further evidence collection unsafe and no alternate store/host is available;
- final M5 review state is reached.

Before any `RESEARCHER_DECISION_REQUIRED`, the Goal must record attempted fixes, source evidence, rejected alternatives, invalidation scope and the smallest concrete decision required.

---

## 5. M5.0BT end-to-end acceptance

### M5.0BT-A — capture-contract repair

HARD acceptance:

- T-BLOCKER-01 through T-BLOCKER-10 resolved or explicitly superseded by stronger evidence;
- capture scripts pass shell/static tests and checker-command dry runs for all ten IDs;
- no old cap-256 job remains active;
- Q2/Q3 remain 80 SM + cap 10240;
- no trace capture begins with unresolved workload source/input identity.

### M5.0BT-B — V100 preflight and BICG capture pilot

Before full capture:

- selected GPU is verified as V100/Volta and recorded by UUID;
- CUDA/NVBit/tracer/postprocessor identities match the contract;
- exact BICG capture binary build passes hardware correctness;
- full BICG trace capture (no kernel/CTA filtering) and postprocess pass;
- resolved capture-result row contains no placeholders;
- raw/grouped trace hashes and trace-bundle ID freeze;
- capture storage growth and compression ratio are measured;
- projected Paper-10 storage fits the capture/return plan.

### M5.0BT-C — pilot transfer and trace replay qualification

Transfer the BICG bundle to `SIM_HOST`, checksum it, then run the same exact trace bundle under:

- PAPER_BASE cap10240;
- PAPER_IO cap10240;
- PAPER_OO cap10240.

HARD acceptance:

- trace parser consumes the immutable bundle;
- Base/IO/OO all use the same trace-bundle ID;
- Base/IO/OO reach the intended common LD/ST/DTC timing path as applicable;
- no fatal/assert/deadlock/stale-fill/duplicate-completion failure;
- request/dependency/PIB/lower/inflight/ref conservation closes;
- expected kernel invocation count is consumed;
- trace-level dynamic stream identity is identical across modes;
- no PTX/cap256 cycle equality is required.

If BICG passes, run GESUMMV as the contrasting qualification case. Add SpMV and/or 2DConv only if a materially distinct memory/operation pattern needs proof.

M5.0BT may declare `TRACE_FORMAL_PATH_VALID` only after the representative qualification contract passes.

### M5.0BT-D — remaining Paper-10 capture

Once the pilot is qualified, capture the remaining Paper workloads on the V100 using the resumable workload queue.

HARD acceptance per workload:

- capture application checker PASS;
- exact source/input/capture binary identity;
- complete full-workload trace;
- postprocess PASS;
- resolved kernel inventory/geometry;
- immutable bundle hashes;
- successful checksum transfer to shared replay store.

A workload-local unsupported trace semantic must be classified. A source-correct execution-driven cap10240 exception is permitted only for that workload if exact trace replay cannot preserve its required semantics; it must not revert the whole campaign.

M5.0BT PASS requires:

- `TRACE_FORMAL_PATH_VALID` for the common Paper path;
- every Paper-10 workload has either `TRACE_FORMAL_ELIGIBLE` with exact bundle ID or a documented source-backed workload-local execution exception;
- all bundles transferred/verified;
- no unresolved capture correctness/provenance issue.

PASS -> M5.0C automatically.

---

## 6. M5.0C acceptance — platform/config/execution payload freeze

HARD acceptance:

- new Base/IO/OO formal config family explicitly uses 80 SM + cap10240;
- all unrelated GPU/L2/MC/NoC/DRAM parameters are byte-identical across the family;
- ratio-zero conventional-L1 policy remains explicit;
- logical/physical/PIB/MSHR/tag-bank/allocation/issue-width semantics match approved definitions;
- formal payload kind is frozen (`TRACE` for common path, explicit per-workload exception only if approved by M5.0BT);
- trace frontend/parser SHA, trace manifest version, runner command shape and shared trace-store policy are frozen;
- result identity tuple is payload-aware rather than PTX-only;
- launch geometry for all exact Paper traces is inventoried.

Mandatory launch/utilization audit per kernel/workload:

- gridDim/blockDim;
- CTA count;
- approximate CTA waves vs 80 SM;
- active-SM coverage class (`FULL_80SM`, `PARTIAL_80SM`, or source-backed equivalent);
- downstream pressure interpreted relative to actually request-generating SMs.

Do not change source/input after seeing DTC performance merely to fill 80 SM. Underfill is evidence and must be reported. A deliberate scale change outside an already-approved pre-performance rule is a researcher boundary.

PASS artifact: `M5_0C_PLATFORM.md` + new config manifest + payload identity schema.

PASS -> M5.0D automatically.

---

## 7. M5.0D acceptance — metrics/parser lock

HARD acceptance:

- Figure 4.2 primary categories are exactly PIB full, true Tag/cacheline allocation failure, MSHR capacity/merge, lower/miss-queue capacity;
- Tag-bank arbitration remains diagnostic only;
- Figure 4.7 common live-miss lifecycle/create-complete conservation is identical across Base/IO/OO;
- replay parser records `capture_app_correctness`, `trace_identity_status`, `replay_terminal_status`, and `replay_accounting_status` separately;
- trace bundle ID is emitted in every result row;
- Base/IO/OO consume the same dynamic trace stream;
- directed counter tests independently trigger all Figure 4.2 categories, tag-bank conflict and live-miss create/complete;
- instrumentation differential proves no timing change unless a deliberate behavior fix was made and regressed.

Keep the frozen Figure 4.7 formal denominator `configured_num_sm * sampled_cycles`, but add diagnostics for active-SM fraction and `avg_concurrent_misses_per_active_sm` or a source-backed residency proxy so an underfilled 80-SM grid is not misinterpreted.

PASS -> M5.0E automatically.

---

## 8. M5.0E acceptance — representative fidelity pilot

Use the frozen trace/config/parser anchor.

Required sentinels remain ATAX, SpMV, 2MM, Conv2D unless a source-backed trace exception requires an equivalent explicit path.

For every Base/IO/OO triplet require:

- immutable same trace payload across modes;
- replay correctness/drain PASS;
- cycles and live-miss metrics;
- Base Figure 4.2 structural stalls;
- PIB/MSHR/Tag/physical/downstream pressure;
- DTC valid/pending/new-miss and lower traffic;
- IO HOL and OO out-of-order retire evidence.

Every surprising result must be classified as implementation/modeling, workload/input/platform, downstream, traffic, compute-bound, or genuine mechanism limitation. Negative performance is not a failure.

If the M5.0E exact identity remains unchanged through M5.1/M5.2, mark those rows `PILOT_FORMAL_REUSABLE`; otherwise rerun only affected identities.

PASS -> launch main Paper matrix automatically.

---

## 9. M5.1 + M5.2 acquisition and acceptance — aggressively parallel

After M5.0E PASS, enqueue the complete ten-workload main matrix under the frozen anchor rather than serializing by chapter:

`10 workloads x {BASE, IO, OO}`.

Operational rule:

- Base rows feed M5.1 Figure 4.2 analysis;
- matching IO/OO rows may run concurrently while other Base rows are still running;
- M5.1 analysis must PASS before M5.2 analysis closes, but data acquisition need not wait.

Never rerun a Base row whose full formal identity already matches M5.0E/M5.1.

M5.1 HARD acceptance:

- all ten Base replay identities valid;
- four Figure 4.2 categories reconcile;
- no primary/diagnostic category aliasing;
- workload/platform differences from thesis are causally documented.

M5.2 HARD acceptance:

- all ten triplets complete with same payload per workload;
- dynamic trace identity matches across modes;
- replay accounting drains;
- Figure 4.7 create==complete/current==0;
- weak/negative speedups retain causal classification;
- IO/OO interpretation uses HOL/OOO evidence;
- outputs `m5_fig4_5_performance.csv`, `m5_fig4_7_concurrent_misses.csv`, causal analysis and review pack.

M5.2 PASS activates Extended E2 and the Paper sensitivity waves.

---

## 10. Post-M5.2 simulation acquisition — do not serialize M5.3/M5.4/M5.5/E2

Once M5.2 freezes the common anchor, the following long replay sets are scientifically independent and should be entered into one shared resource-aware scheduler with stage/priority tags:

- M5.3 logical-cache sweep;
- M5.4 physical-cache sweep;
- M5.5 PIB sweep;
- Extended M5.E2 primary 60-run wave.

Their analysis handoffs may still close in M5.3 -> M5.4 -> M5.5 -> M5.6 order, but execution must overlap when resources permit.

Reuse rules:

- M5.3 16-KiB IO/OO rows reuse M5.2;
- optional Base 16-KiB control reuses M5.1/M5.2;
- M5.4 uses compute-only 16.5/24/32/40/48 KiB physical points;
- M5.5 reuses any exact M5.4 `OO, physical=32 KiB, PIB=128` identity;
- never rerun a matching result solely because another stage wants it.

M5.3 acceptance:

- only logical capacity changes within each family;
- physical capacity/PIB/platform/trace remain fixed;
- 16/32/64 KiB trends explained with miss/concurrency data.

M5.4 acceptance:

- only physical capacity changes within each family;
- IO/OO use identical capacities;
- any deadlock is proven by source/resource no-progress evidence, not timeout alone;
- approved IO passive-release deadlock remains an expected classification where naturally observed;
- OO reclaim invariants close.

M5.5 acceptance:

- PIB is the only mechanism knob changed within each family;
- physical cache=32 KiB and logical cache=16 KiB as approved;
- 32/64/128/192 entries for IO/OO;
- IO/OO retirement width unchanged;
- HOL/concurrency explanation complete, especially SpMV.

---

## 11. Extended E1/E2/E3 trace-aware acceptance

E1 should continue during Paper capture/replay whenever it does not compete for critical trace/storage resources.

If Paper M5.0BT freezes trace-driven as the common path, E1 must add per workload:

- `TRACE_FORMAL_ELIGIBLE`;
- `TRACE_ELIGIBLE_WITH_REVIEW`;
- or `EXECUTION_DRIVEN_EXCEPTION_REQUIRED`.

Extended trace identity must use the same payload-aware schema. Historical trace availability is not formal identity.

If the rented V100 is still available after Paper capture and an Extended workload already has frozen source/input/output-check identity, capturing its exact trace is encouraged so another V100 rental is not required. Do not delay Paper qualification to force incomplete Extended E1 rows onto the capture GPU.

E2 acceptance remains 20 exact Base/IO/OO primary triplets, but replay correctness replaces simulator-side host-output checking for trace payloads; hardware capture correctness travels with the trace bundle.

E3 requires one causal class per workload, negative results retained, and exact memberships for `GM-EXTENDED20` and `GM-ALL-COMPUTE30`.

---

## 12. Aggressive simulator-host parallelism policy

The replay host has very large CPU capacity and substantial RAM. Low parallelism such as 3–5 independent jobs is not the default once trace replay is qualified.

Before each major wave, calibrate with a mixed representative set and derive `N_safe` from measured:

- logical CPU count and per-job CPU utilization;
- p90/p95 RSS;
- MemAvailable and swap I/O;
- trace-store read bandwidth and I/O wait;
- output-disk free space/growth;
- currently active non-M5 jobs.

The scheduler must keep the worker pool filled whenever independent eligible jobs exist and the host remains inside the safe envelope.

Required dynamic behavior:

- if CPU is materially underutilized, MemAvailable remains comfortably above reserve, `si/so=0`, trace I/O is not saturated and disk free space is safe, increase active workers rather than waiting for a stage batch to drain;
- if swap I/O appears, memory reserve is crossed, trace-store I/O wait saturates or disk reserve is threatened, throttle admission without killing healthy running jobs;
- use separate `LIGHT/MEDIUM/HEAVY/TRACE_IO_HEAVY` scheduling classes;
- mix workloads/modes/stages to avoid a heavy tail;
- use one immutable shared trace copy and isolated output directories;
- one failed job enters issue resolution while unrelated jobs continue unless the suspected defect may invalidate them.

Every major batch handoff must record measured `N_safe`, p95 RSS, active-worker peak, trace read pressure, free-space minimum and throttling events.

An orchestration is not accepted as efficient if many independent jobs remain pending while the host has obvious CPU/RAM/I/O headroom and the worker pool stays artificially small without documented reason.

---

## 13. M5.6, compute freeze, and M5.12 acceptance

M5.6 HARD acceptance:

- every Paper-10 workload has a causal classification;
- main performance is linked to live-miss change and Base structural pressure;
- IO-vs-OO claims are backed by HOL/OOO-retire evidence;
- physical/PIB sensitivity claims are backed by corresponding pressure/reclaim metrics;
- downstream/traffic-limited and genuine non-beneficiary cases are retained;
- no unresolved correctness/fidelity issue remains.

Compute freeze requires BOTH:

- Paper M5.6 PASS;
- Extended E3 PASS;
- active compute branches pushed/clean;
- no unresolved correctness/fidelity issue.

Freeze immutable Core/Framework/config/parser/payload-manifest SHAs and exact 30-workload result membership.

M5.12 then consumes the accepted graphics closeout `GRAPHICS_SOURCE_BACKED_UNAVAILABLE`, emits the Paper-10, Extended-20 and all-compute causal synthesis, preserves the absence of formal graphics bars, and reaches:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`.

Figure 4.6 synthesis/area remains outside this Goal unless separately authorized as M6.

---

## 14. Continuous Goal state machine

The final integrated Goal should implement this state machine and continue automatically after every PASS:

`T0_CAPTURE_CONTRACT_REPAIR`
`-> T1_V100_PREFLIGHT_BICG_CAPTURE`
`-> T2_BICG_TRACE_REPLAY_QUALIFICATION`
`-> T3_GESUMMV_SECOND_QUALIFICATION`
`-> T4_REMAINING_PAPER_TRACE_CAPTURE_TRANSFER`
`-> M5.0BT_PASS`
`-> M5.0C`
`-> M5.0D`
`-> M5.0E`
`-> MAIN_MATRIX_PARALLEL_ACQUISITION`
`-> M5.1_PASS`
`-> M5.2_PASS`
`-> PARALLEL_{M5.3,M5.4,M5.5,E2}_ACQUISITION`
`-> M5.3_PASS`
`-> M5.4_PASS`
`-> M5.5_PASS`
`-> M5.6_PASS`
`-> E3_PASS`
`-> M5.COMPUTE_FREEZE`
`-> M5.12`
`-> FINAL_REVIEW_STATE`.

`WAITING` is not a terminal Goal state. When a remote capture or long replay is active, continue safe independent work and low-frequency monitoring; return control only when no useful safe work exists or a genuine researcher boundary is reached.

---

## 15. Files/contracts that must be reconciled before formal M5.0C data

At minimum the active compute branch should reconcile:

- `M5_0BT_TRACE_CAPTURE_HANDOFF.md`;
- `PAPER10_TRACE_CAPTURE_MANIFEST.tsv`;
- `capture_m5_paper10_traces.sh`;
- `CURRENT_STATE.md`;
- `CODEX_NEXT_STAGE.md`;
- `GOAL_START.md`;
- `LATEST_REPORT.md`;
- `M5_0B_LIVE_REVIEW_CHECKPOINT.md` historical/superseded wording;
- `M5_EXPERIMENT_MATRIX.md` trace-transition amendment;
- `M5_HANDOFF_CONTRACT.md`;
- `M5_PARALLEL_BATCH_POLICY.md` payload-aware trace-I/O scheduling;
- result-registry/job-manifest identity schema;
- new explicit cap10240 Base/IO/OO config family;
- Extended `M5_EXTENDED20_FORMAL_MATRIX.md`, `M5_EXTENDED20_HANDOFF_CONTRACT.md` and `M5_E2_JOB_MANIFEST_TEMPLATE.tsv` after Paper trace path is frozen.

Do not silently rewrite historical evidence; add superseding authority and mark obsolete identities explicitly.
