# Lane7 FFN timeline capture continuation

Read `docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/AUTHORIZED_FFN_TIMELINE_CAPTURE_CONTRACT_V1.json` and require SHA256 `cc081ee281b672bd8ff76cb8ae3e226194c0eec44f6f8916ed4fbbfb8facd2f9`.

Create the Lane7 branch/worktree from accepted producer `eae1cc4d831ae8459da558cf1358bb8daf8d76e6`. Fetch authorization branch `hrl/c16-ffn-timeline-identity-recovery-174new-v1`, copy/apply `docs/vm_tlb/review_packs/C16_FFN_TIMELINE_CAPTURE_IDENTITY_RECOVERY_AND_AUTHORIZATION_174NEW_V1/INSTRUMENTATION_DELTA.patch` (SHA256 `06cc0656125e0d5900330f6576b071637de1d09a7e1c9f501929d5577b1361be`), and require patched runner SHA256 `ad922629a9898c01400a165b2f6565659f1c6e422784c10bc1d013265c45b5fb`. Do not reinterpret or reconstruct the scientific identity.

Under one legal `/data/c16/locks/c16_gpu_campaign.lock`, execute exactly the contract's OFF/ON neutrality canary, then the single lightweight NSYS `cuda,nvtx` formal capture only if neutrality passes. Publish raw evidence and SHA receipts to the frozen 164 destination, release the lock, commit/push/fetch-back/clean, and stop. Any contract stop condition means no formal capture or follow-up experiment.
