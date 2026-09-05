# M5 trace-to-final execution runbook

Status: **ACTIVE EXECUTION RUNBOOK — RE-READ AT EVERY STAGE TRANSITION**

Purpose: this file is the persistent operational companion to
`M5_TRACE_TO_FINAL_SINGLE_GOAL_CONTRACT.md`.  The single Codex Goal on the
SIM_HOST must re-read this runbook after every stage PASS, before entering the
next stage, and whenever it resumes after an interruption.  It is not a
separate approval gate and it must not turn ordinary stage transitions into
human pauses.

The current AutoDL SSH endpoint is runtime/ephemeral information and must be
passed to the Goal or orchestrator at execution time.  Do **not** commit host,
port, credentials, private-key contents, or passwords into Git.

---

## 1. Frozen scientific authority

Unless a genuine researcher decision explicitly changes them, keep:

- formal platform: V100 / SM7-style, 80 SM;
- global DTC lower outstanding cap: `10240`;
- researcher scaling rule: 128 credits/SM;
- `-gpgpu_l1_cache_write_ratio 0`;
- `80 SM + cap 256` as historical/diagnostic-only `CURRENT_INVALID_SUSPECT`;
- trace as the intended formal payload after M5.0BT representative
  qualification;
- any workload-local PTX execution exception isolated to that workload only.

Qualification config hashes:

- Base: `0f99ae3b7d3a81f813ba0ac9b24fab5fa57474f323bf655b0c56f73fb6d225d9`
- IO: `7acb491414f84f9738f6bbc76b0bc2bc83dd146fd205e6f8636126b135599f5c`
- OO: `07d451cddb5de536bb84610daf0b5f142adb1ad2a1260260e6f34dfa13c059ed`

Historical cap-256 results are never relabelled as formal cap-10240 results.

---

## 2. Stage re-read protocol — mandatory

At the beginning of the Goal, after every stage PASS, and after any interrupted
resume, read in this order:

1. `docs/dtc_l1/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/dtc_l1/codex_handoff/LATEST_REPORT.md`
3. `docs/dtc_l1/m5/M5_TRACE_TO_FINAL_SINGLE_GOAL_CONTRACT.md`
4. **this file**
5. the next stage's specific handoff/contract
6. `M5_PROBLEM_RESOLUTION_POLICY.md`
7. `M5_PARALLEL_BATCH_POLICY.md` before any long replay wave

Before transitioning:

- verify current Core/Framework/config/payload/parser identities;
- verify the completed stage's HARD acceptance;
- invalidate any stale identity affected by a repair;
- update the compact handoff and `LATEST_REPORT.md`;
- `git diff --check`;
- stage explicit paths only; never `git add .` / `git add -A`;
- commit/push compact evidence;
- immediately continue into the next authorized stage.

A checkpoint commit is not a Goal stop condition.

---

## 3. One-Goal host model

### SIM_HOST

Owns:

- the one persistent Goal;
- active scientific Git branches;
- immutable replay trace store;
- result registry;
- replay simulation;
- all analysis/review packs;
- final M5.12 synthesis.

### CAPTURE_HOST

AutoDL V100 is a disposable capture worker only.  It must not create
scientific commits or become a second independently managed research Goal.

AutoDL must use two distinct checkouts beneath the selected large data volume:

- `m5-control`: current V100-ready M5 Framework commit; contains controller,
  sm70 build scripts, checkers and Paper10 source manifest;
- `tracer-pin`: clean detached Framework
  `0db04452ec1c47630e4b08002067d82c6811e243`; used only through
  `--tracer-framework-src`.

Prefer SIM_HOST -> SSH -> AutoDL orchestration.  If GitHub SSH is unavailable
on the rented host, use public HTTPS or rsync a verified clean checkout from
SIM_HOST; do not copy long-lived private Git credentials to AutoDL.

---

## 4. AutoDL preflight — T1 entry

Freshly verify on the actual rental:

- exactly one CUDA-visible NVIDIA V100;
- compute capability 7.0;
- GPU UUID/model;
- driver;
- `/usr/local/cuda-11.8/bin/nvcc` and `ptxas`;
- gcc/g++/make/git/rsync/tar/zstd;
- CPU/RAM;
- mounted filesystems and free space;
- write test on the selected large data volume;
- SSH/rsync path back to SIM_HOST.

Do not assume `/root/autodl-tmp` is best merely because it was used before;
choose from fresh `df`/write evidence.  Do not place multi-GB traces on the
small root filesystem when a larger data volume exists.

