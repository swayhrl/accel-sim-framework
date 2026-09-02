# CODEX_NEXT_STAGE

## Status

Authorized macro execution after S1-B0.

Two independent tracks are authorized:

- **Track A:** `M1 -> M2 -> M3` VM/TLB/PTW implementation and validation.
- **Track B:** **M4A-P pre-capture preparation only**. Real rented-GPU capture is deliberately split into a later `M4A-C` stage and is **not authorized yet**.

Track B blockers do not block Track A unless they reveal a direct semantic incompatibility. Track A must preserve strict `M1 -> M2 -> M3` ordering.

Read before execution:

1. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. repository `AGENTS.md`
4. all stage specs referenced below
5. `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md` for Track B

Do not modify `chatgpt_handoff/*`.

---

## 0. Required synchronization and remote setup

### Framework

Use repository:
`swayhrl/accel-sim-framework`

Fetch the latest coordination branch `hrl/vm-core-v0` before creating/updating worktrees. The stage branches are:

- `hrl/vm-m1-m3-v0`
- `hrl/llm-trace-prep-v0`

The stage branches must include the latest ChatGPT-owned handoff/spec updates before execution.

### Core

Use writable project repository:
`swayhrl/gpgpu-sim`

Keep official upstream identity separate. Recommended local writable remote:

```bash
git remote add research git@github.com:swayhrl/gpgpu-sim.git
```

If `research` exists, verify it points exactly there rather than blindly rewriting it.

Verify:

- `research/hrl/vm-core-v0`
- `research/hrl/vm-m1-m3-v0`

Establish writability with a non-destructive authenticated check before Core source modification. Never push to official upstream.

---

## 1. Worktree / branch isolation

### Track A — M1-M3

Recommended worktrees:

- Core: `/workspace/worktrees/gpgpu-sim-vm-m1-m3`
- Framework: `/workspace/worktrees/accel-sim-vm-m1-m3`

Branches:

- Core: `hrl/vm-m1-m3-v0`
- Framework: `hrl/vm-m1-m3-v0`

Do not alter TLS worktrees, bootstrap worktrees, or unrelated running experiment worktrees.

### Track B — M4A-P

Framework worktree:

`/workspace/worktrees/accel-sim-llm-trace-prep`

Branch:

`hrl/llm-trace-prep-v0`

Track B must not modify Core simulator source. Its current goal is to recover/reuse existing rented-server trace infrastructure, prepare workload/metadata/capture tooling, and produce a ready external-capture package. It must STOP before actual rented-GPU capture.

---

## 2. Track A execution order

Execute in order:

1. `stage_specs/M1_VM_CORE_FOUNDATION.md`
2. `stage_specs/M2_FUNCTIONAL_TRANSLATION.md`
3. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`

For every macro stage:

1. implement only authorized scope;
2. run required directed tests;
3. run required integrated tests;
4. evaluate every acceptance criterion;
5. create `docs/vm_tlb/review_packs/<stage>/`;
6. make semantic commits using explicit-path staging only;
7. if PASS, continue automatically to the next authorized Track-A stage;
8. if FAIL / ambiguous correctness / provenance conflict, report, push review evidence, and STOP.

M1 failure blocks M2. M2 failure blocks M3.

After M3 PASS create:

`docs/vm_tlb/review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`

It must prove the resulting single-GPU VM baseline is suitable for later LLM reproduction.

---

## 3. Track B execution order — pre-capture only

The parent reference remains:

`stage_specs/M4A_LLM_TRACE_METADATA_PREP.md`

But execution is now split because real trace collection will occur on a separately rented GPU server.

### Authorized now

Execute:

`stage_specs/M4A_PRECAPTURE_PREP.md`

This stage must, among other things:

- audit exact public paper artifacts/traces;
- **find and report the user's previous AutoDL/rented-server generic trace collection scripts before writing replacements**;
- produce a capture-hardware compatibility matrix;
- freeze the short Llama workload contract;
- prepare the contiguous-weight workload path as far as possible without the rental GPU;
- prepare metadata schema/hooks and non-GPU validation;
- create a ready-to-run external capture package and runbook;
- recommend the exact GPU class to rent.

### Prepared but NOT authorized

`stage_specs/M4A_EXTERNAL_CAPTURE.md`

Do not start it until the user has selected/provisioned a rental GPU and ChatGPT updates the handoff.

Track B must STOP after M4A-P closeout even if a rental service is immediately accessible.

Do not claim a self-collected trace is the authors' exact trace. If a required paper detail remains unavailable, record `UNKNOWN` / `PAPER_DETAIL_UNAVAILABLE`; do not silently invent a `PAPER_EXACT` implementation.

---

## 4. Parallel reporting rule

Two Codex windows will run on separate branches. To avoid `LATEST_REPORT.md` merge conflicts, each track must maintain its own report path:

### Track A

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

### Track B

`docs/vm_tlb/codex_handoff/m4a/LATEST_REPORT.md`

Each track may create the needed subdirectory on its own branch. The bootstrap root report:

`docs/vm_tlb/codex_handoff/LATEST_REPORT.md`

is historical/bootstrap state and must not be used as the active report target by both parallel windows.

Each stage review pack remains under:

`docs/vm_tlb/review_packs/<stage>/`

At final consolidation, ChatGPT will review the two track-specific reports independently.

---

## 5. Global acceptance and STOP rules

The repository `AGENTS.md` is authoritative. STOP immediately on:

- baseline transparency failure;
- request loss;
- duplicate wakeup;
- duplicate store/atomic side effect;
- recursive translation of PTE requests;
- multiple active walks for one translation key contrary to frozen policy;
- unexplained nondeterminism;
- a required paper-exact detail that cannot be established and materially affects implementation;
- inability to push modified source to the approved writable remote;
- an attempt to cross from M4A-P into real external capture without explicit authorization.

Do not weaken a directed test merely to continue the macro task.

---

## 6. Review-pack requirements

Each stage pack must include at minimum:

- `README.md`
- `SOURCE_ANCHORS.md`
- `COMMIT_HISTORY.md`
- `CHANGED_FILES.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- `RAW_LOG_INDEX.tsv`

Functional VM stages additionally require machine-checkable invariant/test results and representative structured statistics.

M4A-P additionally requires a legacy-capture-asset audit, rental hardware recommendation, and exact external capture entry command/runbook.

Large raw logs, traces, model weights, build directories, credentials, and copyrighted paper PDFs must not be committed.

---

## 7. Git requirements

Forbidden:

- `git add .`
- `git add -A`
- pushing to official upstream
- force-pushing shared research history without authorization

Stage explicit paths only. Keep structural refactors separate from functional changes when practical.

Track A commits should clearly indicate M1/M2/M3 semantics. Track B commits should clearly indicate M4A pre-capture preparation and remain free of VM-mechanism Core changes.

---

## 8. Final STOP boundary for this authorization

### Track A

After M3 and `M1_M3_VM_BASELINE_CLOSEOUT`:

- push Core + Framework stage branches;
- update `codex_handoff/m1_m3/LATEST_REPORT.md`;
- provide review-pack entry points;
- STOP before M4B / Segmentation / synthetic-KV / new AI-aware mechanism.

### Track B

After `M4A_PRECAPTURE_PREP`:

- push `hrl/llm-trace-prep-v0`;
- update `codex_handoff/m4a/LATEST_REPORT.md`;
- report exact reusable legacy scripts found;
- report recommended rental GPU class and exact capture entry point;
- STOP before `M4A_EXTERNAL_CAPTURE`.

The user/ChatGPT will review both tracks independently before authorizing later work.
