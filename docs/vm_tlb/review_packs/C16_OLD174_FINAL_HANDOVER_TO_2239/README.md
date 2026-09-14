# C16 old174 final handover to 2239 — V0

This review pack is the CPU-only, non-destructive final inventory for the
old174 C16 AI-workload source environment.  It is a control-plane handover,
not a data migration or a new scientific campaign.

Decision: `OLD174_HANDOVER_COMPLETE`.

The accepted next topology is: Git for code/receipts/manifests; node 109 as
the RTX4080 producer; new174/2239 as CPU ingest and catalog; and node 164 as
long-term storage.  old174 is retained only as a historical source and is not
an assumed dependency of the future capture pipeline.

The detailed inventory deliberately preserves the frozen scientific boundary:

- RTX3090 closeout: `649af1b9d65a774d4aa8c32a15f9b6f4da0dd4d9`.
- RTX4080 clean R5: `b75f26674a09705659e770ab2134351414aa3c93`,
  `READY_FOR_MULTIMODEL_REVIEW`; R4 remains mechanism-only.
- V2A historical input result: `HISTORICAL_FROZEN_INPUT_NOT_RECOVERED`.
- V2C adopted input result: `ADOPTED_INPUT_AUTHORITY_V1_PASS`, future use
  only and not historical recovery.

No conclusion here authorizes a Route-B representative selection, a canary,
formal capture, CUTLASS identity repair, or a rerun.  The two required
CUTLASS rows remain `FAILED_CLOSED_CODE_OBJECT_IDENTITY_UNRESOLVED` and the
representative selection remains blocked.

Files in this pack are metadata and provenance records only.  Existing raw
evidence, models, receipts, and historical artifacts were neither changed nor
copied by this V0 review.
