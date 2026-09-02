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

Framework G3-1-RF evidence head:

`329b80b27a2db8709e2b2a0609f4783789552d98`

The former cross-page-size PTE-address alias is closed. The generic backend uses one fixed 33-bit maximum VPN namespace width for every `(page-size-class, level)` namespace. Directed tests cover the explicit old collision and all 64KB/2MB × four-level namespace min/max boundaries. PTE requests remain physical and translation-bypassing; application and PTE physical ranges remain separated for the accepted 49-bit generic backend.

This accepts G3-1 as a **generic simulator contract**, not as target-paper exact PTW behavior.

## G3-2 current status

`G3-2 — real PTE L2/DRAM integration`: **BLOCKED — correctness STOP**.

Framework blocked-evidence head reported by Codex:

`cc055d3a4b044136b37a1ab2ccba8f4a8a360ba5`

Core remains at the accepted G3-1 head; G3-2 source is local/uncommitted and is not accepted evidence.

What G3-2 established before the stop:

- explicit `PTE_ACC_R` requests are physical and translation-bypassing;
- they bypass shader L1D and can traverse real interconnect/L2/DRAM resources;
- walkers wait for matching PTE responses;
- one-kernel replay produced `4/4` PTE requests/responses, all DRAM, zero misassociation;
- an earlier completed BFS kernel produced both L2-resident and DRAM PTE responses with zero misassociation.

The later BFS kernel then reached a translation key whose VPN violates the G3-1 backend's hardcoded 49-bit VA contract and asserted before G3-2 could close.

### Important review decision

Do **not** widen, truncate, mask, canonicalize, or bypass the offending address yet.

The M1 long-lived contract names the transaction address `SimVA` and preserves identity-like `SimPA == SimVA`; it did not independently freeze a 49-bit width for every Accel-Sim trace/simulator address. Conversely, the Segmentation paper's 49-bit VA assumption is target-paper-specific and does not prove that every generic simulator address is a 49-bit GPU VA.

The current evidence does not record the exact offending `SimVA`, memory-space class, kernel/PC, access type, or whether the value came directly from the trace versus simulator local/generic-address linearization. Therefore an address-width/backend redesign is not yet authorized.

## Current authorization

Execute only:

`G3-2A — Address Provenance Diagnostic`

Source specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_2_ADDRESS_PROVENANCE_DIAG.md`

The diagnostic must determine the exact provenance of the >49-bit request and STOP for ChatGPT review. G3-2 semantic changes, G3-3/PWC, and later M3 gates remain unauthorized.

## Important generic-page-table locality boundary

The accepted G3-1 namespace encoding proves collision-free deterministic physical PTE identities only within its currently accepted 49-bit generic backend. It does **not**, by itself, prove that upper-level PTE physical-address sharing exactly matches a conventional hardware radix tree or the Segmentation paper.

Before G3-3/PWC and certainly before G3-5 timing characterization, explicitly define/document the generic hierarchy-prefix/PTE-sharing semantics used by PWC and page-table locality. If conventional prefix sharing is implemented, directed-test it; if a flatter synthetic model is retained, label it `MODELING_DECISION` and quantify the locality implication.

Current M3 v0 remains one simulated address space / ASID-0 execution path; do not claim multi-ASID PTE physical separation without extending the backend.

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
- G3-2 blocked evidence: `cc055d3a4b044136b37a1ab2ccba8f4a8a360ba5`

Branches:

- Core: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Frozen modeling decisions

- trace/coalesced transaction address is simulator `SimVA`; translation produces `SimPA`; preserve both;
- baseline data mapping remains resident and identity-like (`SimPPN=SimVPN`);
- translation operates on coalesced transactions before real data-cache access;
- M1-M3 excludes page fault/migration/UVM oversubscription/MCM;
- TLB persists across ordinary kernels in the simulated context;
- M2 zero-hit-latency TLB with finite ports is functional only; timing-realistic lookup latency belongs to M3;
- M3 PTE requests are physical and non-recursive;
- page-table organization, PWC and timing details not exposed by the target paper remain explicit generic `MODELING_DECISION`s;
- **no generic VA-width change is frozen yet beyond the accepted G3-1 backend; G3-2A must establish the provenance of addresses that violate it.**

## STOP boundary

STOP immediately on recursive PTE translation, response misassociation, request loss, duplicate wakeup/store/atomic, deadlock, M2 regression, source/provenance ambiguity, or any attempt to change VA width/address canonicalization/PTE namespace before the G3-2A provenance evidence is reviewed.

After G3-2A evidence is pushed, STOP for ChatGPT review. Do not enter G3-3.
