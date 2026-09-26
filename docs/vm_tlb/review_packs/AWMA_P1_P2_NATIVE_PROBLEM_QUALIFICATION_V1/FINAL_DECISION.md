# Final decision

`P1_P2_NATIVE_QUALIFICATION_NO_RESIDUAL_V1`

- P1 exhibits a real batch-dependent FP16 output change in stock Flash SDPA, but a parallel fixed-split software baseline is bitwise batch-invariant with no material residual under the preregistered timing/CV gate.
- P2 has a material ONLINE-minus-READY difference after CUDA-Graph launch optimization, but exact-index and liveness checks show it is fully bounded by the selector's own arithmetic cost; no independent index-publication/readiness cost is localized.
- Neither candidate survives discovery, so no holdout or NCU run is triggered. This stage authorizes no mechanism and no 174/Accel-Sim work.
