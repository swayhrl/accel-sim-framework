# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF accepted**.

`G3-0`: **PASS**.

`G3-1 — PTE backend/request contract`: **PASS**.

`G3-2A — address provenance`: **PASS — CASE A**.

`G3-2B — generic trace-width extension`: **PASS**.

`G3-2 — real PTE L2/DRAM integration`: **PASS — independently accepted**.

Accepted Core start:
`965bd8e188175731c31cabfef6c3bdeb7c59e1fd`

Framework G3-2 evidence:
`dbbd9d8360121aeda553eaf9365073e7332018bf`

## Next authorized target

Execute as one continuous internal target:

`G3-2C hierarchy-prefix PTE identity -> G3-3 generic PWC`

Specification:

`docs/vm_tlb/chatgpt_handoff/stage_specs/M3_G3_2C_HIERARCHY_AND_G3_3_PWC.md`

If G3-2C PASSes, continue automatically into G3-3.  After G3-3 PASS, commit,
push and STOP for ChatGPT review before G3-4.

## Mandatory read order

1. repository-root `AGENTS.md`
2. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
4. this file
5. `stage_specs/M3_G3_2C_HIERARCHY_AND_G3_3_PWC.md`
6. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`
7. `stage_specs/M3_REFERENCE_MATERIALS.md`
8. G3-2B/G3-2 closeout evidence
9. accepted M1/M2/G3-1 evidence
10. long-lived VM specs and parameter ledger

Do not modify `chatgpt_handoff/*`.

## Source anchors

Core:
`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

Expected Core start:
`965bd8e188175731c31cabfef6c3bdeb7c59e1fd`

Framework:
`swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Fetch/pull latest Framework handoff before implementation.

## Architecture decision

The old flat `(level, full VPN)` PTE identity was sufficient for G3-2 plumbing
but is not accepted for final PWC locality.

Implement the balanced generic radix-prefix model in the stage spec.

For each page size:

```text
B = virtual_address_bits - log2(page_size)
L = levels
r = ceil(B/L)
top = B - r*(L-1)
level widths = [top, r, r, ...]
```

PTE identity at level `l` must use the VPN prefix through that level.  Physical
PTE namespace subranges must be deterministic, non-overlapping and
overflow-safe.

Required directed examples:

- 56-bit/64KB `[10,10,10,10]`;
- 56-bit/2MB `[8,9,9,9]`;
- 49-bit/64KB `[6,9,9,9]`;
- 49-bit/2MB `[7,7,7,7]`.

This is `MODELING_DECISION`, not target-paper exact behavior.

## G3-2C gate

Before PWC, prove:

- intended upper-level PTE sharing for related VPNs;
- leaf uniqueness;
- unrelated-prefix separation;
- 64KB/2MB class separation;
- physical namespace/range safety;
- 49-bit and 56-bit tests PASS;
- former BFS offender still preserves raw SimVA/identity-like SimPA;
- full G3-2 real PTE L2/DRAM suite, LUD/BFS, response identity and M1/M2
  regressions PASS under the new hierarchy identities.

Changed L2 PTE hit counts are allowed only when directly explained by the new
hierarchy-prefix identities.

On PASS continue automatically into G3-3.

## G3-3 PWC contract

Cache intermediate/non-leaf PTEs only, levels `0..L-2`.

PWC key:

`(ASID, page-size-class, level, prefix(vpn,level))`

Required modes:

- `OFF`: no entries;
- `FINITE`: default 128 entries, fully associative LRU;
- `IDEAL`: diagnostic unbounded/no-eviction.

The 128-entry default is generic/reference-motivated only; it is not a
Segmentation-paper parameter.

A hit skips exactly that intermediate level's PTE memory request.  Leaf PTE
reads still use the real accepted PTE memory path.

Required exact tests include:

- `vm_pwc_zero`;
- `vm_pwc_warm`: first related 56-bit/64KB walk = 4 PTE requests, second walk
  sharing upper 30 bits = three PWC hits + one leaf PTE request, total 5 rather
  than 8;
- `vm_pwc_partial_share`;
- deterministic finite-capacity LRU eviction;
- `vm_pwc_no_leaf`;
- `vm_pwc_2mb`;
- integrated real-memory PWC traffic reduction;
- no change to resolved SimPA/data semantics;
- all response/waiter/replay/conservation invariants remain PASS.

Maintain structured per-level PWC access/hit/miss, insert/eviction, occupancy,
high-water and skipped-PTE-request statistics.

## Important timing policy

Do not invent an unexplained PWC port bottleneck.  Follow the stage spec:
configurable one-cycle generic service with enough logical lookup bandwidth for
active walkers is preferred.  If a zero-cycle functional PWC probe is used for
implementation safety, document it explicitly and leave G3-5 responsible for
adding/accounting the final configured PWC lookup latency before M3 closeout.

## Explicitly forbidden

Do not:

- rewrite/mask/canonicalize generic SimVA;
- start G3-4 before review;
- implement Segmentation or L2-TLB sub-entry/coalescing;
- inject synthetic KV;
- add page faults/migration/UVM/MCM;
- claim hierarchy/PWC organization is exact NVIDIA hardware or exact target
  Segmentation-paper behavior;
- silently broaden claims to multi-ASID.

## Reporting

Maintain:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

and:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Update the M3 review pack with separate hierarchy and PWC evidence.

## STOP conditions

STOP on:

- hierarchy namespace collision/overflow;
- PTE/application physical-range overlap;
- unexpected prefix-sharing behavior;
- PWC nondeterminism;
- recursive PTE translation;
- response identity/misassociation failure;
- request loss, duplicate wakeup/store/atomic effect;
- M1/M2 regression;
- deadlock or unexplained nondeterminism;
- source/provenance ambiguity;
- any need to change the approved hierarchy/PWC policy.

After G3-3 PASS, push both repositories and STOP before G3-4.
