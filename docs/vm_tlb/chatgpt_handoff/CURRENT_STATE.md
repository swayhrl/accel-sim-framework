# Current state

## Track A status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF independently accepted**.

Accepted repaired M2 execution head:

`3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`

The registered-waiter retry pollution is closed: already accepted `(translation key, waiter UID)` requests remain pending without re-consuming/probing L1/L2 TLB resources, while new waiters still perform their first lookup and may merge. Cold M1/G2 regressions, disabled/ideal transparency, one-kernel/LUD/BFS functional replays, kernel-persistence evidence, and latency-sensitivity checks all pass.

## M3 G3-1 review result

`G3-0`: **PASS**.

`G3-1 — PTE backend / physical request contract`: **PASS — accepted after namespace repair**.

Accepted Core G3-1 head:

`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

The former 64KB/2MB PTE-address alias is closed. The accepted backend uses one fixed maximum VPN namespace width for every `(page-size-class, level)` namespace, and PTE requests remain physical/non-recursive. That acceptance was for the then-configured 49-bit generic backend; G3-2A has since shown that generic trace SimVA cannot be globally constrained to 49 bits.

## G3-2 / G3-2A review result

`G3-2 — real PTE L2/DRAM integration`: **BLOCKED pending width-contract repair; plumbing evidence is positive but unaccepted source remains local/uncommitted**.

Before the stop, local G3-2 proved:

- explicit `PTE_ACC_R` requests are physical and translation-bypassing;
- they bypass shader L1D and traverse real interconnect/L2/DRAM resources;
- walkers advance only on matching PTE responses;
- one-kernel replay produced `4/4` PTE requests/responses, all DRAM, zero misassociation;
- BFS produced both L2-resident and DRAM PTE returns with zero misassociation before reaching the old width assertion.

`G3-2A — Address Provenance Diagnostic`: **PASS — CASE A independently accepted**.

Framework diagnostic evidence head:

`8eefe9d69764000f860871ca92770d986e7be0b6`

The first >49-bit request is a real trace-derived BFS kernel-7 global store, not local/param-local, not a sentinel, and not recursive PTE traffic:

- raw lane address: `0x00fffdc0000000cd`
- coalesced `SimVA`: `0x00fffdc0000000c0`
- required width: 56 bits
- operation: `STG.E.SYS`, `GLOBAL_ACC_W`
- VM-disabled and VM-ideal-identity controls accept the same transaction and finish normally.

Complete disabled/ideal BFS controls observed 49,047 global transactions, 12 at/above `2^49`, and a maximum required width of 56 bits. The available LUD run stayed within 47 bits. This evidence establishes a **generic simulator trace-width requirement**, not a commercial GPU architectural VA-width claim.

## Architecture decision after G3-2A

For the generic M1-M3 VM substrate:

- keep the frozen M1 meaning: the raw/coalesced trace address is `SimVA`;
- preserve resident identity-like data mapping, `SimPA == SimVA`;
- do not mask, truncate, canonicalize or rewrite generic `SimVA`;
- make generic PTE-backend VA width configurable;
- use **56 bits** for the current generic M3 trace-driven baseline, because that is the maximum width established by the complete available BFS control;
- requests requiring more than the configured width remain hard correctness stops;
- the target Segmentation paper's 49-bit VA remains a later **paper-specific configuration**, not a generic trace contract.

The exact high address is suggestive of a 49-bit payload encoded with repeated high bits. This is worth recording as `TRACE_ENCODING_OBSERVATION` for the later paper-specific trace adapter, but it is not authorization to canonicalize generic M3.

## Current authorization

Execute only:

`G3-2B — generic trace-width extension and G3-2 resume`

Specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_2_TRACE_WIDTH_EXTENSION.md`

Required outcome:

1. generic page-table width is configurable and the current generic M3 run uses 56 bits;
2. 49-bit configuration remains directed-tested for later paper-specific use;
3. application and PTE physical ranges remain provably disjoint with overflow-safe namespace arithmetic;
4. the exact former BFS offender translates without rewriting its raw `SimVA`/identity-like `SimPA`;
5. real G3-2 PTE L2/DRAM plumbing passes integrated validation;
6. STOP before G3-3/PWC.

## Important PWC/locality boundary

G3-1/G3-2 currently use a collision-free deterministic flat per-level/full-VPN synthetic PTE identity. This is sufficient for G3-2 memory-path plumbing, but it is not yet an approved hierarchy-prefix/PTE-sharing model for PWC locality.

Therefore G3-2B must STOP after G3-2 closeout. Before G3-3, ChatGPT will separately decide and specify the generic hierarchy-prefix/PTE-sharing semantics. Do not present current PTE L2-hit behavior as paper-exact radix locality.

Current M3 remains one simulated address space / ASID-0 path. Do not claim multi-ASID PTE physical separation.

## Frozen / accepted source anchors

Core/GPGPU-Sim:

- baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- accepted repaired M2: `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`
- accepted G3-1 namespace repair: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

Framework/Accel-Sim:

- baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- M2-RF evidence: `c12ad7bc9fb6865e97ff8b65c215490a5d92305a`
- G3-1-RF evidence: `329b80b27a2db8709e2b2a0609f4783789552d98`
- G3-2 blocked evidence: `cc055d3a4b044136b37a1ab2ccba8f4a8a360ba5`
- G3-2A provenance evidence: `8eefe9d69764000f860871ca92770d986e7be0b6`

Branches:

- Core: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Frozen modeling decisions

- coalesced trace address is simulator `SimVA`; translation produces `SimPA`; preserve both;
- baseline data mapping is resident and identity-like (`SimPA == SimVA`);
- translation operates on coalesced transactions before real data-cache access;
- generic M3 trace/backend width is configurable; current generic configuration is 56-bit after G3-2A;
- paper-specific 49-bit width remains separate and must be explicitly selected later;
- M1-M3 excludes page fault/migration/UVM oversubscription/MCM;
- TLB persists across ordinary kernels in the simulated context;
- M2 zero-hit-latency TLB with finite ports is functional only; timing-realistic lookup latency belongs to M3;
- M3 PTE requests are physical and non-recursive;
- page-table hierarchy/PWC/timing details not exposed by the target paper remain explicit generic `MODELING_DECISION`s.

## STOP boundary

STOP on any width/range overflow, application/PTE physical-range overlap, recursive PTE translation, response misassociation, request loss, duplicate wakeup/store/atomic, M2 regression, deadlock, or provenance ambiguity.

After G3-2B closes G3-2, STOP before G3-3/PWC for a separate hierarchy/locality architecture review.
