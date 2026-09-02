# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF independently accepted**.

Accepted M2 execution head:
`3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`

`G3-0`: **PASS**.

`G3-1 — PTE backend/request contract`: **PASS — independently accepted after G3-1-RF namespace repair**.

Accepted G3-1 Core head:
`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

Framework G3-1-RF evidence head before this handoff:
`329b80b27a2db8709e2b2a0609f4783789552d98`

The fixed 33-bit maximum VPN namespace removes the former 64KB/2MB alias; all eight page-size-class/level namespace boundaries are directed-tested. PTE requests remain physical/non-recursive and M2 regressions remain clean.

## Next authorized execution

Resume the existing Codex Goal / target-mode macro from:

`G3-2 — real PTE L2/DRAM integration`

Then continue automatically through:

`G3-2 -> G3-3 -> G3-4 -> G3-5 -> G3-CLOSEOUT -> M1_M3_VM_BASELINE_CLOSEOUT`

only when each gate is PASS. Do not pause for ordinary successful gate transitions; STOP on any hard failure/ambiguity below.

## Mandatory read order

1. repository-root `AGENTS.md`
2. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
4. this file
5. `stage_specs/M2_M3_TARGET_MODE.md`
6. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`
7. `stage_specs/M3_REFERENCE_MATERIALS.md`
8. repaired M2 review pack
9. M3 review pack including `G3_1_PTE_BACKEND.md` and `G3_1_ADDRESS_NAMESPACE_FIX.md`
10. long-lived VM specs and target-paper known/unknown ledger

Do not modify `chatgpt_handoff/*`.

## Source anchors

Core branch:
`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

Expected accepted Core start:
`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

Framework branch:
`swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Fetch/pull the latest Framework handoff before implementation.

## G3-2 stash handling

The user reports prior uncommitted G3-2 WIP in Core `stash@{0}`.

It is not accepted evidence. Do **not** blindly `git stash pop`.

First inspect it with a read-only diff against the accepted Core head. Reuse only code that still satisfies the repaired M2 and accepted G3-1 contracts. Prefer selective application/reimplementation if the stash contains stale assumptions. Do not drop the stash until the replacement G3-2 work is committed, tested, and safely recoverable.

## G3-2 acceptance emphasis

Implement the real timing path:

`L2 TLB miss -> translation MSHR -> PWQ -> walker -> PTE request -> real L2/lower memory -> matching response -> walker progress -> fill/wakeup/replay`.

Required:

- PTE request is explicitly physical and bypasses translation;
- PTE request bypasses L1D under the generic M3 policy and uses actual L2/memory-subpartition/interconnect/DRAM timing resources;
- walker cannot advance before the correct PTE response;
- multiple outstanding PTE requests are associated with the correct translation key, walk level, and request identity;
- PTE and data traffic are separately observable;
- PTE traffic consumes a demonstrable shared resource, not merely a counter/fixed delay;
- deterministic `vm_pte_l2_hit`, `vm_pte_dram`, response-identity, no-recursion, and shared-resource-pressure tests pass;
- all repaired M2 replay/conservation/store/atomic tests remain PASS.

Hard STOP on recursive translation, lost/misassociated response, deadlock, duplicate wakeup/side effect, or unexplained early walker progress.

## Page-table locality / PWC guard for later gates

G3-1 proves collision-free deterministic PTE physical identities, but the target paper does not expose its exact page-table hierarchy/locality.

Current generic address identity must not be presented as paper-exact upper-level radix locality.

Before G3-3/PWC is accepted, explicitly document and test the hierarchy-prefix/PTE-sharing semantics used by the generic baseline. If conventional prefix sharing is implemented, prove related VPNs share the intended upper-level PTE/PWC keys; if a flatter synthetic model is retained, label it `MODELING_DECISION`, quantify its locality implication, and do not make hardware-fidelity claims. This issue must be resolved before G3-5 performance characterization.

Current M3 v0 is one simulated address space / ASID-0 execution path; do not claim multi-ASID PTE physical separation without extending the backend.

## G3-3 onward

Continue with the existing stage specification:

- G3-3: finite PWC, zero/baseline/ideal modes, shared-resource behavior, M2 regressions;
- G3-4: 64KB/2MB semantics and timing decomposition;
- G3-5: integrated causality/sensitivity including fixed-latency M2 vs real-memory M3;
- closeout: complete `M3_TIMING_REALISTIC_BASELINE` and `M1_M3_VM_BASELINE_CLOSEOUT` review packs.

Do not implement target-paper L2-TLB sub-entry, Segmentation, synthetic KV, page faults/migration/UVM, MCM, or new AI-aware mechanisms in M3.

## Reporting

Maintain:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

and:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Update:

`docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/`

Final macro pack:

`docs/vm_tlb/review_packs/M1_M3_VM_BASELINE_CLOSEOUT/`

## STOP conditions

STOP immediately on:

- recursive PTE translation;
- PTE response identity/misassociation failure;
- request loss, duplicate wakeup, duplicate store/atomic effect;
- M1/M2 transparency or replay regression;
- deadlock or unexplained nondeterminism;
- a materially new page-table/timing modeling choice not covered by the approved generic-M3 policy;
- source/provenance uncertainty.

After M3 PASS and macro closeout, push both repositories, report final SHAs, and STOP before M4B / Segmentation / sub-entry / synthetic-KV / new research mechanisms.