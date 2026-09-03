# M5 Compute Workload Manifest

Status: M5.0B in progress.  This file locks the recovered source and build
identity first; Base-smoke outcome, exact runtime, and captured launch geometry
are appended only after each completed run.

## Shared recovery contract

- Canonical PolyBench/GPU source: `https://github.com/sgrauerg/polybenchGpu`,
  commit `5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c`.
- Rebuild command: `util/dtc_l1/build_m5_polybench_cuda.sh
  /tmp/dtc-l1-m5-polybenchGpu /tmp/dtc-l1-m5-polybench-build` with CUDA 11.8
  `nvcc`, `-arch=sm_52 -O2 -cudart shared`, and a separate `-ptx` invocation.
- Input identity: each listed source release selects `STANDARD_DATASET` when no
  dataset macro is supplied.  The dimension-header SHA below is the deterministic
  input-definition hash.  No DTC result selected these dimensions.
- Run contract: the M5.0A runtime anchor remains historical. The active
  ratio-zero recovery uses Core runtime `libcudart.so` SHA-256
  `f115144d6009bab4af6d8ab0d86b69e54e8449a4c76a3809561571d32075a453`,
  set `PTX_SIM_USE_PTX_FILE=1` and `PTX_SIM_KERNELFILE=<artifact>.1.sm_52.ptx`,
  and use the fixed `PAPER_BASE_16KB.config` (SHA-256
  `993513296458bf014cfa33ff047e1ed7391a1fee990e3b4a2d9d738cab0ff366`)
  for formal Base smoke.  The M5.0A one-process calibration was superseded by
  measured host headroom and the explicit authorized parallel campaign; each
  process remains isolated and carries its own identity record.

## Recovered PolyBench/GPU algorithms

| Thesis ID | Recovered canonical ID | Mapping | Standard dimensions (header SHA-256) | Binary / PTX SHA-256 |
| --- | --- | --- | --- | --- |
| `bicg` | `BICG/bicg.cu` | `EXACT_MATCH` | `NX=NY=4096`; `2a9929d6b36fb18cfc7c3b7bf9b22234cac7ad929e8ec8c12413beac1da68d7e` | `db1cc9246ee97389b32396d3b20294a3c8a89139067cabcda93ec87d0ed1f84b` / `0040bbe0f942a99d468f79818722327835c02dea95a5b9e3273db3de2f7417a0` |
| `atax` | `ATAX/atax.cu` | `EXACT_MATCH` | `NX=NY=4096`; `0c5e9504a086fc56b2521efe64db8da3ac1000ff49cf67f911da5579e83fbba9` | `647851e4573103f853373323fe7cf779e363c2fb0242fe22089f64fd7d2db163` / `f5e084aac5afd6ac78311ad865c31f950de557f39e84b35894b1ba2eeacefe89` |
| `gemv` | `GEMVER/gemver.cu` | `SOURCE_EQUIVALENT_CONFIRMED` | `N=4096`; `b30c7701d9b64d10fe961474ea96e20a6b0133c95056679d1f41509dc653a7c3` | `04d6c9b931988faf7f715eeda40f7688e0fee98b4b114a0c86d4a0f6da2dce5d` / `4fcd29b43d7823c8d5329420264114f48b4b8feda9689a7e7961cff9b39a2f12` |
| `mvt` | `MVT/mvt.cu` | `EXACT_MATCH` | `N=4096`; `51857653a32535ed9a3ec9f3ad6b0312ee7d881f7ff6e7852f28ef0e0a10ea33` | `7baa7b6b06b4e7868d836a01e11f0e435a76f10d989f1107bcbaea71bd0b9d8b` / `01d31d1f9d18ca6b7294765aeae4ebacd8957a922e725e7a5f2fd81f3d9e3b9f` |
| `syrk` | `SYRK/syrk.cu` | `EXACT_MATCH` | `NI=NJ=1024`; `e3705e34f99ded71bdf541098ee170ed4b4dc2ebef3f8c3cf4c60e964ee499e7` | `e711f0dd94a2db64b746a24d34bff1fca9a634814e2978cf4efa058718f0af30` / `0feb9348f96d118e78cc80144863b27ae7fb5f3ba9c1aa116b3c53a2a766c6e3` |
| `gesu` | `GESUMMV/gesummv.cu` | `SOURCE_EQUIVALENT_CONFIRMED` | `N=4096`; `466b6facaf9c48e58256bb361b0036ead460a460fa405d13b4d87ff438615537` | `32da3ab10c6b0cdb0a7e9af569899e51ebb302a19602f9d37e3377469ab6447e` / `fa2bf1f5ac44e6b7988c783d438ddfd09944c470d54704f7afea436ed3eef830` |
| `syr2k` | `SYR2K/syr2k.cu` | `EXACT_MATCH` | `NI=NJ=1024`; `287ae4fdd8a5f196d298fe1bb0337a06d6fde673be975814a4e09da96020d94a` | `1cbb363142092a6a72dfc787db63cfeb864fa0dfe2b403ff7fcf6b098b734978` / `9654b639f63880049ae9eb0b43f23cd97ca788eba06f405e23bc4313769f0a17` |
| `2mm` | `2MM/2mm.cu` | `EXACT_MATCH` | `NI=NJ=NK=NL=1024`; `9eba6b40d9a0ae23c5033ee5ce09b8c493f27d88e07f2e1244430e94b5075745` | `549c0a64248596af597c1b33894608bfa32fd5e59edcd4937ac6ccc4f2d3bcf1` / `cc3900b3f54538497b7479dbf3276142b2d08ae04cffb1f6509a95d6f8e2312e` |
| `conv2d` | `2DCONV/2DConvolution.cu` | `SOURCE_EQUIVALENT_CONFIRMED` | `NI=NJ=4096`; `51edb9574e0e942bae6f4f2a1f7bd4c9a385fcb38fbacf77fe4451b2d40dd132` | `8ade2d6153cdaa9816cb6c4bc4d65320fe12c0b4fa9f18f90db7d50fd4831bc1` / `30a8a95bfd8851d55178a5ec1fc1d7e846ea9b0b53b15bd9d26a5d9a60daae12` |
| `spmv` | Parboil CUDA JDS wrapper | `SOURCE_EQUIVALENT_STANDARD_INPUT` | canonical `medium`: bcsstk18 11948x11948; matrix `abbe1909f57d6fc17fc800446bac326bd0c5343305cf193b3aa1bc8f40c82ec9`, vector `d155de2b9615cae3c2bb8b60a9e82a7d26be7e80de772a5f1c0cb830d2e49061`; the fully recorded `large` diagnostic timed out while progressing | `08f834ff68e9e092db1f988974ddb8491bba06c176037e862aa81b839ec5900c` / `ad653aaee22ad19f0a08510bf5454c9aaf2d4984d85d379fa3634dab629a5ae7` |

