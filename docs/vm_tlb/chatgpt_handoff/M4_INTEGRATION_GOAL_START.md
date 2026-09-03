# M4 integration Goal start — AUTHORIZED

Status: **AUTHORIZED NOW**.

This file supersedes `M4_INTEGRATION_GOAL_START_DRAFT.md` and the historical
Track-A `STOP / HOLD` wording once the startup instruction has fetched the
Track-A authorization HEAD containing this file.

The accepted inputs are now complete:

- Track-A M1-M3 VM baseline: PASS/accepted;
- Track-B M4A merge preparation: `M4A_MERGE_PREP_PASS_READY_FOR_INTEGRATION`;
- no GPU recapture is needed;
- no synthetic KV is authorized in this Goal.

## Exact immutable anchors

Core VM baseline:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Track-B accepted merge-prep Framework:

`e21ffebce280e6b932fb4556ef75c609ff54c326`

Track-B integration manifest:

`docs/vm_tlb/review_packs/M4A_MERGE_PREP/INTEGRATION_MANIFEST.md`

Manifest Git blob SHA at accepted B commit:

`291d749e7b96cc858f09335b052c6e37e5966b98`

Formal archive SHA256 values and semantic derivative hashes are frozen in:

`stage_specs/M4_INTEGRATION_AUTHORIZED_ADDENDUM.md`

The exact Track-A Framework authorization HEAD is supplied by the startup
instruction and must be this file's commit or a descendant containing all
current ChatGPT M4 handoff files.

## Mandatory read order

1. repository-root `AGENTS.md`
2. this `M4_INTEGRATION_GOAL_START.md`
3. `CURRENT_STATE.md`
4. `DISCUSSION_REFERENCE.md`
5. `CODEX_NEXT_STAGE.md`
6. `stage_specs/M4_INTEGRATION_AUTHORIZED_ADDENDUM.md`
7. `stage_specs/M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`
8. `stage_specs/M4I_AB_INTEGRATION_AND_REPLAY.md`
9. `stage_specs/M4C_LLM_BASELINE_CHARACTERIZATION.md`
10. `stage_specs/M4B_SEGMENTATION_REPRODUCTION.md`
11. Track-A `M1_M3_VM_BASELINE_CLOSEOUT/`
12. Track-B `M4A_MERGE_PREP/` at accepted B SHA
13. `paper_specs/SEGMENTATION_LLM_2026.md` and parameter/evidence ledgers

`M4_INTEGRATION_AUTHORIZED_ADDENDUM.md` overrides all unresolved placeholders,
old `DRAFT ONLY` status markers, and any conflicting planned values in the four
prepared M4 stage specs.

## Required fresh branches/worktrees

Do not reuse either historical A or B worktree for implementation.

Framework branch:

`hrl/vm-llm-m4b-v0`

from the exact Track-A authorization HEAD in the startup instruction.

Core branch:

`hrl/vm-llm-m4b-v0`

exactly from:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Do not wholesale-merge Track B. Use the path-scoped import contract and produce
`B_IMPORT_MANIFEST.tsv`.

## Continuous authorized target

Execute as one Goal with internal gates:

```text
M4I-0 admission / fresh branches
 -> M4I-1 path-scoped B import
 -> M4I-2 immutable artifact binding
 -> M4I-RF0 range-index/object-coverage safety check
 -> M4I-3 final-Core cold build + M1-M3 admission regressions
 -> M4I-4 49-bit/object metadata admission
 -> M4I-5 final-Core semantic parser smoke
 -> M4R formal replay policy + throughput/feasibility gate
 -> M4C real prefill/decode1 baseline translation characterization
 -> M4B-P paper paging/sub-entry baseline
 -> M4B-S Weight Segmentation on the same formal real traces
 -> M4B-CLOSEOUT
 -> STOP before M5 synthetic KV
```

Do not pause for ordinary successful transitions. Continue automatically when
each internal gate passes.

## Concrete evidence decisions already frozen

- both formal ROIs require only 47-bit VA;
- no decoded formal address is `>=2^49`;
- paper-facing 49-bit mode is therefore authorized without address rewriting;
- prefill semantic list = 692 COMPUTE + 32 NCCL;
- decode1 semantic list = 740 COMPUTE + 32 NCCL;
- primary paper-facing trace policy = `COMPUTE_ONLY_TP_PARTITION`;
- `FULL_RANK0` is required self-capture sensitivity/provenance;
- neither trace policy is author-exact;
- long-context synthetic KV remains outside this Goal.

Before object-specific M4C claims, execute the addendum's mandatory
`M4I-RF0` range-index safety check. This does not invalidate the immutable
capture or 49-bit evidence; it determines whether Track-B's historical
Weight/KV/UNKNOWN split can be reused unchanged or must be recomputed offline.

## Hard STOP conditions

Stop immediately on any condition defined in the master/addendum specs,
including:

- A/B source or archive/manifest hash mismatch;
- inability to preserve exact path-scoped import provenance;
- M1-M3 regression on the final Core lineage;
- corrected range-index audit revealing invalid historical object coverage and
  failure to recompute it exactly;
- parser/trace corruption on required compute kernels;
- legitimate formal SimVA outside the approved 49-bit paper contract;
- repeated lookup polling/port consumption;
- recursive PTE traffic or response misassociation;
- request loss or duplicate wakeup/store/atomic/data side effect;
- sub-entry implementation requiring a materially new approximation not covered
  by the authorized fallback;
- Segmentation changing non-weight paging semantics;
- a Weight segment hit still creating conventional L2-TLB/MSHR/PTW/PTE work;
- no-progress/deadlock under repository timing rules;
- provenance ambiguity.

Expected normal final STOP:

`M4B-CLOSEOUT`, before M5.

## Explicitly forbidden in this Goal

Do not:

- access/rent a GPU or recapture formal traces;
- modify/repack accepted formal archives;
- use Track-B's old parser Core as the integrated Core;
- mask/truncate/canonicalize formal addresses;
- tune parameters to force paper reference numbers;
- inject synthetic KV / emulate 12K long context;
- segment KV;
- add page faults/migration/UVM/MCM;
- broaden to multi-ASID study;
- implement a new AI-aware mechanism beyond target Segmentation.

Maintain integrated progress/report files:

- `docs/vm_tlb/codex_handoff/m4b/TARGET_PROGRESS.md`
- `docs/vm_tlb/codex_handoff/m4b/LATEST_REPORT.md`

After the final M4B closeout, push both integration branches and STOP for
ChatGPT review.
