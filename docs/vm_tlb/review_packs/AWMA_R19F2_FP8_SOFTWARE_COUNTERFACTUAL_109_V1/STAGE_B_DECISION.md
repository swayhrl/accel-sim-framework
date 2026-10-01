# Stage B decision — exact fused software closes the MLP residual

`R19F2_FUSED_SOFTWARE_SUFFICIENT`

The one permitted opt-in cooperative CUDA quantizer passed the exactness gate on the same frozen real Qwen hidden X. Its E4M3 bytes SHA256 `79c754c1ec58ac3e5338e3bab28887a56803d0139394fe5a93c35df74e33ee15` and inverse-scale SHA256 `e40242473eecf057b7426f890b25b6645e7c8d6f570596591ec2b150598c8734` equal TE v2.19 exactly; amax is `12.25`. Gate, up and natural full-MLP outputs are bitwise identical to Stage A. The original TE cached weights and GEMM consumers are unchanged. The extension makes exactly one `cudaLaunchCooperativeKernel` source call and implements no GEMM. Its binary SHA256 is `3304de8b95d2ee31c08248746f2eb56364db210f6d2d2e2f83c465891f432da2`. Output FP8/scale/amax buffers and TE wrapper are preallocated outside the timed interval, as declared in `STAGE_B_CONTRACT.md`; this is a bounded strong-software diagnostic, not a production-ready TE patch.

Formal unprofiled synchronized wall medians (15 samples/arm/region):

| Region | S1 shared TE | S2 exact fused shared | D0 ready pair | S2−D0 / S2 | S1→D0 gap recovered by S2 |
| --- | ---: | ---: | ---: | ---: | ---: |
| P: gate+up | 0.134402 ms | 0.107263 ms | 0.102620 ms | 4.33% | 85.39% |
| M: full natural MLP | 0.187174 ms | 0.154272 ms | 0.148045 ms | **4.04%** | **84.09%** |

For Region M, S1−S2 paired-group median gaps are `0.025138/0.032675/0.034897 ms`, all positive; the combined `0.032902 ms` gap exceeds 3× the larger arm MAD. S2−D0 complete MLP median gap is only `0.006227 ms` (`4.04%` of S2), does **not** exceed 3× the larger arm MAD, and its three group medians `0.009596/0.006791/−0.000257 ms` are not consistently positive. CUDA-event medians likewise move from S1 `0.183296` to S2 `0.151552` to D0 `0.144384 ms`; the residual is below 5% in that channel as well. The predeclared software-sufficient rule is met both by `<5%` Region-M residual and `>=70%` recovery (actual `84.09%`).

Stage-A B0 and D0 receipts remain frozen; the Stage-B S1/D0 samples are a new paired comparison context, not a rewrite of Stage A. No NCU was needed. The result closes the current R19F1 operator-readiness hardware line at this software baseline; it does not claim whole-model speedup, online deployment legality, or Blackwell FP4/TMEM behavior.
