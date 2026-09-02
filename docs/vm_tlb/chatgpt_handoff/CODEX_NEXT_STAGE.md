# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF independently accepted**.

`G3-0`: **PASS**.

`G3-1 — PTE backend/request contract`: **PASS — accepted after namespace repair**.

Accepted G3-1 Core head:

`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

`G3-2 — real PTE L2/DRAM integration`: **BLOCKED — correctness STOP**.

Framework blocked-evidence head:

`cc055d3a4b044136b37a1ab2ccba8f4a8a360ba5`

G3-2 locally proved the real physical/non-recursive PTE memory path and response association on completed kernels, but a later BFS kernel reached a VPN outside the accepted G3-1 backend's hardcoded 49-bit address contract. No width/namespace workaround is authorized.

## Next authorized execution

Execute only:

`G3-2A — Address Provenance Diagnostic`

Specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_2_ADDRESS_PROVENANCE_DIAG.md`

This is a diagnostic gate, not a G3-2 implementation gate.

After the diagnostic evidence is complete, STOP for ChatGPT review. Do **not** resume G3-2 or start G3-3 automatically.

## Mandatory read order

1. repository-root `AGENTS.md`
2. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
4. this file
5. `stage_specs/M3_G3_2_ADDRESS_PROVENANCE_DIAG.md`
6. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`
7. `stage_specs/M3_REFERENCE_MATERIALS.md`
8. `review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_BLOCKED.md`
9. accepted M1/M2/G3-1 review evidence
10. long-lived VM specs

Do not modify `chatgpt_handoff/*`.

## Source anchors

Core branch:

`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

Accepted Core semantic anchor:

`a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`

Framework branch:

`swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Fetch/pull the latest Framework handoff before diagnosis.

## G3-2 local WIP handling

The local uncommitted G3-2 implementation may be used only to reproduce the blocked path and collect diagnostic evidence. It remains unaccepted source.

- Do not commit/push it as G3-2 implementation evidence.
- Do not blindly restore/pop/drop historical `stash@{0}`.
- Temporary diagnostic instrumentation is permitted but must not silently alter VM semantics.
- Keep the accepted Core branch semantics unchanged at diagnostic closeout.

## Diagnostic objective

Determine exactly what the first >49-bit `SimVA` represents.

At minimum capture:

- exact SimVA/VPN/page size/required width;
- kernel sequence/name, PC, UID, SID/WID when available;
- load/store/atomic, mem-access type and instruction memory space;
- whether the value comes directly from the trace or from simulator local/generic-address transformation;
- min/max and >49-bit counts by global/local/param-local space for available LUD/BFS;
- the same address/path under VM disabled and ideal identity;
- proof that it is not sentinel/uninitialized/PTE recursion/corruption.

The final diagnostic must classify the evidence as Case A/B/C/D exactly as defined in the stage spec.

## Explicitly forbidden

Do not:

- widen `virtual_address_bits`;
- truncate/mask/canonicalize the address;
- alter PTE namespace/range;
- bypass functional VM for one memory space to make the test pass;
- change page size or ASID semantics;
- start PWC/G3-3;
- claim the Segmentation paper's 49-bit VA is a generic trace-width fact;
- claim an observed high value is a valid GPU VA until provenance proves it.

## Reporting

Maintain:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

and:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Create/update:

`docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/G3_2_ADDRESS_PROVENANCE_DIAG.md`

with compact evidence files specified by the stage spec.

Push Framework diagnostic evidence and STOP.

## STOP condition

After D0-D5, STOP regardless of whether provenance is Case A, B, C, or D. The next architecture decision belongs to ChatGPT review.
