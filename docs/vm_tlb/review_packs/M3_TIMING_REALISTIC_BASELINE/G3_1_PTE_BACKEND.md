# G3-1 — PTE backend and physical request contract

Status: `PASS`\
Core: `8c613a356e6a146951cd59c9929046c6c4cfd856`\
Framework evidence anchor: `65a6e68d35cded7b78293b92a253e09c75c5aa36`

## Generic model contract

`radix_page_table_backend` is a replaceable `page_table_backend` interface.
The generic default is four configurable levels over a 49-bit simulator
address space.  It resolves the frozen resident identity-like mapping
(`SimPPN=SimVPN`) while deriving a deterministic unique PTE physical address
for every `(page-size class, level, VPN)` tuple.

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
- PTE address lies in, and application address lies outside, the reserved PTE
  range;
- every PTE request is physical and translation-bypassing;
- an injected replacement backend changes only PPN policy while retaining the
  existing MSHR/walker/replay lifecycle.

The compact M1/G2-1/G2-2/G2-3/G2-4 suite all passed after the change.  A full
Core+Framework build passed.  The bounded one-kernel functional replay again
ended normally with the unchanged M2 values: 79 completions, one MSHR/walk,
one registration/wakeup, and zero active translation state.  Its configuration
print confirms the four new generic M3 options at their documented defaults.

No PTE request enters L2/DRAM in this gate.  That integration, response
association, and real-resource proof are deliberately deferred to G3-2.
