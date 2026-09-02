# Current state

## Track A status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF independently accepted**.

Accepted repaired M2 execution head:

`3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`

The registered-waiter retry pollution is closed: already accepted `(translation key, waiter UID)` requests remain pending without re-consuming/probing L1/L2 TLB resources, while new waiters still perform their first lookup and may merge. Cold M1/G2 regressions, disabled/ideal transparency, one-kernel/LUD/BFS functional replays, kernel-persistence evidence, and latency-sensitivity checks all pass.

## M3 G3-1 review result

`G3-0`: **PASS**.

`G3-1 — PTE backend / physical request contract`: **PASS — independently accepted after namespace repair**.

Accepted Core G3-1 repaired head:

`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

Framework G3-1-RF evidence head before this handoff:

`329b80b27a2db8709e2b2a0609f4783789552d98`

The former cross-page-size PTE-address alias is closed. The generic backend now uses one fixed 33-bit maximum VPN namespace width for every `(page-size-class, level)` namespace. Directed tests cover the explicit old collision and all 64KB/2MB × four-level namespace min/max boundaries. PTE requests remain physical and translation-bypassing; application and PTE physical ranges remain separated. M1/M2 regressions and the bounded functional replay remain clean.

This accepts G3-1 as a **generic simulator contract**, not as target-paper exact PTW behavior.

## Current authorization

Resume the existing target-mode M3 goal at:

`G3-2 — real PTE L2/DRAM integration`

Source specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_TIMING_REALISTIC_BASELINE.md`

The original continuous target may proceed through G3-2 -> G3-3 -> G3-4 -> G3-5 -> G3-CLOSEOUT only when each internal gate passes. STOP on any invariant/provenance failure.

The reported uncommitted G3-2 WIP remains in Core `stash@{0}`. It is not evidence and must not be blindly popped. Inspect its diff against the accepted Core head first; selectively reuse only code that still satisfies the current M2/G3-1 contracts. Reimplement conflicting pieces rather than weakening accepted semantics.

## Important generic-page-table locality boundary

The accepted G3-1 namespace encoding proves collision-free deterministic physical PTE identities. It does **not**, by itself, prove that upper-level PTE physical-address sharing exactly matches a conventional hardware radix tree or the Segmentation paper.

Therefore:

- G3-2 may proceed to prove physical/non-recursive requests, real L2/DRAM resource use, response identity, and walker blocking;
- do not present G3-2 PTE L2-hit behavior as paper-exact page-table locality;
- before G3-3/PWC and certainly before G3-5 timing characterization, explicitly define/document the generic hierarchy-prefix/PTE-sharing semantics used by PWC and page-table locality. If the current flat per-level/full-VPN identity is retained, label it as a `MODELING_DECISION` and quantify the implication; if conventional prefix sharing is implemented, directed-test it;
- current M3 v0 remains one simulated address space / ASID-0 execution path; do not claim multi-ASID PTE-physical separation without extending the backend.

## G3-2 hard requirements

G3-2 must establish that each required PTE step:

- creates an explicit physical request and never recursively translates;
- bypasses L1D by the approved generic policy and enters the real L2/lower-memory timing path;
- consumes actual shared queues/cache-MSHR/interconnect/DRAM resources rather than statistics-only delay;
- advances the walker only after the matching response;
- preserves request/walk identity with multiple outstanding translations;
- produces separately observable PTE vs data traffic;
- passes deterministic L2-hit, forced-DRAM, response-identity, and shared-resource-pressure tests;
- preserves all repaired M2 replay/store/atomic/conservation invariants.

## Frozen / accepted source anchors

Core/GPGPU-Sim:

- baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- accepted repaired M2 execution head: `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`
- G3-1 provisional parent: `8c613a356e6a146951cd59c9929046c6c4cfd856`
- accepted G3-1 namespace repair: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

Framework/Accel-Sim:

- baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- M2 dependency fix: `4012be3606c300d11e7b34826ee1cb22b0852b93`
- M2-RF evidence: `c12ad7bc9fb6865e97ff8b65c215490a5d92305a`
- G3-1-RF evidence: `329b80b27a2db8709e2b2a0609f4783789552d98`

Branches:

- Core: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Frozen modeling decisions

- trace address is simulator `SimVA`; translation produces `SimPA`; preserve both;
- baseline data mapping remains resident and identity-like (`SimPPN=SimVPN`);
- translation operates on coalesced transactions before real data-cache access;
- M1-M3 excludes page fault/migration/UVM oversubscription/MCM;
- TLB persists across ordinary kernels in the simulated context;
- M2 zero-hit-latency TLB with finite ports is functional only; timing-realistic lookup latency belongs to M3;
- M3 PTE requests are physical and non-recursive;
- page-table organization, PWC and timing details not exposed by the target paper remain explicit generic `MODELING_DECISION`s.

## STOP boundary

STOP immediately on recursive PTE translation, response misassociation, request loss, duplicate wakeup/store/atomic, deadlock, unexplained early walker progress, M2 regression, source/provenance ambiguity, or a new modeling ambiguity that materially changes the approved generic architecture.

After M3 PASS and `M1_M3_VM_BASELINE_CLOSEOUT`, STOP before Segmentation/sub-entry/synthetic-KV/new AI-aware mechanisms.