A newer NVIDIA driver is acceptable; the capture compiler/toolkit remains
pinned to CUDA 11.8.

If CUDA 11.8 is absent, attempt a source-correct install or locate a valid
existing toolkit before escalating.

---

## 5. T1 — BICG exact capture pilot

Use the current Paper10 source contract and workload-conditional controller.
BICG must require only:

- exact PolyBench source;
- current M5 control checkout;
- tracer pin checkout;
- NVBit 1.8 archive;
- CUDA 11.8;
- one V100.

No SpMV/Parboil path is required for BICG.

No `DYNAMIC_KERNEL_RANGE`, shortened workload, kernel subset, or CTA subset is
formal.

HARD T1 acceptance:

- source commit/tree/file hash exact;
- CUDA11.8/sm70 build PASS;
- `TRACE_CAPTURE_BINARY_SHA` frozen;
- hardware application checker PASS;
- raw capture PASS;
- postprocess PASS;
- ordered kernel/invocation mapping PASS;
- geometry manifest PASS;
- immutable bundle SHA manifest PASS;
- archive PASS;
- no false PASS before archive completion.

Ordinary build/tracer/checker/postprocess failures are resolve-in-goal issues.

---

## 6. Storage admission and transfer

After BICG, measure:

- raw trace bytes;
- grouped traceg bytes;
- archive bytes;
- working/postprocess headroom;
- free bytes;
- safety factor.

Generate and validate `STORAGE_ADMISSION.json` bound to the exact BICG bundle
ID and archive SHA.  Any non-BICG formal capture requires this admission.

If BICG is not a credible storage upper bound, automatically capture an
additional representative/heavy pilot and update the admission calculation;
do not stop merely to ask permission for that storage diagnostic.

Copyback sequence:

`archive -> source SHA -> rsync partial/append-verify (or accepted equivalent)
-> destination SHA -> unpack once in SIM_HOST immutable store -> internal
SHA256SUMS revalidation -> transfer receipt`.

A valid capture bundle is never recaptured merely because archive or transfer
later failed.  Resume the missing archive/transfer state only.

---

## 7. T2 — BICG replay qualification

On SIM_HOST run the same immutable BICG trace bundle under Base/IO/OO at:

- 80 SM;
- cap 10240;
- ratio-zero.

HARD acceptance:

- same `TRACE_BUNDLE_ID` across the triplet;
- parser success;
- every expected invocation consumed;
- same dynamic trace stream across modes;
- Base/IO/OO enter their intended common cache/DTC timing paths;
- PIB/lower/inflight/pending/ref/reclaim/dependency accounting balances;
- final lifecycle drains are zero;
- no stale fill, duplicate lower request, unclassified deadlock, fatal or
  assertion.

Do not require cycle equality to old PTX/cap256 runs.

Keep distinct evidence fields for:

- capture application correctness;
- trace identity;
- replay terminal status;
- replay accounting status.

Repair source-correct trace/frontend/parser integration bugs rather than
abandoning trace mode after a repairable failure.

---

## 8. T3 — GESUMMV contrasting qualification

Capture/copy back exact GESUMMV and qualify Base/IO/OO under the same frozen
platform.  Apply the same HARD requirements as BICG.

If BICG + GESUMMV do not cover a materially distinct operation/cache path,
qualify SpMV and/or 2DConv as needed.

When sufficient representative evidence closes Q1, set:

`TRACE_FORMAL_PATH_VALID`.

A workload-local unsupported semantic may use a documented PTX_EXEC exception
without reverting the entire campaign.

---

## 9. T4 — remaining Paper-10 capture

Capture all remaining exact Paper-10 workloads resumably.  Every formal bundle
requires:

- exact source/input identity;
- hardware checker PASS;
- immutable trace bundle ID;
- ordered invocation manifest;
- geometry manifest;
- archive PASS;
- copyback SHA PASS;
- SIM_HOST internal SHA validation PASS.

Never overwrite a PASS bundle.  One physical V100 may capture sequentially;
reliability/resume/offload is more important than artificial capture
parallelism.

---

## 10. Extended-20 during the same V100 rental

Do not release the capture host immediately after Paper-10 if Extended-20 will
need exact traces.

Continue E1 source/input/checker/payload eligibility formalization while the
rental is live.  For each approved Extended workload classify:

