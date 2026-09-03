# M4 master goal — A/B integration -> LLM characterization -> Segmentation

Status: **FUTURE CONTRACT / DRAFT ONLY — NOT YET AUTHORIZED**.

This file is prepared while Track B is still executing `M4A_MERGE_PREP`.  It is
not a startup authorization.  After Track B reports
`M4A_MERGE_PREP_PASS_READY_FOR_INTEGRATION`, ChatGPT must independently review
that closeout, replace every `<B_...>` placeholder below with accepted immutable
anchors, make any evidence-driven small corrections, and issue a separate
`AUTHORIZED` start file.

The purpose of preparing this contract now is to make the post-B transition a
small provenance update rather than a new architecture-planning round.

---

## 1. Macro objective

Start from the accepted Track-A M1-M3 VM baseline and the accepted Track-B
formal LLM trace artifacts, then execute a single goal with internal gates:

```text
M4I — A/B integration
  -> M4R — formal trace replay compatibility
  -> M4C — LLM baseline translation characterization
  -> M4B-P — paper-facing paging-baseline preparation
  -> M4B-S — Segmentation mechanism reproduction on real prefill/decode1
  -> M4B-CLOSEOUT
  -> STOP before long-context synthetic-KV M5
```

The goal must preserve the distinction between:

- **generic VM infrastructure** accepted in M1-M3;
- **paper-known parameters** from the 2026 Segmentation paper;
- **self-captured LLM trace facts** from M4A;
- **project modeling decisions** used only where the paper/artifact is silent;
- **diagnostic/sensitivity modes** that must not silently become the paper
  baseline.

The first paper-facing result is allowed only after the real LLM traces run
through the final accepted M1-M3 Core and baseline translation behavior has been
characterized without Segmentation.

---

## 2. Frozen source anchors

### 2.1 Track A — accepted VM baseline

Core/GPGPU-Sim:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Framework accepted M1-M3 evidence source:

`47dde5767af8d30b892c7d63d932455644b7cf3a`

Track-A Framework may have later **ChatGPT-documentation-only descendants**.
The future authorized start file will provide the exact Framework branch point.
Do not replace the accepted Core with any Track-B parser Core.

### 2.2 Track B — placeholders until final merge-prep review

Accepted merge-prep Framework:

`<B_ACCEPTED_FRAMEWORK_SHA>`

Accepted M4A merge-prep integration manifest:

`<B_INTEGRATION_MANIFEST_PATH_AND_SHA>`

Formal prefill archive:

`/workspace/m4a-rented-host-pilot/formal-prefill/m4a-llama-prefill-20260902T182016Z.tar.zst`

SHA256:

`f96b7ea91b798e2ce8eb8f4592b1ef6512a762870471d2dbb85ab4777c97f181`

Formal decode1 archive:

`/workspace/m4a-rented-host-pilot/formal-decode1/m4a-llama-decode1-20260903T004138Z.tar.zst`

SHA256:

`5bdd4b55ed0e1499cbfee756d289cbd8072f556db4f467a882a54e42cd32dcad`

Capture executable Framework:

`c79f4469c6a2befa59e4c4efcd3c885dc2259a81`

Model:

`meta-llama/Llama-3.2-1B@4e20de362430cd3b72f300e6b0f18e50e7166e08`

The old Core `73774727e25fadf89df6f30ef5cf014091115db7` is only a
frozen parser-compatibility anchor from M4A.  It must never become the integrated
VM Core.

---

## 3. Required new integration branches

After authorization, create fresh branches/worktrees rather than reusing either
A or B worktree.

Core:

`swayhrl/gpgpu-sim:hrl/vm-llm-m4b-v0`

must branch exactly from:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Framework:

`swayhrl/accel-sim-framework:hrl/vm-llm-m4b-v0`

must branch from the exact Track-A Framework handoff SHA provided by the future
start authorization.

### Integration policy

Do **not** merge the Track-B Framework branch wholesale.

Use a deterministic **path-scoped import** from the accepted Track-B SHA.  This
prevents stale B copies of `CURRENT_STATE.md`, `CODEX_NEXT_STAGE.md`, and old
capture authorizations from overwriting the accepted A state.

Expected B-owned import families include, subject to the accepted merge-prep
manifest:

- `docs/vm_tlb/llm/**`
- `docs/vm_tlb/review_packs/M4A_*`
- `docs/vm_tlb/codex_handoff/m4a/**`
- historical `docs/vm_tlb/chatgpt_handoff/M4A_*`
- historical `docs/vm_tlb/chatgpt_handoff/stage_specs/M4A_*`
- `util/llm_trace_capture/**`
- the reviewed NVBit tracer ROI changes required by the captured artifacts

