# 2DCONV: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

One nine-term stencil sweep on4096x4096 FP32 row-major A, produces B (64MiB each), not iterative filtering. For dj=-1 weights over di=-1/0/+1 are(.2,-.3,.4); dj=0:(.5,.6,.7); dj=+1:(-.8,-.9,.10), S:115-123. CPU expression matches (S:39-58). A=rand()/RAND_MAX without explicit srand here (S:62-73); exact bytes depend on libc/process state. B boundaries are neither written nor compared (S:76-96,119).

## 2. Actual source authority and build

**S** denotes [2DCONV/2DConvolution.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/2DCONV/2DConvolution.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/2DCONV/2DConvolution.cu`, SHA256 `5e12047cbe8cc8a21658d15df602434ee70ebf0b873d45119974fb49da63a192`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/2DCONV/2DConvolution.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 186 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

M5 separately pins sgrauerg/polybenchGpu5584aaa7... with source SHA cef6d23d7c1d931e5427175dcf4c02a2d5e81ca2747b133222ad962d63b390d8 and sm52 recovery/sm70 capture recipes. Same4096 dimensions and a convolution name are insufficient for binary equivalence. No 2DCONV initialization/geometry transform occurs in those recipes. Its M5 input/macro/runtime records remain separate from the chosen source/trace.

## 3. Host control and kernel execution sequence

main initializes A, selects GPU0, runs GPU then CPU/comparison (S:154-185). GPU allocates A/B, copies only A, launches once/synchronizes, DtoH whole B/frees (S:128-151). Grid(128,512),block(32,8):65536 CTAs. Formula swaps NI/NJ roles relative to j/i mapping (S:140); equal4096 makes this correct here, not proof for nonsquare inputs.

## 4. Every unique kernel implementation

Only Convolution2D_kernel (S:108-125): j=32*bx+tx,i=8*by+ty, strict interior guard, one output B[i,j] per thread from nine A neighbors. No loop, shared tile, barrier, texture, atomic or previous-B load. Coefficients are local scalar constants, not an explicit CUDA constant-memory array. Outer rows and edge lanes are inactive.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

For lane l, i fixed,j=j0+l: neighbor A=BA+4*((i+di)*4096+j0+l+dj), output B=BB+4*(i*4096+j0+l), di/dj in{-1,0,1}. Fixed-operand lane stride4B; no thread loop. Adjacent CTA warps increment i by1,16384B output stride, sharing two input rows. x-neighbor CTAs share one-column halos, y-neighbor CTAs share rows; no data-dependent address (S:110-123).

## 6. Dataflow, locality, coalescing and concurrency

A full interior warp with aligned rows: dj=0 uses1 line/4 sectors per row; dj=+1 or-1 uses2 lines/5 sectors. Nine-operand input union is3 rows*34 floats=408 useful bytes,9 lines/18 sectors: each aligned32-column segment plus both halos spans3 lines/6 sectors. These union counts are not summed dynamic transactions. B stores use1 line/4 sectors; edge predicates change counts. Source lacks cooperative shared staging, so cache/scheduling decides halo reuse.65536 CTAs give abundant work supply; nine independent neighbor addresses feed a final weighted sum, but emitted scheduling/scoreboard/registers determine in-flight requests. No iteration/kernel dependency exists.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-01`. Parameters `NO_ARGS`; frozen input digest `d984ea5475a581ad8ffa8181eaf1bb91e524de3889d30243278c285ed707c7a0`; bundle `e230789ec7addca421101b60a1c9fdcb60d700a8a75478fdd5faab21574aa5ac`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/e230789ec7addca421101b60a1c9fdcb60d700a8a75478fdd5faab21574aa5ac/tree/kernelslist.g`, kernelslist SHA256 `23bcc08b04d82fc527ffc1365d3199f4d1f3057bf6a2705d1110c5c226227d64`.

This audit read kernelslist and <=4096 header bytes per member (1 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z20Convolution2D_kernelPfS_` | 1 | `(128,512,1)` | `(32,8,1)` | 24 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1: nearby warp/CTA halo requests can overlap while pending; measure this separately from ordinary hits, and test searchable-tag versus physical-row-line retention. EP-L2: assess duplicates surviving L1 and B write allocation versus A row traffic. Compare broad CTA supply against16-CTA matrix-vector cases without inferring performance from coalescing alone.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: rand input/libc identity, capture ELF and complete threadblock bodies unresolved. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