- `TRACE_FORMAL_ELIGIBLE`
- `TRACE_ELIGIBLE_WITH_REVIEW`
- `EXECUTION_DRIVEN_EXCEPTION_REQUIRED`

Capture every source-frozen trace-eligible Extended workload during this rental
when practical.  This is infrastructure preparation only; E2 simulation
remains blocked until M5.2 PASS.

Never alter Extended membership based on DTC speedup.

---

## 11. Capture-host release condition

Set `CAPTURE_HOST_RELEASE_READY` only when:

- all required Paper-10 bundles are copied back and verified;
- all currently required trace-eligible Extended bundles are copied back and
  verified;
- no capture-only issue still needs the physical V100;
- archive/transfer receipts are valid.

This state does **not** stop the Goal.  Continue immediately on SIM_HOST.  The
researcher may release the paid AutoDL instance separately in the provider UI.

---

## 12. M5.0BT PASS

Requires:

- BICG qualification PASS;
- GESUMMV qualification PASS;
- additional representative qualification if needed;
- all Paper exact bundles returned/verified;
- `TRACE_FORMAL_PATH_VALID` or explicit workload-local exception;
- no unresolved correctness/fidelity issue.

PASS -> M5.0C automatically.

---

## 13. M5.0C — platform/payload fidelity lock

Freeze:

- 80 SM;
- cap10240;
- ratio-zero;
- formal Base/IO/OO hashes;
- execution payload kind;
- Core/Framework/parser/frontend identities;
- trace format/store policy;
- payload-aware result identity.

For every Paper workload audit actual:

- ordered kernel sequence;
- gridDim/blockDim;
- CTA count;
- CTA waves relative to 80 SM;
- active/request-generating SM opportunity;
- occupancy/resource constraints where available.

Do not change workload/input/launch geometry after seeing DTC performance.
Underfill is evidence to classify and explain, not a trigger for silent tuning.

PASS -> M5.0D.

---

## 14. M5.0D — metrics/parser lock

Keep Figure 4.2 categories:

- PIB full;
- true Tag+Cacheline allocation failure;
- MSHR capacity/merge;
- Miss Queue/lower capacity.

Tag-bank conflict remains diagnostic only.

Keep the approved Figure 4.7 configured-SM metric.  Add active-SM/CTA-wave
and per-active-SM diagnostics without changing the formal denominator after
seeing results.

Require directed counter tests, conservation/reconciliation, final zero live
state, parser schema freeze, and timing-neutral instrumentation proof or full
invalidation/regression when timing is affected.

PASS -> M5.0E.

---

## 15. M5.0E — formal fidelity pilot

At minimum run ATAX, SpMV, 2MM and 2DConv Base/IO/OO with exact same payload
inside each triplet.

Collect and validate:

- cycles/instructions;
- Figure 4.2 stalls;
- Figure 4.7 live misses;
- PIB/MSHR/true allocation/physical pool/reclaim;
- lower/downstream pressure;
- traffic/duplicate traffic;
- IO HOL;
- OO OOO-retire/reclaim evidence.

No thesis speedup threshold is a PASS criterion.  Weak/negative results are
causally diagnosed and retained.

Rows that exactly match the final formal anchor may be marked
`PILOT_FORMAL_REUSABLE`.

PASS -> main Paper acquisition.

---

## 16. Main Paper wave — high parallelism

After M5.0E, enqueue all eligible Paper-10 Base/IO/OO rows into one resumable
dynamic worker pool.  Do not serialize all Base, then all IO, then all OO.

M5.1 analysis closes before M5.2 analysis, but IO/OO acquisition may run while
M5.1 is being assembled.  Reuse exact M5.0E and M5.1/M5.2 identities.

Before each major wave measure:

- CPU count/load/per-job CPU;
- p50/p90/p95 RSS;
- MemAvailable;
- swap `si/so`;
- iowait;
- trace-store read throughput/latency;
- output/trace-store free space;
- unrelated host load.

Derive/refill `N_safe` dynamically.  The historical execution-driven 5-job
limit is not authority.  When measurements support it, scale toward tens of
independent replay jobs on the 512-CPU SIM_HOST.  If trace I/O is the binding
resource, reduce only to the measured I/O-safe concurrency.

One failed job never drains the whole pool.

---

## 17. M5.1 and M5.2

### M5.1

Requires ten valid Base identities, Figure 4.2 reconciliation and per-workload
bottleneck classification.  Do not rerun an identical Base row.

### M5.2