Do not import Track B's root `CURRENT_STATE.md` or `CODEX_NEXT_STAGE.md`.
Create `B_IMPORT_MANIFEST.tsv` recording every imported path and source blob/SHA.

No raw/formal archive is committed to Git.

---

## 4. Macro gate sequence

### M4I — integration and provenance

Follow `M4I_AB_INTEGRATION_AND_REPLAY.md`.

Minimum gates:

- I0 source/branch admission;
- I1 path-scoped B import;
- I2 immutable archive/derived-artifact binding;
- I3 final-Core build and M1-M3 regression preservation;
- I4 address-domain and object-metadata audit;
- I5 integrated parser/replay smoke.

### M4R — formal replay compatibility

Also covered by `M4I_AB_INTEGRATION_AND_REPLAY.md`.

Required distinction:

- `FULL_RANK0`: immutable semantic full ordering, including captured NCCL if
  present;
- `COMPUTE_ONLY_TP_PARTITION`: non-destructive semantic compute-only derivative.

Neither may be silently substituted for the other.  Both remain bound to the
same formal archive and semantic manifest.

A replay policy is not finalized from filename-only classification.  It must use
Track-B merge-prep semantic kernel names read from trace headers.

### M4C — LLM baseline translation characterization

Follow `M4C_LLM_BASELINE_CHARACTERIZATION.md`.

This stage runs **without Segmentation**.  It must establish what the real
prefill/decode1 traces actually do to:

- L1/L2 TLB;
- translation MSHR/PWQ;
- walkers;
- PWC;
- real PTE memory traffic;
- translation requester latency/stall;
- object-specific Weight/KV/UNKNOWN translation behavior;
- L2-TLB replacement interference, especially KV/UNKNOWN arrivals evicting
  weight translations.

The generic M1-M3 baseline is a reference point, not automatically the final
paper paging baseline.

### M4B-P — paper-facing paging baseline

Follow `M4B_SEGMENTATION_REPRODUCTION.md`.

Freeze the paper-known Table-I configuration and resolve the L2-TLB sub-entry
requirement before calling anything `PAPER_BASELINE`.

If exact target-paper/reference-[4] sub-entry semantics remain unavailable, the
goal may continue only under the explicitly authorized fallback rules in the
stage spec.  It must never silently call a guessed sub-entry design
`PAPER_EXACT`.

### M4B-S — Segmentation

Implement the weight-segment mechanism only after M4C and M4B-P gates pass.

Required causal behavior:

```text
weight segment hit
 -> conventional paging path suppressed before L2-TLB/MSHR/PTW
 -> no weight translation fill/replacement pollution
 -> physical address formed by descriptor mapping
 -> ordinary data cache/memory request proceeds once
```

Non-weight accesses remain on the conventional paging path.

Formal prefill/decode1 must then be rerun with the exact same trace/list/config
inputs except for the Segmentation mechanism.

### M4B-CLOSEOUT

Produce a short-context reproduction package and stop **before M5 synthetic KV**.

Do not inject a guessed 12K KV stream in this goal.  The target paper does not
publish enough detail about synthetic-KV temporal/VPN/reuse/port/MSHR/PTW
behavior for that to be an automatic modeling choice.

---

## 5. Paper-known configuration boundary

From the project paper specification, paper-known values include:

- model: Llama-3.2 1B;
- TP scale factor: 4, evaluate one partition;
- batch: 8;
- input sequence: 64;
- generated tokens: 3;
- primary trace regions: prefill and first decode;
- SMs: 35;
- clock: 1500 MHz;
- L1 cache: 128KB per SM;
- L2 cache: 3MB, 16-way;
- GDDR6: 12 channels;
- L1 TLB: 32 entries, fully associative;
- L2 TLB: 768 entries, 16-way;
- walkers: 16;
- page size: 64KB;
- L2-TLB sub-entry support belongs to the paging baseline;
- segment descriptor concept: base/limit/offset;
- 49-bit VA / 16-bit 64KB page offset -> 33-bit page-number field;
- weight segment lookup may run in parallel with L1-TLB lookup and masks the
  conventional result on a segment hit.

The following M1-M3 defaults remain **generic/reference modeling choices** until
stronger evidence exists:

- 32 translation MSHRs;
- 32 PWQ entries;
- FINITE-128 intermediate-only PWC;
- balanced radix prefix page table;
- L1/L2 TLB service timing 10/80 cycles;
- generic 56-bit VA mode.

Paper-facing runs should use 49-bit VA only if the formal trace address-domain
audit proves the captured SimVA representation fits that contract without
masking/truncation/canonicalization.  Otherwise stop before claiming
paper-specific address fidelity.

---

## 6. Formal run labels

Every result row must carry one of these labels:

