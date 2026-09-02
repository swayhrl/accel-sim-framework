# Current state

## Track A status

`M1_VM_CORE_FOUNDATION` has been independently reviewed by ChatGPT and is **PASS**.

Reviewed source anchors:

- Core/GPGPU-Sim M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- Framework Track-A branch: `hrl/vm-m1-m3-v0`
- Framework M1 closeout reported by Codex: `ccee0a821c379b1fb8ac183c3519ed6b3762b141`

Review entry:
`docs/vm_tlb/review_packs/M1_VM_CORE_FOUNDATION/README.md`

M1 evidence accepted:

- VM-disabled path matches frozen baseline on required architectural counters;
- ideal identity translation matches VM-disabled behavior;
- QV100 LUD-64, RTX3070 LUD-64, and BFS-4096 transparency runs pass;
- `SimVA == SimPA` in identity mode;
- ideal/disabled modes add zero translation stall;
- directed page-offset/cross-page helper tests pass;
- M1 contains no functional TLB/MSHR/PTW implementation.

### Non-blocking M2 caution

The M1 substrate initializes `SimPA` numerically from the original address before functional translation, while validity is represented by translation-applied state. M2 must preserve the invariant that no consumer treats `SimPA` as completed translation before completion. Replay must not re-enter or double-apply translation for an already translated request.

## Current authorization

Track A is now authorized to execute **M2 -> M3 continuously in Codex target mode**.

Execution/monitoring source:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M2_M3_TARGET_MODE.md`

M2 source spec:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M2_FUNCTIONAL_TRANSLATION.md`

M3 source spec:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_TIMING_REALISTIC_BASELINE.md`

M3 evidence/reference boundary:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_REFERENCE_MATERIALS.md`

Codex maintains target progress in:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

M2 may transition automatically to M3 only after the complete M2 stage gate passes. No human pause is required between M2 and M3 when every gate is PASS. Any failed correctness/provenance gate is an immediate STOP.

## Frozen source anchors

- Core/GPGPU-Sim baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- M1 Core: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- Framework/Accel-Sim baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- Writable Framework: `swayhrl/accel-sim-framework`
- Writable Core: `swayhrl/gpgpu-sim`
- Track-A branches: `hrl/vm-m1-m3-v0` in both repositories

## Frozen M1-M3 modeling decisions

- Trace address is simulator `SimVA` by modeling contract, not a claim about exact internal NVIDIA address stage captured by NVBit.
- Translation produces `SimPA`; preserve both identities.
- Identity bring-up uses `SimPPN = SimVPN`, so data `SimPA == SimVA`.
- Translation operates on approved coalesced transactions before real L1D/data-cache access.
- M1-M3 model resident-memory address translation only: no page fault, migration, UVM oversubscription, or CPU fault service.
- TLB state persists across ordinary kernels in one simulated context unless explicitly invalidated/reset.
- PTE requests in M3 are physical and must never recursively translate.

## M3 evidence boundary

M3 builds a reusable generic timing-realistic VM/TLB/PTW substrate. It does not yet claim exact reproduction of the Segmentation paper's PTW or sub-entry implementation.

Known target-paper parameters may be recorded separately from generic M3 choices. Any unavailable PTW/PWC/latency detail remains `UNKNOWN` or an explicitly documented `MODELING_DECISION`. CLAP/legacy `dev-uvm` values/code are references only and must not be relabeled as target-paper exactness.

## STOP boundary

M2 must STOP before M3 if any required directed test, conservation law, replay invariant, or transparency check fails.

M3 must STOP on recursive PTE translation, PTE response misassociation, request loss, deadlock, duplicate wakeup/side effect, unexplained nondeterminism, or timing/model ambiguity requiring an unapproved semantic change.

After M3 PASS and M1-M3 macro closeout, STOP before M4B, Segmentation, synthetic-KV injection, or new AI-aware TLB mechanisms.