`gemv` is resolved to GEMVER because its three GPU kernels implement the
matrix update followed by the two matrix-vector operations described by the
thesis phrase; `gesu` is resolved to GESUMMV because its kernel combines two
matrix-vector products with scalar `alpha`/`beta`; and `conv2d` is resolved to
2DConvolution because the existing `pb_2dconv` wrapper differs from the
canonical source only in relative include paths.

## Remaining recovery

`spmv` is source-equivalent to canonical Parboil CUDA JDS: both invoke
`coo_to_jds(..., mirrored=1, binary=0, ...)` and the same 50-kernel JDS loop.
The M5 wrapper additionally uses the correct `float` byte count for the vector
copy and prints a local completion marker. The canonical `large` input is a
real-symmetric MatrixMarket text file despite its historical `.bin` suffix; it
is therefore parsed correctly with `binary=0`.  The M4 `fidapm05` matrix is
expressly not accepted because it is 42x42 / 520 entries and reached Base PIB
peak 3. Base full-load and official-output comparison remain pending.

SpMV source provenance: wrapper checkout `gpgpu-workloads`
`de9cf4293f418877aa9cdb6a2395338ca06674a6`; canonical Parboil checkout
`https://github.com/palmer-dabbelt/parboil`,
`4e0fc54866546efa44fe93af57c9cef62f6c8eb9`. Rebuild with
`util/dtc_l1/build_m5_parboil_spmv.sh <wrapper> <parboil-root> <output>`.

## Base smoke ledger

| Workload | Status | Evidence |
| --- | --- | --- |
| `bicg` | `RATIO0_BASE_OUTPUT_CLEAN_STRICT` | Earlier `M5-27a653d36a4da01b` remains `DIAGNOSTIC_CONFIG_INVALIDATED` by M5-T004 because it dynamically used a 128 KiB conventional L1. The corrected isolated ratio-zero run completed naturally with zero CPU/GPU mismatches and strict drain closure; see `m5/generated/m5_0b_bicg_base_ratio0.json` and `m5/handoffs/M5_0B_RATIO0_BASE_BATCH.md`. |
| `spmv` | `R5DV_CLOSED_RATIO0_CANONICAL_SMOKE` | Earlier `M5-9c1b7df007ca2a11` remains `DIAGNOSTIC_CONFIG_INVALIDATED` by M5-T004 and ratio-25 evidence remains diagnostic. Corrected LEGACY/PAPER_BASE ratio-zero runs both pass the official comparison and strict drain checks; canonical Base is `3,202,814` cycles, 121,342,000 instructions, and lower acquired/released `3,844,406/3,844,406`. This closes M5-T005 but does not close the normal M5.0B triplet campaign. |
| other eight | `ACTIVE_FORMAL_BASE_16KB` | Corrected isolated Base runs are active; no output claim is made before source self-check and strict invariant parsing complete. |