- `CONTROL_VM_DISABLED`
- `CONTROL_VM_IDEAL_IDENTITY`
- `GENERIC_M3_LLM_BASELINE`
- `PAPER_PAGING_BASELINE`
- `PAPER_PAGING_BASELINE_APPROX` only if explicitly authorized fallback is used
- `SEGMENTATION_REAL_TRACE`
- `DIAGNOSTIC`

Also record the trace-policy label:

- `FULL_RANK0`
- `COMPUTE_ONLY_TP_PARTITION`

No plot/table may combine these without retaining both dimensions.

---

## 7. Global correctness invariants

The M1-M3 invariants remain frozen:

- raw/coalesced trace address is `SimVA`;
- preserve `SimVA` and `SimPA` separately;
- no data-cache request before translation is READY;
- no repeated TLB probe/port consumption while lookup service is in flight;
- same registered waiter retry bypasses before lookup resources;
- new waiter receives normal first lookup and may merge;
- one active walk per translation key;
- PTE requests physical, bypass translation and never recurse;
- PTE response association exact;
- wakeup exactly once;
- store/atomic/data side effects exactly once;
- ordinary kernel boundaries preserve intended translation state;
- final lookup/MSHR/PWQ/walker state quiesces.

Additional M4 invariants:

- trace archives and semantic full lists are immutable;
- object metadata is observational until Segmentation registration explicitly
  consumes only the frozen Weight segment;
- object classification alone cannot change cache/TLB behavior;
- segment hit never allocates/fills L2 TLB or starts MSHR/PTW;
- non-weight segment miss is observationally equivalent to the selected paging
  baseline;
- segment-table state persists across ordinary kernels in the same serving
  instance;
- no synthetic KV is introduced in M4B;
- no page fault/migration/UVM/MCM/multi-ASID mechanism is added.

---

## 8. Long-run / progress policy

Formal LLM replay may be substantially longer than LUD/BFS.

Do not classify a progressing simulation as failed only because wall-clock time
is long.  Record at least:

- wall-clock;
- simulator cycle/instruction progress;
- current kernel/list position;
- RSS;
- trace bytes/files consumed.

Follow repository `AGENTS.md` stop rules for stalled jobs.  In particular,
separate **slow but making progress** from **no-progress/hung**.

Before launching a very long full prefill, run a bounded throughput/ETA pilot on
the exact same configuration.  Do not replace the formal full replay with a
sample merely for convenience.  If projected runtime becomes operationally
unreasonable, stop with measured feasibility evidence rather than silently
changing the workload.

---

## 9. Required review packs

Create/complete:

- `docs/vm_tlb/review_packs/M4I_AB_INTEGRATION/`
- `docs/vm_tlb/review_packs/M4R_LLM_REPLAY_COMPAT/`
- `docs/vm_tlb/review_packs/M4C_LLM_TRANSLATION_CHARACTERIZATION/`
- `docs/vm_tlb/review_packs/M4B_PAGING_BASELINE/`
- `docs/vm_tlb/review_packs/M4B_SEGMENTATION_REAL_TRACE/`
- `docs/vm_tlb/review_packs/M4B_CLOSEOUT/`

Each formal pack must contain the standard project provenance files:

- `README.md`
- `SOURCE_ANCHORS.md`
- `COMMIT_HISTORY.md`
- `CHANGED_FILES.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- `RAW_LOG_INDEX.tsv`

and stage-specific structured CSV/TSV/JSON artifacts.

Maintain a new integrated report path:

`docs/vm_tlb/codex_handoff/m4b/LATEST_REPORT.md`

and progress ledger:

`docs/vm_tlb/codex_handoff/m4b/TARGET_PROGRESS.md`.

---

## 10. Hard STOP conditions

Stop before advancing if any of the following occurs:

- accepted Track-A Core cannot be reproduced/built after integration;
- Track-B archive/hash/derived-manifest mismatch;
- path-scoped import provenance cannot be resolved exactly;
- integrated parser changes the immutable trace or silently drops kernels;
- formal SimVA exceeds the selected paper-specific width and would require
  truncation/masking/canonicalization/relocation not already authorized;
- object ranges overlap ambiguously or do not correspond to trace SimVA in a
  way needed for segment registration;
- M1-M3 correctness regression;
- repeated lookup polling/resource consumption;
- request loss, duplicate wakeup or duplicate store/atomic/data effect;
- recursive PTE traffic or response misassociation;
- sub-entry implementation requires a materially new unapproved approximation;
- Segmentation changes non-weight paging semantics;
- segment hit still generates L2-TLB fill/MSHR/PTW activity;
- deadlock or unexplained nondeterminism;
- formal LLM replay has no measurable progress under the repository timeout
  policy;
- source/provenance ambiguity.

The expected normal final stop is after `M4B-CLOSEOUT`, before M5 long-context
synthetic-KV pressure and before any new AI-aware mechanism beyond the target
Segmentation reproduction.
