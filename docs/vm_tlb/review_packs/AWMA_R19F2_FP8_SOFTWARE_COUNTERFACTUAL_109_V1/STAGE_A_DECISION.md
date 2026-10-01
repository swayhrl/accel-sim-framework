# Stage A decision — proceed to bounded Stage B

`STAGE_A_IDENTITY_PASS_AND_MATERIAL_MLP_RESIDUAL`

Real-input and exact gate/up/down weights passed source and hash closure. Gate/up normal online quantizers, the public shared representation, and the frozen R19F1 representation have identical E4M3 bytes/inverse scale. Cached gate/up FP8 weight bytes, scales and device pointers remained unchanged; all three arms' gate/up and complete MLP outputs were finite and bitwise identical. The sole new NSYS/CUPTI capture attributed two identical `sm89_xmma_gemm_e4m3bf16_e4m3f32_f32_tn...` consumer kernels (`grid=4,38,1`, `block=128,1,1`) per arm, with 2/1/0 input-quantizer invocations for B0/S1/D0. No alternative GEMM was used.

Formal unprofiled synchronized wall medians (15 samples per arm per region):

| Region | B0 duplicate | S1 shared | D0 ready | S1−D0 / S1 | Shared recovery of B0−D0 |
| --- | ---: | ---: | ---: | ---: | ---: |
| P: gate+up | 0.143876 ms | 0.130056 ms | 0.100856 ms | 22.45% | 32.13% |
| M: full natural MLP | 0.195725 ms | 0.182693 ms | 0.151110 ms | **17.29%** | **29.21%** |

For Region M, `H_ideal=0.044615 ms`, `H_shared=0.013032 ms`, `R_remaining=0.031583 ms`. B0−S1 paired-group median gaps were all positive (`0.014782/0.007638/0.011333 ms`); S1−D0 paired-group medians were `0.032417/0.031744/0.033005 ms`, all positive. The combined S1−D0 gap exceeds 3× the larger arm MAD (`3×0.005615 ms`). CUDA-event Region-M medians also agree in direction: B0 `0.192512`, S1 `0.179200`, D0 `0.147456 ms`. Thus neither the `<5%` full-MLP stop nor the `>=70%` shared-recovery stop applies. The region-P-only negative label does not apply because Region M retains a material residual.

Stage B is therefore authorized **inside this Goal** under its existing one-path/no-sweep limits. This is not a hardware admission. Raw paired samples and all summary calculations are in `STAGE_A_TIMING_P.tsv`, `STAGE_A_TIMING_M.tsv` and `STAGE_A_TIMING_SUMMARY.json`.
