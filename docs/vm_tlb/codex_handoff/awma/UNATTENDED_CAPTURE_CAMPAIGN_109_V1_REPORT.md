# AWMA Unattended Capture Campaign 109 V1

Decision: `AWMA_109_UNATTENDED_CAPTURE_CAMPAIGN_V1_COMPLETE_WITH_SCOPE`

Reason: `USER_EARLY_CLOSE_AFTER_P2C_TO_RELEASE_NODE109`.

- P0/P1/P2A/P2B/P2C accepted node164 ACK bundles: 16.
- P2C completed all requested primary GEMV points: step 4, 8, 16, 24, 32.
- P2D Step-4 had no terminal receipt when early close arrived; it was not admitted and all P2D+ targets are marked `SKIPPED_BY_USER_EARLY_CLOSE_AFTER_P2C`.
- GPU is released before this CPU-only finalization.

Review pack: `docs/vm_tlb/review_packs/AWMA_UNATTENDED_CAPTURE_CAMPAIGN_109_V1/`

Raw artifacts remain only in their immutable accepted paths; this Git review pack stores paths and hashes, not raw traces.
