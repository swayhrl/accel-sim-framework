# AWMA R54 Fast-Path Requalification V1R1

This authority tests the official Transformers Hub generic CUDA mappings omitted by R54 V1. The mappings execute on SM89, but the frozen exact top1/top2 ordering gate fails. Final state: `R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED`.

Large raw NSYS/SQLite, Hub artifacts, and hashes are retained in this durable authority. Git contains the compact review pack and reproduction utilities.

# R54 V1R1 decision

Final state: `R54_V1R1_HUB_KERNEL_SEMANTICS_NOT_QUALIFIED`.

The exact Hub generic function path is technically available on RTX4080/SM89. NSYS records all four required optimized strata, while the fallback arm records none of those signatures. The SM121-only `Atlas-Inference/gdn` whole-layer mapping was not used.

The frozen semantic contract failed without adding a tolerance: fallback initial top-2 IDs were `[5533, 13]`, while Hub initial top-2 IDs were `[5533, 369]`. Initial argmax, initial top-8 set, finite outputs, shape/dtype, and the complete fixed 16-token greedy continuation all matched, but exact top1/top2 ordering is mandatory.

Therefore V1R1 does not resume checkpoint lifecycle timing, state-schema work, P0/P1/P2, D512/D2048, restore, amortization, holdout, or NCU. No fourth runtime/backend is attempted. Current-platform R54 remains not scientifically qualified.
