# Fair-arm source audit

C13 Path A is selected from direct source and execution evidence.  `FAIR_ARM_MANUAL` (0) preserves the parsed translation configuration; it does not apply the F7 profile.  F7 explicitly replaces the L2 mode with `L2_TLB_STANDARD` (0), whereas the C12 source config inherited by original C13 configs contains `gpgpu_vm_l2_tlb_mode=1` (`L2_TLB_SUBENTRY_16`).  Original C13 only overrode entries and Segment fields, so its MANUAL rows retained mode 1.

The repaired generator writes the final override with explicit fair arm, entries, associativity, and `gpgpu_vm_l2_tlb_mode 0`.  Launch is refused unless independent last-option folding, frozen trace/registration SHA, binary SHA, Core HEAD, and exclusion-map provenance agree with the manifest.
