# AWMA R19F1 — native Ada FP8 numerical decomposition

Stage: `AWMA_R19F1_FP8_NUMERIC_DECOMPOSITION_109_V1`

Execution branch: `hrl/awma-r19f1-fp8-readiness-109-v1`

Starting HEAD: `6ac000ce411dad034eeeb1f88a8e58fb180a5ead`

Scientific parent: `63de02aa82587680baca665d09101dc8c67222a2`

Final label: `R19F1_FP8_READINESS_RESIDUAL_PRESENT`

The parent R19 V1 BF16-versus-FP8 elementwise allclose gate **remains failed**. R19F1 asked a distinct question: when TE's exact FP8 represented input/weight are used for the non-FP8 reference, does the FP8 consumer satisfy TE's quantized-compute tolerance, and what time does online representation preparation add to that **same** consumer? Both gates passed on the single frozen real Qwen projection.

| Measured boundary | A1 online | D0 already-ready | Difference |
| --- | ---: | ---: | ---: |
| Complete synchronized call, wall median (15 samples/arm) | 0.085846 ms | 0.062693 ms | 0.023153 ms / 26.97% |
| Wall MAD | 0.003176 ms | 0.001412 ms | — |
| CUDA-event median | 0.081024 ms | 0.059456 ms | 0.021568 ms / 26.62% |

The three paired groups all have positive A1–D0 median differences, and the complete wall gap exceeds both the preregistered 5% investment screen and 3× the larger arm MAD. These are *same-FP8-consumer*, uninstrumented operator measurements, not BF16-versus-FP8 performance or a whole-model speedup. D0 is a diagnostic with the FP8 input representation already prepared, **not** a deployable online alternative.

The single NSYS/CUPTI capture found the identical `sm89_xmma_gemm_e4m3bf16_e4m3f32_f32_tn` cuBLAS consumer in A1 and D0, same `grid=4,38,1` and `block=128,1,1`, once per range. A1 additionally launches one each of amax reset, amax reduction, scale computation and BF16→E4M3 conversion. D0 launches only the GEMM. Under NSYS, the consumer's GPU kernel service is about 16 µs in both arms; the four prep kernels sum to about 5 µs per A1 range. Profiler inter-kernel gaps and NVTX durations are *not* primary timing or an exact decomposition of the 23 µs formal difference. No NCU was needed to establish the consumer or causal arm identity.

The matched numerical gate passed: F0 versus R0 max absolute error `0.016699`, mean absolute error `0.000310`, cosine `0.99999845`, all finite and allclose at the frozen TE E4M3 `atol=0.0675, rtol=0.125`. By contrast, R0 versus original B0 has mean absolute difference `0.008748` and fails that elementwise diagnostic tolerance. This isolates representation distortion from FP8 consumer error without altering the V1 conclusion. See `NUMERICAL_DECOMPOSITION.md` for exact hashes and full metrics.

Evidence is in this compact review pack; large real payload, frozen numerical objects, raw NSYS/SQLite, all samples and logs are in node164 under the path in `RAW_DATA_INDEX.tsv`. All CUDA/NSYS ran under `/data/c16/locks/c16_gpu_campaign.lock`; the lock was released after each bounded run. There was no NCU, NVBit, custom GEMM, Blackwell FP4/TMEM inference, 174, Accel-Sim or hardware design. This residual is review-only: it does not by itself prove a useful hardware mechanism or model-level benefit.

## Review provenance and open boundary

`VERIFIED_CODE`: TE source commit `5e52bef...` supplies the current-scaling quantizer, quantized-input bypass and native `generic_gemm` dispatch. `VERIFIED_RUN`: parent real payload hash, R19F1 numerical receipt, CUPTI-correlated NSYS identity and all 30 uninstrumented samples. The branch starts at the handoff `6ac000ce...` and cites the frozen scientific parent `63de02aa...`; no parent history or V1 result was rewritten. The diff adds only R19F1 runnable audit/timing/parsing utilities and this review pack—no TE, model, driver or simulator source changes.

Open for later scientific review: whether a ready FP8 representation can be obtained legally in a real online request, whether launch-chain overhead can be reduced by existing software, and whether any model-level quality/latency benefit survives. None is answered by this bounded operator diagnostic. No follow-on experiment or mechanism is automatically authorized.
