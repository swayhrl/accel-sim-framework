# Future M4 integration Goal start — DRAFT / NOT AUTHORIZED

This file is intentionally **NOT AUTHORIZED YET**.

Do not execute it while Track B is still running `M4A_MERGE_PREP`.

After Track B finishes, ChatGPT will review the merge-prep evidence, replace the
placeholders below, make any required small corrections to the stage specs, and
publish a separate explicit `AUTHORIZED` start file.  At that point the goal is
intended to run continuously through M4B closeout unless a hard STOP condition
is triggered.

## Planned source anchors

Framework Track-A frozen integration start:

`<A_INTEGRATION_HANDOFF_SHA>`

Core frozen VM baseline:

`5ba17a1ba88b8e8ec0f9505a7e684c81df8f0b7d`

Accepted Track-B merge-prep Framework:

`<B_ACCEPTED_FRAMEWORK_SHA>`

Accepted Track-B integration manifest:

`<B_INTEGRATION_MANIFEST_PATH_AND_SHA>`

## Planned new branches

Framework:

`hrl/vm-llm-m4b-v0`

Core:

`hrl/vm-llm-m4b-v0`

## Planned continuous target

```text
M4I-0 admission / clean integration branches
 -> M4I-1 path-scoped B import
 -> M4I-2 immutable artifact binding
 -> M4I-3 final-Core build + M1-M3 admission regressions
 -> M4I-4 address-domain / metadata audit
 -> M4I-5 integrated parser smoke
 -> M4R replay-policy / feasibility gate
 -> M4C LLM baseline translation characterization
 -> M4B-P paper paging/sub-entry baseline
 -> M4B-S weight Segmentation on formal prefill/decode1
 -> M4B-CLOSEOUT
 -> STOP before M5 synthetic KV
```

## Mandatory future read order

1. repository-root `AGENTS.md`
2. authorized replacement for this start file
3. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
4. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
5. `docs/vm_tlb/chatgpt_handoff/CODEX_NEXT_STAGE.md`
6. `stage_specs/M4_INTEGRATION_TO_SEGMENTATION_MASTER.md`
7. `stage_specs/M4I_AB_INTEGRATION_AND_REPLAY.md`
8. `stage_specs/M4C_LLM_BASELINE_CHARACTERIZATION.md`
9. `stage_specs/M4B_SEGMENTATION_REPRODUCTION.md`
10. M1-M3 final closeout pack
11. accepted M4A merge-prep pack/integration manifest
12. paper specification / parameter ledgers

## Planned normal execution policy

Do not stop for ordinary successful internal gate transitions.

Automatically continue when each gate passes.

Hard STOP only on the explicit conditions in the stage specs, including source
or artifact mismatch, 49-bit address-contract failure requiring an unapproved
rewrite, M1-M3 regression, trace/parser corruption, sub-entry provenance
conflict requiring a new architecture decision, VM conservation failure,
Segmentation affecting non-weight semantics, deadlock/no-progress, or
provenance ambiguity.

## Explicitly not part of this goal

- long-context synthetic-KV injection / 12K pressure;
- segmenting KV;
- new AI-aware VM mechanism beyond target Segmentation;
- page fault/migration/UVM;
- MCM/chiplet behavior;
- multi-ASID study.
