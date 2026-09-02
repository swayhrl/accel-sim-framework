# CODEX_NEXT_STAGE

## Status

Authorized macro execution after S1-B0.

Two independent tracks are authorized:

- **Track A:** `M1 -> M2 -> M3` VM/TLB/PTW implementation and validation.
- **Track B:** `M4A` LLM trace / metadata / paper-input preparation.

Codex may interleave the tracks. Track B blockers do not block Track A unless they reveal a direct semantic incompatibility. Track A must preserve the strict `M1 -> M2 -> M3` ordering.

Read before execution:

1. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
2. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
3. repository `AGENTS.md`
4. all stage specs referenced below
5. `docs/vm_tlb/paper_specs/SEGMENTATION_LLM_2026.md` for M4A

Do not modify `chatgpt_handoff/*`.

---

## 0. Required synchronization and remote setup

Before any source modification:

### Framework

Use repository:
`swayhrl/accel-sim-framework`

Fetch the latest `hrl/vm-core-v0` and the pre-created target branches:

- `hrl/vm-m1-m3-v0`
- `hrl/llm-trace-prep-v0`

### Core

Current local worktree previously had only the official upstream remote. Add a writable research remote without replacing the upstream identity:

```bash
git remote add research git@github.com:swayhrl/gpgpu-sim.git
```

If a `research` remote already exists, verify it points exactly there rather than blindly rewriting it.

Fetch and verify:

- `research/hrl/vm-core-v0`
- `research/hrl/vm-m1-m3-v0`

A push dry-run or equivalent authenticated non-destructive check must establish writability before Core source modification.

Never push to the official Accel-Sim/GPGPU-Sim upstream.

---

## 1. Worktree / branch isolation

### Track A — M1-M3

Recommended worktrees:

- Core: `/workspace/worktrees/gpgpu-sim-vm-m1-m3`
- Framework: `/workspace/worktrees/accel-sim-vm-m1-m3`

Branches:

- Core: `hrl/vm-m1-m3-v0`
- Framework: `hrl/vm-m1-m3-v0`

Use the current remote branches created from the reviewed VM-core bootstrap. Do not alter TLS worktrees, the bootstrap worktrees, or unrelated running experiment worktrees.

### Track B — M4A

Recommended Framework worktree:

`/workspace/worktrees/accel-sim-llm-trace-prep`

Branch:

`hrl/llm-trace-prep-v0`

M4A must not modify Core simulator source. If Core/tracer changes become genuinely necessary to acquire metadata, document the exact need and STOP before making them unless the M4A spec explicitly permits the specific change.

---

## 2. Track A execution order

Execute these specs in order:

1. `stage_specs/M1_VM_CORE_FOUNDATION.md`
2. `stage_specs/M2_FUNCTIONAL_TRANSLATION.md`
3. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`

For every macro stage:

1. implement only the authorized scope;
2. run the required directed tests;
3. run the required integrated tests;
4. evaluate every acceptance criterion;
5. create `docs/vm_tlb/review_packs/<stage>/`;
6. make semantic commits using explicit-path staging only;
7. if PASS, continue automatically to the next authorized Track-A stage;
8. if FAIL / ambiguous correctness / provenance conflict, update `LATEST_REPORT.md`, push review evidence, and STOP.

M1 failure blocks M2. M2 failure blocks M3.

After M3 PASS, create an additional macro closeout pack:

`docs/vm_tlb/review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`

It must prove that the resulting single-GPU VM baseline is suitable for later LLM reproduction.

---

## 3. Track B execution

Execute:

`stage_specs/M4A_LLM_TRACE_METADATA_PREP.md`

M4A may proceed while Track A runs. It may perform web/artifact searches, local environment inventory, workload setup, tracer feasibility tests, small trace captures, metadata extraction, and trace validation as authorized by its spec.

If an exact artifact or exact synthetic-KV implementation is unavailable, record this as `UNKNOWN`/`PAPER_DETAIL_UNAVAILABLE`; do not silently design an approximation.

M4A must STOP before:

- implementing the paper's Segment Table in the simulator;
- modifying M1-M3 VM semantics;
- adding synthetic-KV performance injection to the simulator;
- claiming a self-collected trace is the authors' exact trace;
- starting M4B/M5.

---

## 4. Global acceptance and STOP rules

The repository `AGENTS.md` is authoritative. In particular, STOP immediately on:

- baseline transparency failure;
- request loss;
- duplicate wakeup;
- duplicate store/atomic side effect;
- recursive translation of PTE requests;
- multiple active walks for one translation key contrary to the frozen policy;
- unexplained nondeterminism;
- a required paper-exact detail that cannot be established and materially affects implementation;
- inability to push a modified source repository to the approved writable remote.

Do not weaken a directed test to continue the macro task.

---

## 5. Codex-owned reporting

Maintain:

`docs/vm_tlb/codex_handoff/LATEST_REPORT.md`

During a long target-mode run, update it at each macro-stage closeout so interruption still leaves a useful checkpoint.

Each stage pack must include at minimum:

- `README.md`
- `SOURCE_ANCHORS.md`
- `COMMIT_HISTORY.md`
- `CHANGED_FILES.md`
- `VALIDATION_SUMMARY.md`
- `OPEN_ISSUES.md`
- `RAW_LOG_INDEX.tsv`

Functional VM stages must additionally provide machine-checkable invariant/test results and representative structured statistics.

Large raw logs, traces, model weights, build directories, and copyrighted paper PDFs must not be committed.

---

## 6. Git requirements

Forbidden:

- `git add .`
- `git add -A`
- pushing to official upstream
- force-pushing shared research history without authorization

Stage explicit paths only. Keep structural refactors separate from functional changes when practical.

Track A commits should clearly indicate M1/M2/M3 semantics. Track B commits should clearly indicate M4A preparation and must remain free of VM-mechanism source changes.

---

## 7. Final STOP boundary

When Track A reaches M3 closeout and Track B reaches M4A closeout:

- push both research branches;
- update `LATEST_REPORT.md` with both track statuses and final SHAs;
- provide review-pack entry points;
- STOP.

**STOP BEFORE M4B / Segmentation implementation / synthetic-KV simulator injection / new AI-aware TLB mechanism.**
