# Admission decision

`TARGET_SPECIFIC_VM_METADATA_REQUIRED`

The exact V2 F0 effective config enables Weight Segment (`=1`) and supplies a segment map. Source at `vm_translation.cc:1863-1890` shows the active Segment descriptor can produce a functional translation result, assigns PPN and `TRANSLATION_SOURCE_SEGMENT_HIT`, and therefore can affect functional translation/cache/memory execution. A target-local neutral map would fabricate unavailable descriptor metadata. T1/T2 require real target-specific Segment registration metadata: ASID-scoped VA range, real PA extent/PPN mapping, rights, epoch/registration state, and target-specific object-range binding. No automatic node109 capture is authorized.
