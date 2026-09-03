# CODEX_NEXT_STAGE — integrated M4 Goal

## Status

Accepted prerequisites:

- `M1_M3_VM_BASELINE_CLOSEOUT`: PASS / ACCEPTED;
- `M4A_MERGE_PREP`: PASS / ACCEPTED FOR INTEGRATION.

Final VM Core anchor:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Accepted Track-B merge-prep Framework:

`e21ffebce280e6b932fb4556ef75c609ff54c326`

Accepted B integration-manifest blob:

`291d749e7b96cc858f09335b052c6e37e5966b98`

## Current authorization

**AUTHORIZED:** execute the integrated M4 Goal from the explicit start file:

`docs/vm_tlb/chatgpt_handoff/M4_INTEGRATION_GOAL_START.md`

Read the evidence-driven override before the prepared stage specs:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M4_INTEGRATION_AUTHORIZED_ADDENDUM.md`

The addendum supersedes old draft-only status markers and resolves the frozen
B evidence/decisions.

## Continuous target

Create fresh integration worktrees/branches and execute:

```text
M4I-0 admission
 -> M4I-1 path-scoped B import
 -> M4I-2 immutable artifact lock
 -> M4I-RF0 range-index/object-coverage safety check
 -> M4I-3 final-Core cold build + M1-M3 regression
 -> M4I-4 49-bit/object metadata admission
 -> M4I-5 final-Core parser smoke
 -> M4R replay policy + throughput/feasibility
 -> M4C real LLM baseline translation characterization
 -> M4B-P paper paging/sub-entry baseline
 -> M4B-S Weight Segmentation on real prefill/decode1
 -> M4B-CLOSEOUT
 -> STOP before M5
```

Do not stop for ordinary successful transitions. Continue automatically after
each passing internal gate.

## Branch/source rule

Framework:

`hrl/vm-llm-m4b-v0`

must branch from the exact Track-A authorization HEAD supplied by the startup
instruction.

Core:

`hrl/vm-llm-m4b-v0`

must branch exactly from:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`.

Do not reuse historical A/B implementation worktrees and do not wholesale merge
Track B. Import B-owned paths from exact SHA `e21ffeb...` and record every
source/destination blob in `B_IMPORT_MANIFEST.tsv`.

## Frozen formal evidence

- prefill: 724 entries = 692 COMPUTE + 32 NCCL;
- decode1: 772 entries = 740 COMPUTE + 32 NCCL;
- both formal full address scans require only 47-bit VA;
- zero decoded addresses are `>=2^49`;
- paper-facing 49-bit mode is authorized without address rewriting;
- primary paper-facing trace policy is `COMPUTE_ONLY_TP_PARTITION`;
- `FULL_RANK0` remains required self-capture sensitivity/provenance;
- no synthetic KV is allowed before the final M4B stop.

Exact archive/list/coverage hashes are in the authorized addendum.

## Mandatory M4I-RF0 correction

Before using B's historical Weight/KV/UNKNOWN object split for M4C or Segment
registration, resolve the range-index ordering risk described in the addendum.

Required outcome:

- corrected integration analyzer globally sorts merged ranges and asserts
  monotonic starts;
- tests cover KV below and above Weight;
- resumable partial identity is strengthened to bind analysis/range-map
  semantics;
- if actual historical B sidecar ranges were already monotonic, document and
  retain B object totals;
- if not, recompute affected object coverage offline before M4C.

This does not reopen capture or the already accepted 49-bit/global-address
result.

## M4C / M4B policy

M4C is behavior-neutral characterization only. It must establish object-specific
TLB/MSHR/walker/PWC/PTE/latency behavior and L2-TLB incoming-object -> victim-
object replacement evidence before Segmentation.

M4B-P must first audit the paper/reference source for L2 sub-entry semantics. If
still unavailable, the prepared `REFERENCE_APPROX_SUBENTRY_16` fallback is
pre-authorized only as `PAPER_PAGING_BASELINE_APPROX`.

M4B-S segments only the frozen contiguous Weight range. Segment + L1 lookup are
parallel; default Segment service latency equals L1 service latency as an
explicit modeling decision. A Segment hit must suppress conventional L2-TLB,
MSHR/PWQ/walker/PWC/PTE activity and conventional Weight TLB fills. A Segment
miss reuses the already completed L1 result and must not re-probe L1.

## Hard STOP

Follow all hard-stop rules in the start/addendum/master specs. In particular,
STOP on source/artifact mismatch, unresolved import provenance, M1-M3 regression,
required compute trace corruption, legitimate SimVA outside the approved
paper-width contract, repeated lookup polling, recursive/misassociated PTE
traffic, duplicate side effects, materially new unapproved sub-entry semantics,
Segmentation changing non-weight behavior, Segment hits still producing paging
work, deadlock/no-progress, or provenance ambiguity.

## Final boundary

After `M4B-CLOSEOUT`:

- commit/push both integration branches;
- complete the M4 review packs and integrated report/progress ledgers;
- STOP for ChatGPT review.

Do not start M5 synthetic-KV/12K pressure, KV segmentation, new AI-aware
mechanisms, page faults/migration/UVM/MCM, or multi-ASID work.
