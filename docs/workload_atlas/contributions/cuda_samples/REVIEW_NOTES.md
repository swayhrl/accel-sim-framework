# CUDA Samples self-review and cross-review

Nine independent ten-section reports completed. Exact distinct-kernel/recorded-launch counts: BlackScholes1/1; convolutionSeparable2/2; fastWalshTransform3/16; histogram4/8; mergeSort4/13; scalarProd1/1; scan3/33; transpose8/24; vectorAdd1/1.

Source authority is explicitly candidate-only: fixed gpu-app-collection b059fdae25c2aabf737486aada743fca114469ce source tree4.2, while frozen captures name cudasdk9.1 paths. All39 downloaded small source/Makefile files match their recorded SHA256. No compile, native GPU, capture, simulation, controller or registry mutation occurred. Bounded existing trace header reads and command lists only; large trace bodies were neither scanned nor rehashed.

Important preserved discrepancies: convolution candidate host divides size3072 to384x192 and runs a warmup plus one pair (4 launches), versus recorded3072x3072 and one pair (2 launches); scan candidate hostN26624 versus recorded6815744. Fixed-source algorithms and recorded scope remain separately useful; neither resolves capture host/ELF identity.

Address self-checks: convolution column lanes are contiguous within16-lane halfwarps, while the same-thread loop jumps8rows. FWT globalgrid remains unchanged across shrinking-stride passes. Transpose16x16 naive stores touch16lines/sectors per32-lane warp because two16-lane rows share adjacent words within each outputcolumn; do not import32-wide-tile formulas. Scan secondary lanes are4096B apart; histogram merges use256B/1024B lane strides. Aligned fullwarp32Bsector and128Bline counts are explicitly conditional on access width/alignment.

Independent EP mapping review used the authority freeze directly, not the EP agent's saved DTC candidate rows: Conv shares the selected registered trace; FWT7/21 and vectorAdd4M match retained DTC alternatives. All3 reconstructed hashes agree. EP_CROSS_REVIEW.json preserves the checks and limits identity to registered member metadata, not host/source/ELF certification.

No new runtime evidence was created; source-proven facts, structural derivations and DTC/EP mechanism hypotheses remain separate. Parent coordinator owns final integration and immutable publication.
