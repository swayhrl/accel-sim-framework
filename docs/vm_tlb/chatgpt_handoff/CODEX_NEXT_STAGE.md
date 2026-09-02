# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF independently accepted**.

`G3-0`: **PASS**.

`G3-1 — PTE backend/request contract`: **PASS — accepted after namespace repair**.

Accepted G3-1 Core head:

`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

`G3-2A — Address Provenance Diagnostic`: **PASS — CASE A accepted**.

Framework G3-2A evidence:

`8eefe9d69764000f860871ca92770d986e7be0b6`

The first >49-bit request is a legitimate raw/coalesced global BFS store with 56-bit `SimVA`; VM-disabled and ideal-identity controls accept the same transaction. Therefore the generic M3 backend must not hard-code the target paper's 49-bit VA width.

## Next authorized execution

Execute only:

`G3-2B — generic trace-width extension and G3-2 resume`

Specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_2_TRACE_WIDTH_EXTENSION.md`

After G3-2B closes G3-2, STOP for ChatGPT review before G3-3/PWC.

## Mandatory read order

1. repository-root `AGENTS.md`
2. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
4. this file
5. `stage_specs/M3_G3_2_TRACE_WIDTH_EXTENSION.md`
6. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`
7. `stage_specs/M3_REFERENCE_MATERIALS.md`
8. `review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_ADDRESS_PROVENANCE_DIAG.md`
9. `review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_BLOCKED.md`
10. accepted M1/M2/G3-1 evidence and long-lived VM specs

Do not modify `chatgpt_handoff/*`.

## Source anchors

Core branch:

`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

Accepted Core semantic anchor:

`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

Framework branch:

`swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Fetch/pull latest Framework handoff before implementation.

## Architecture decision to implement

For generic M1-M3:

- raw/coalesced trace address remains `SimVA`;
- preserve identity-like data mapping `SimPA == SimVA`;
- do not mask/truncate/canonicalize generic SimVA;
- generic PTE backend VA width becomes configurable;
- current generic M3 configuration = **56 bits**;
- 49-bit configuration remains supported/tested for later target-paper use;
- more-than-configured-width requests remain explicit correctness stops.

This is a simulator trace/backend modeling decision, not a commercial SM86 VA-width claim.

## Required implementation and validation

Follow every gate in `M3_G3_2_TRACE_WIDTH_EXTENSION.md`.

At minimum:

1. remove the semantic hard-code that accepts only 49-bit generic VA;
2. make width/range arithmetic overflow-safe and configuration-derived;
3. prove non-overlap of 56-bit application identity-like addresses and the synthetic PTE-reserved range;
4. prove all 64KB/2MB × four-level PTE namespaces remain disjoint under 56-bit config;
5. keep original 49-bit namespace tests passing;
6. accept the exact former BFS offender without changing its raw SimVA/identity-like SimPA;
7. record a non-blocking high-bit/canonical-pattern audit over all available BFS transactions >=2^49 as `TRACE_ENCODING_OBSERVATION` only;
8. reimplement/selectively reuse the local G3-2 WIP only after inspecting it against the accepted source;
9. rerun real PTE request/response, L2/DRAM, multi-walker identity, one-kernel, BFS, LUD, M1 transparency and repaired M2 regressions;
10. prove zero PTE response misassociation, conservation and final MSHR/PWQ/walker quiescence.

The historical `stash@{0}` remains non-evidence. Do not blindly pop/drop it.

## PWC stop boundary

Do **not** enter G3-3 after G3-2 PASS.

Current PTE identities are sufficient for G3-2 physical-memory plumbing but are not yet an approved hierarchy-prefix/PTE-sharing model for PWC locality. ChatGPT will specify that separately after G3-2 closeout.

## Explicitly forbidden

Do not:

- canonicalize, mask or truncate raw SimVA;
- silently modulo-map PTE addresses;
- change TLB/MSHR/PWQ/replay semantics;
- expand to multi-ASID;
- implement PWC/G3-3;
- implement Segmentation, L2-TLB sub-entry or synthetic KV;
- implement page fault/migration/UVM/MCM;
- claim generic 56-bit mode is target-paper exact.

## Reporting

Maintain:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

and:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Update:

`docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/`

Commit/push safe Core + Framework results and STOP after G3-2 closeout for ChatGPT review.

## STOP conditions

STOP immediately on:

- width/range overflow or overlap;
- a trace request requiring more than configured 56-bit generic width;
- recursive PTE translation;
- PTE response identity failure/misassociation;
- request loss, duplicate wakeup, duplicate store/atomic effect;
- M1/M2 regression;
- deadlock or unexplained nondeterminism;
- source/provenance ambiguity;
- any need to change the approved generic width policy rather than implement it.