Requires ten complete same-payload triplets with performance, Figure 4.7 live
misses, traffic/downstream pressure, IO HOL, OO retirement/reclaim evidence and
causal classification.  Retain weak/negative workloads.

M5.2 PASS activates Extended E2 and Paper sensitivity acquisition.

---

## 18. After M5.2 — concurrent acquisition

Long data acquisition for these tracks may run concurrently:

- M5.3 logical capacity sensitivity;
- M5.4 physical capacity sensitivity;
- M5.5 PIB sensitivity;
- Extended E2 primary 60-run matrix.

Do not serialize them merely because handoff numbering is sequential.  Reuse
matching identities exactly.

M5.3/M5.4/M5.5 sweep points remain those already approved in the formal
matrix.  Do not invent new points.  An expected M5.4 deadlock requires
source-backed resource-deadlock evidence, not an arbitrary timeout.

---

## 19. Extended E1/E2/E3

E1 freezes all 20 source/build/input/checker/payload eligibility identities.
Do not redo already-valid evidence without reason.

E2 starts only after M5.2 PASS:

`20 x {Base, IO, OO} = 60 primary rows`.

Use the same high-parallel dynamic worker pool policy.  Every triplet uses the
same payload kind and exact trace bundle or documented PTX exception.

E3 causally classifies all 20, retains non-beneficiaries and computes explicit
membership for `GM-EXTENDED20` and `GM-ALL-COMPUTE30`.

---

## 20. M5.6 / Compute Freeze / M5.12

M5.6 must explain every Paper workload from evidence: Base bottleneck, DTC
concurrency change, performance/lack thereof, downstream saturation, traffic,
IO HOL, OO retire/reclaim, and sensitivity behavior.

Compute freeze requires both Paper M5.6 PASS and Extended E3 PASS, no unresolved
correctness/fidelity issue, clean pushed branches, frozen configs/parser, and
complete review packs.  Record immutable `COMPUTE_FREEZE_CORE_SHA` and
`COMPUTE_FREEZE_FRAMEWORK_SHA`.

M5.12 then integrates Paper-10, Extended-20, Figures 4.2/4.5/4.7/4.8/4.9/4.10,
causal classifications, differences from thesis, limitations, and accepted
`GRAPHICS_SOURCE_BACKED_UNAVAILABLE` evidence.  Do not fabricate graphics
results.

Terminal planned state:

`M5_COMPUTE30_COMPLETE_GRAPHICS_SOURCE_UNAVAILABLE_READY_FOR_REVIEW`.

---

## 21. Problem-resolution loop — do not stop on ordinary failures

Ordinary issues are not researcher boundaries.  For build, dependency, NVBit,
capture, postprocess, transfer, parser, counter, simulator assertion,
workload-local trace incompatibility, timeout-with-progress, weak/negative
performance, storage pressure, sensitivity deadlock, or one failed batch row,
use:

`OBSERVE -> REPRODUCE -> CLASSIFY -> SOURCE/TRACE/CONFIG INVESTIGATION ->
REPAIR/RECONSTRUCT -> REGRESS -> INVALIDATE AFFECTED STALE IDENTITIES -> RESUME`.

AutoDL SSH disconnect: reconnect/resume; do not recapture valid bundles.
Storage pressure: archive/offload/reclaim only according to validated receipts.
Performance anomaly: diagnose scientifically; do not tune architecture/input to
force thesis bars.

Pause only after exhausting reasonable source-backed options when:

1. the only fix changes frozen DTC architecture semantics;
2. irreducible scientifically different workload/metric interpretations remain;
3. a proxy/approximation would be required for a formal claim;
4. a platform/input change alters approved experiment meaning;
5. required hardware/storage evidence is impossible with no valid alternate;
6. required runtime credentials/connection information truly cannot be
   obtained;
7. the final M5 review state has been reached.

Before `RESEARCHER_DECISION_REQUIRED`, record attempts, source evidence,
rejected alternatives, invalidation scope and the smallest concrete decision
required.

---

## 22. Current-stage resume rule

After every PASS, the first action of the next stage is **not** to invent a new
plan.  Re-read the stage protocol in this runbook, the single-Goal contract,
and the stage-specific handoff, then execute the already-authorized next work.

Do not stop at:

- `BICG_CAPTURE_PASS`;
- `TRACE_FORMAL_PATH_VALID`;
- `M5.0BT_PASS`;
- `M5.2_PASS`;
- `M5.6_PASS`.

Only the final planned review state or a true researcher boundary ends the
persistent Goal.
