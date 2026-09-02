# G3-1 — PTE backend and physical request contract

Status: `PASS (G3-1-RF) — STOP FOR CHATGPT REVIEW`\
Core: `a192e5dcb5b28b51fcae4b22fb9c985f60a4f5e9`\
Framework handoff: `0ca67e7ca0c22f6352b63ff8a24471717be3dc3f`

## Generic model contract

`radix_page_table_backend` is a replaceable `page_table_backend` interface.
The generic default is four configurable levels over a 49-bit simulator
address space.  It resolves the frozen resident identity-like mapping
(`SimPPN=SimVPN`) while deriving a deterministic globally injective PTE
physical address for every `(page-size class, level, VPN)` tuple.

The original provisional encoding used a page-size-dependent shift and was not
injective: a 64KB level-0 VPN `(4 << 28) | X` could alias a 2MB level-0 VPN
`X`.  G3-1-RF fixes the slot to use the fixed maximum supported VPN width,
33 bits (`49 - log2(64KB)`), for every namespace.  This matches the existing
PTE-range sizing and leaves mapping/replay semantics unchanged.

The default application identity range is `[0, 2^49)` and the PTE range is
`[2^52, 2^52 + 2^40)`.  Construction validates that the ranges do not overlap;
the range is a `MODELING_DECISION`, not a target-paper or hardware fact.
Runtime configuration exposes the level count and all range endpoints as
`-gpgpu_vm_pt_levels`, `-gpgpu_vm_application_physical_limit`,
`-gpgpu_vm_pte_physical_base`, and `-gpgpu_vm_pte_physical_bytes`.

`pte_request` carries the translation key, walk level, deterministic physical
address, and request identity.  It is constructed with `is_physical=true` and
`bypass_translation=true`; this is the explicit non-recursion contract that
G3-2 must preserve when it creates a real `mem_fetch`.

The generic PTE backend supports the required 64KB and 2MB page classes.
Segmentation sub-entry/coalescing and 4KB behavior are not introduced.

## Directed and integration evidence

`vm_m3_g3_1_test PASS` asserts:

- deterministic level-distinct 64KB PTE addresses;
- distinct 64KB/2MB PTE address classes;
- the explicit former-collision pair has distinct PTE PAs;
- minimum/maximum valid VPN boundaries for every 64KB/2MB × four-level
  namespace are ordered and non-overlapping;
- PTE address lies in, and application address lies outside, the reserved PTE
  range;
- every PTE request is physical and translation-bypassing;
- an injected replacement backend changes only PPN policy while retaining the
  existing MSHR/walker/replay lifecycle.

The compact M1/G2-1/G2-2/G2-3/G2-4/M2-RF suite all passed after the change.  A
cold Core+Framework build passed.  The bounded one-kernel functional replay
again ended normally: 9522 cycles, one MSHR/walk/registration/wakeup, and zero
active translation state.  Its configuration print confirms the generic M3
options at their documented defaults.

The repaired M2 execution path emits no PTE memory traffic.  No PTE request
enters L2/DRAM in this gate.  That integration, response association, and
real-resource proof remain unauthorized G3-2 work.
