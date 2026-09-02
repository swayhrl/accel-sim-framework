# Current state

## Track A status

`M1_VM_CORE_FOUNDATION` has been independently reviewed by ChatGPT and is **PASS**.

Reviewed source anchors:

- Core/GPGPU-Sim M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- Framework M1 closeout branch: `hrl/vm-m1-m3-v0`
- Framework closeout HEAD reported by Codex: `ccee0a821c379b1fb8ac183c3519ed6b3762b141`

Review entry:
`docs/vm_tlb/review_packs/M1_VM_CORE_FOUNDATION/README.md`

M1 evidence accepted:

- VM-disabled path matches the frozen baseline on the required key architectural counters;
- ideal identity translation matches VM-disabled behavior;
- QV100 LUD-64, RTX3070 LUD-64, and BFS-4096 transparency runs pass;
- `SimVA == SimPA` in identity mode;
- ideal/disabled modes add zero translation stall;
- directed page-offset and cross-page helper tests pass;
- M1 contains no functional TLB/MSHR/PTW implementation.

### Non-blocking M2 caution

The M1 substrate initializes `SimPA` numerically from the original address before functional translation, while validity is represented by the translation-applied state. M2 must preserve the invariant that no consumer treats `SimPA` as a completed physical translation before translation has actually completed. Replay must not re-enter or double-apply translation for an already translated request.

## Next authorized Track A work

Proceed directly to:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M2_FUNCTIONAL_TRANSLATION.md`

If M2 PASS, continue automatically to M3 under the existing target-mode macro authorization.

Do not repeat M1 implementation unless a later correctness failure proves M1 itself is implicated.

## Frozen source anchors

- Core/GPGPU-Sim baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- Framework/Accel-Sim baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- Writable Framework: `swayhrl/accel-sim-framework`
- Writable Core: `swayhrl/gpgpu-sim`

## Frozen M1-M3 modeling decisions

- Trace address is simulator `SimVA` by modeling contract, not a claim about the exact internal NVIDIA address stage captured by NVBit.
- Translation produces `SimPA`; preserve both identities.
- Identity bring-up uses `SimPPN = SimVPN`, so data `SimPA == SimVA`.
- Translation operates on approved coalesced memory transactions before real L1D/data-cache access.
- M1-M3 model resident-memory address translation only: no page fault, migration, UVM oversubscription, or CPU fault service.
- TLB state persists across ordinary kernels in one simulated context unless explicitly invalidated/reset.
- PTE requests in M3 are physical and must never recursively translate.

## STOP boundary

M2 must STOP before M3 if any required directed test or correctness invariant fails. Performance characterization remains blocked by deadlock, request loss, duplicate wakeup, duplicate store/atomic side effect, recursive PTE translation, unexplained nondeterminism, or baseline-transparency failure.
