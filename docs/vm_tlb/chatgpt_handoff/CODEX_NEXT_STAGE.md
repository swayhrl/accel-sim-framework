# CODEX_NEXT_STAGE — Track A

## Status

`M1_VM_CORE_FOUNDATION`: **PASS**.

`M2_FUNCTIONAL_TRANSLATION`: **PASS — repaired M2-RF independently accepted**.

Accepted repaired M2 execution head:

`3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`

Framework M2-RF review evidence head before this handoff:

`c12ad7bc9fb6865e97ff8b65c215490a5d92305a`

The pending-waiter retry pollution is closed: already-registered waiters bypass before TLB port/probe, new waiters retain first lookup/merge semantics, cold/integrated regressions pass, and latency sensitivity no longer turns same-waiter wait time into proportional L2 miss inflation.

## G3-1 review result

The preserved provisional G3-1 commit:

`8c613a356e6a146951cd59c9929046c6c4cfd856`

is **NOT YET ACCEPTED**.

Independent review found a deterministic PTE-address alias because current address encoding uses page-size-dependent VPN widths. A 64KB level-0 key with `vpn=(4<<28)|X` aliases a 2MB level-0 key with `vpn=X` under the current formula.

Do not start G3-2.

## Next authorized stage

Execute only:

`stage_specs/M3_G3_1_ADDRESS_NAMESPACE_FIX.md`

Do not modify `chatgpt_handoff/*`.

## Mandatory read order

1. repository-root `AGENTS.md`
2. `docs/vm_tlb/chatgpt_handoff/CURRENT_STATE.md`
3. `docs/vm_tlb/chatgpt_handoff/DISCUSSION_REFERENCE.md`
4. this file
5. `stage_specs/M3_G3_1_ADDRESS_NAMESPACE_FIX.md`
6. `stage_specs/M3_TIMING_REALISTIC_BASELINE.md`
7. `stage_specs/M3_REFERENCE_MATERIALS.md`
8. repaired M2 review pack
9. current M3 review pack / G3-1 evidence

## Source anchors

Core branch:
`swayhrl/gpgpu-sim:hrl/vm-m1-m3-v0`

Expected Core start:
`3b93e2432cbde1fcfa0eb68efc8b10d57ff3546b`

Framework branch:
`swayhrl/accel-sim-framework:hrl/vm-m1-m3-v0`

Fetch/pull the latest Framework handoff before implementation.

## Required G3-1-RF behavior

Fix the generic PTE physical-address namespace so `(page-size-class, level, VPN)` is globally injective across supported 64KB and 2MB classes.

Prefer a fixed namespace width based on the maximum supported VPN width:

```text
max_vpn_bits = 49 - log2(64KB) = 33
namespace_id = page_size_class * levels + level
slot = (namespace_id << max_vpn_bits) | vpn
```

An equivalent provably injective mapping is acceptable.

The existing PTE-range sizing already assumes the maximum 64KB VPN width; keep sizing and encoding consistent.

## Mandatory tests

At minimum prove:

- explicit former collision is gone:
  - 64KB level0 `vpn=(4<<28)|0x12345`
  - 2MB level0 `vpn=0x12345`
  - PTE PAs must differ;
- min/max VPN namespace boundaries do not overlap for every supported class/level;
- same key different levels remain distinct;
- 64KB/2MB PTE namespaces are distinct;
- PTE PA stays in reserved PTE range;
- application physical range stays outside PTE range;
- PTE request remains physical and translation-bypassing;
- replacement backend seam remains valid;
- repaired M2 regressions and pending-retry test remain PASS;
- one bounded functional M2 replay remains clean/quiescent.

## Documentation/status cleanup

Update the M3 review pack and Codex progress/report so they do not claim G3-2 is RUNNING before this fix is accepted.

If touching the M2 invariant wording, state precisely:

> the repaired M2 execution path emits no PTE memory traffic.

Do not claim the current source tree contains no `pte_request` class, because the provisional G3-1 definitions are already in history.

## G3-2 stash boundary

The user reports G3-2 WIP is preserved in Core `stash@{0}`.

Do not apply, modify, drop, or rely on that stash during this stage. No G3-2 source is authorized.

## Reporting

Update:

`docs/vm_tlb/codex_handoff/m1_m3/TARGET_PROGRESS.md`

and:

`docs/vm_tlb/codex_handoff/m1_m3/LATEST_REPORT.md`

Update/reclose:

`docs/vm_tlb/review_packs/M3_TIMING_REALISTIC_BASELINE/`

After G3-1-RF acceptance criteria pass:

- push Core + Framework;
- report exact SHAs and evidence entry;
- **STOP FOR CHATGPT REVIEW**.

Do not continue to G3-2, PWC, later M3 gates, Segmentation, synthetic KV, page faults/migration/UVM, or MCM work until the next ChatGPT handoff.
