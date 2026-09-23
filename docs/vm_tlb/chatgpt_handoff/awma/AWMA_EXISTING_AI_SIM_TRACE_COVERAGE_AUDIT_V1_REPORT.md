# Existing simulator-native AI trace coverage audit

Stage: `AWMA_EXISTING_AI_SIM_TRACE_COVERAGE_AUDIT_V1`
Execution branch: `hrl/awma-existing-ai-sim-trace-coverage-audit-v1`
Coordination base: `b5a366fcda31ee0ba18f235288eed51b998e4589`

## Result

The future representative suite can start without recapture from exactly three hash-closed simulator-native payloads. They are the only entries with accepted RTX4080/V1 replay evidence:

| target | phase / normalized family | exact function and shape | payload SHA256 | runner/index SHA256 |
|---|---|---|---|---|
| T0 `Q05_PREFILL_ATTN_FLASH` | PREFILL / `PYTORCH_FLASH_FWD` | `pytorch_flash::flash_fwd_kernel<...>`; grid `16,1,14`, block `128,1,1`; occurrence 0 / global launch 34 | `d8fa338f82800f646c8501a6a1d1049afaae213fe0d7f70d4913fcfaa76ba67a` | `a8b4ba1cf33f34be345b38908cb39572c0d14972170fd1972b4b080e81154fd5` |
| T1 `PREFILL_GEMM_PRIMARY_OCC0` | PREFILL / `CUBLAS_GEMM` | `cutlass_80_tensorop_f16_s16816gemm_relu_f16_256x128_32x3_tn_align8`; grid `128,3,1`, block `256,1,1`; occurrence 0 | `e36178f9a92033cd91f3c1ff4b165321b7958157c7deed2a9aaa4696e7c73e8c` | `c9dd68f84606deceb8d7dcece6e35c93750b16bf507ac3666c3adb2a0e0cdc41` |
| T2 `DECODE_GEMV_PRIMARY_STEP16` | DECODE / `CUBLAS_GEMV` | `internal::gemvx::kernel<...cublasGemvTensorStridedBatched...>`; grid `1216,1,1`, block `16,4,1`; step 16, occurrence 10 | `b87cd6cb6a2bc0f67e17616e26d1bf9091facad242d46a43f5f9c1ac274b6138` | `2a458d31a945cf11ce465b563582e6ab29292ae692bd3d2acd74bf4e8b5c2c4a` |

All three are `P1_ACCEPTED` in the frozen RTX4080/V1 trace authority and have accepted 10/80 and 0/80 replays. Payload/index closure was independently checked against node164.

## Existing coverage requiring only requalification

There are 92 formal simulator-native traceg payloads with no accepted RTX4080/V1 replay. These are not missing captures. They remain reusable inputs after an identity/config/replay qualification on the frozen V1 baseline:

- PREFILL Flash candidates: four targeted occurrence bundles, plus the remaining 34 contiguous-prefix payloads not equal to T0.
- PREFILL GEMM candidates: occurrences 4, 8, 16, and 19, plus historical simulator-native lines.
- DECODE GEMV: steps 4, 8, 24, and 32, alongside the accepted step-16 T2.
- DECODE Flash splitkv: exact `flash_fwd_splitkv_kernel` candidates over steps 1/8/16/24/32 and recorded occurrences.
- DECODE Flash combine: exact `flash_fwd_splitkv_combine_kernel` candidates over steps 1/8/16/24/32 and recorded occurrences.

The full one-row-per-payload mapping, including phase, candidate, function, grid/block, step/occurrence, payload SHA, derived runner/index SHA, producer identity, simulator qualification, and V1 replay flag is `ASSET_INVENTORY.tsv`. A missing sidecar is represented as `UNKNOWN`, never inferred.

## Native-only boundary

Nine historical Qwen2.5 S2 NVBit/MREF or LDGSTS shard bundles are catalogued as `NATIVE_ONLY`. They provide Native census/context evidence only. They are not represented as traceg, are not claimed losslessly convertible, and do not satisfy simulator-input coverage.

## Native census linkage (all weights provisional)

The existing V1 census is linked only for prioritization pending Window A V2 reclassification. Its Qwen2.5 S2 family totals are: Prefill `CUBLAS_GEMM` 70 launches / 66.48% time; Prefill `PYTORCH_FLASH_FWD` 10 / 14.31%; Decode `CUBLAS_GEMV` 5,408 / 49.76%; Decode `PYTORCH_FLASH_FWD` 1,536 / 9.87%. Other trace-absent but material Decode families are vectorized elementwise 9.05%, elementwise 7.64%, copy-kernel 6.62%, and unrolled elementwise 5.44%. These V1 shares are **PROVISIONAL** and must not select or weight the final suite until Window A returns V2.

## Classifications and minimum future gap

`REUSABLE_NOW`: T0, T1, T2 above.

`REQUIRES_REQUALIFICATION`: 92 existing simulator-native payloads, especially splitkv/combine step and occurrence diversity. Requalification must bind exact payload/index, frozen V1 source/config, instructions/CTA/UID, terminal state, and 10/80/0/80 replay; it is not capture.

`NATIVE_ONLY`: the nine catalogued NVBit/MREF/LDGSTS shard bundles.

`MISSING_SIM_TRACE`: no accepted simulator-native payload presently covers the material non-target Decode families listed above. The minimum eventual node109 request, if the final selector requires it after V2 reconciliation, is one exact simulator-native capture per selected absent family/shape: first `AT_NATIVE_VECTORIZED_ELEMENTWISE`, then `AT_NATIVE_ELEMENTWISE`, `COPY_KERNEL`, and `AT_NATIVE_UNROLLED_ELEMENTWISE`. Do not request any capture merely to fill the existing splitkv/combine or GEMV/PREFILL Flash/GEMM coverage: those payloads already exist.

## Boundaries and execution record

- No GPU capture, node109 job, simulator replay, or Lane B change was started.
- The local object database already contained `origin/hrl/awma-post-lanea-representative-suite-handoff-v1 @ b5a366f...`; a fresh `git fetch` was attempted but the configured GitHub proxy at `127.0.0.1:63900` refused connection. The audit used the cached origin ref plus current Git authority and node164 provenance. Push/fetch-back is retried at closeout.
- The contiguous-prefix bundle contains 35 traceg files. T0 is specifically `kernel-34-ctx_0x5b5ba0bd1a60.traceg.xz`; it was separately rehashed as the accepted `d8fa...` payload. It must not be confused with the bundle's kernel-0 trace (`82b5...`).
