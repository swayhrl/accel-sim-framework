# Lane7 FFN timeline capture continuation

Read `docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/AUTHORIZED_FFN_TIMELINE_CAPTURE_CONTRACT_V1.json` and require SHA256 `b6b6b36a71eb6ce092b4bd28d55de037fec5911074fe3f93ddb3e0ede7e8a7cd`.

Create the Lane7 branch/worktree from accepted producer `eae1cc4d831ae8459da558cf1358bb8daf8d76e6`. Fetch authorization branch `hrl/c16-ffn-timeline-identity-recovery-174new-v1`, copy/apply `docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/INSTRUMENTATION_DELTA.patch` (SHA256 `bdffcd5bf135fd9db310973828f51de23976fb45e558ed9ba5cc7cfc2a9bcbeb`), and require patched runner SHA256 `ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb`. Do not reinterpret or reconstruct the scientific identity.

Under one legal `/data/c16/locks/c16_gpu_campaign.lock`, execute exactly the contract's OFF/ON neutrality canary, then the single lightweight NSYS `cuda,nvtx` formal capture only if neutrality passes. Publish raw evidence and SHA receipts to the frozen 164 destination, release the lock, commit/push/fetch-back/clean, and stop. Any contract stop condition means no formal capture or follow-up experiment.
