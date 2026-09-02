# Current state

## Track A status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF independently accepted**.

Accepted repaired M2 Core:
`3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`

`G3-0`: **PASS**.

`G3-1 — PTE backend / physical request contract`: **PASS — accepted after namespace repair**.

Accepted G3-1 Core:
`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

`G3-2A — address provenance diagnostic`: **PASS — CASE A accepted**.

It proved that generic Accel-Sim trace/coalesced `SimVA` can legitimately exceed
49 bits.  The first offender was a real BFS global store with
`SimVA=0x00fffdc0000000c0`, and the same transaction completed in disabled and
ideal-identity modes.

## G3-2B / G3-2 review result

`G3-2B — generic trace-width extension`: **PASS — independently accepted**.

`G3-2 — real PTE L2/DRAM integration`: **PASS — independently accepted**.

Accepted Core:
`965bd8e188175731c31cabfef6c3bdeb7c59e1fd`

Framework evidence head reported by Codex:
`dbbd9d8360121aeda553eaf9365073e7332018bf`

Accepted generic address contract:

- raw/coalesced trace address remains `SimVA`;
- generic resident data mapping remains identity-like, `SimPA == SimVA`;
- generic backend width is configurable;
- current generic M3 baseline uses 56-bit SimVA;
- retained 49-bit configuration is directed-tested for later paper-specific use;
- no masking/truncation/canonicalization is performed;
- application identity-like physical range is `[0,2^56)`;
- synthetic PTE physical range is disjoint and overflow-checked;
- requests wider than configured width remain correctness stops.

Accepted G3-2 real-memory behavior:

- PTE reads use explicit `PTE_ACC_R` traffic;
- PTE requests are physical and translation-bypassing;
- they bypass shader L1D and consume real request/response interconnect, L2 and
  lower-memory/DRAM resources;
- walkers advance only after the matching PTE response;
- response association preserves request identity even when L2 aligns its
  working address;
- complete BFS and LUD replays pass with zero response misassociation and final
  MSHR/PWQ/walker quiescence;
- the former 56-bit BFS offender completes without rewriting SimVA/SimPA;
- M1/M2/G3 directed regressions and release build remain PASS.

The 12 observed BFS addresses above `2^49` are retained only as
`TRACE_ENCODING_OBSERVATION`; they are not canonicalized or used to redefine
generic SimVA.

## Remaining hierarchy/PWC ambiguity

G3-2 intentionally used a collision-free flat `(page-size-class, level, full
VPN)` synthetic PTE identity.  That was sufficient to prove physical PTE
request plumbing, but it is not an acceptable final locality model for PWC:
upper-level PTE sharing would otherwise be determined by an arbitrary flat
identity rather than a radix-prefix relationship.

Therefore G3-3 cannot use the old flat identity unchanged.

## Architecture decision for next gate

Authorize a generic balanced radix-prefix hierarchy as `MODELING_DECISION`.
For each page-size class:

```text
B = virtual_address_bits - log2(page_size)
L = levels
r = ceil(B/L)
top = B - r*(L-1)
level widths = [top, r, r, ...]
```

Examples:

- 56-bit / 64KB: `[10,10,10,10]`;
- 56-bit / 2MB: `[8,9,9,9]`;
- 49-bit / 64KB: `[6,9,9,9]`;
- 49-bit / 2MB: `[7,7,7,7]`.

At walk level `l`, PTE identity is based on the VPN prefix through that level,
not the full VPN.  Physical PTE subranges are deterministic and non-overlapping
per `(page-size-class, level)`, with overflow-safe prefix-sum sizing.

This is a generic simulator hierarchy, not an NVIDIA hardware claim and not a
Segmentation-paper exact page table.

For G3-3, the generic PWC caches intermediate/non-leaf PTEs only, keyed by
`(ASID, page-size-class, level, prefix)`.  Default finite organization is 128
entries, fully associative LRU; OFF and IDEAL diagnostic modes are required.
The 128-entry default is motivated only by other recent GPU VM simulation work
(e.g. CLAP), not by the target Segmentation paper.

## Current authorization

Execute:

`G3-2C — hierarchy-prefix PTE identity`

then, only if it PASSes, automatically continue to:

`G3-3 — generic PWC`.

Specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_2C_HIERARCHY_AND_G3_3_PWC.md`

After G3-3 PASS, STOP for ChatGPT review before G3-4.

## Frozen / accepted source anchors

Core/GPGPU-Sim:

- baseline: `73774727e25fadf89df6f30ef5cf014091115db7`
- M1: `82fa2bc79cf09dd137073431dc41e48bc2f30cec`
- accepted repaired M2: `3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`
- accepted G3-1: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`
- accepted G3-2B/G3-2: `965bd8e188175731c31cabfef6c3bdeb7c59e1fd`

Framework/Accel-Sim:

- baseline: `3016c658f810bdae9a14bf4534ee99e9945eedae`
- M2-RF evidence: `c12ad7bc9fb6865e97ff8b65c215490a5d92305a`
- G3-1-RF evidence: `329b80b27a2db8709e2b2a0609f4783789552d98`
- G3-2A evidence: `8eefe9d69764000f860871ca92770d986e7be0b6`
- G3-2B/G3-2 evidence: `dbbd9d8360121aeda553eaf9365073e7332018bf`

Branches:

- Core: `swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`
- Framework: `swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

## Frozen modeling decisions

- coalesced trace address is simulator `SimVA`; translation produces `SimPA`;
- resident baseline data mapping is identity-like;
- generic current address width = 56 bits; paper-specific 49-bit mode remains
  separate;
- translation occurs after coalescing and before real data-cache access;
- PTE traffic is physical, non-recursive and uses real L2/DRAM resources;
- current M1-M3 is resident-memory, single-address-space/ASID-0 for claims;
- TLB persists across ordinary kernels;
- page faults/migration/UVM/MCM/Segmentation/sub-entry are outside M3;
- hierarchy and PWC details not exposed by the target paper are explicit generic
  `MODELING_DECISION`s.

## STOP boundary

STOP on hierarchy namespace collision/overflow, application/PTE range overlap,
recursive PTE translation, response misassociation, request loss, duplicate
wakeup/store/atomic, M1/M2 regression, PWC determinism failure, deadlock, or
provenance ambiguity.

After G3-3 PASS, STOP before G3-4 for review.
