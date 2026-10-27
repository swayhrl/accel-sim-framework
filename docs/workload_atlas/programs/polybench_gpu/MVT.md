# MVT: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

MVT computes x1+=A*y1 then x2+=A^T*y2, with4096x4096 FP32 A (64MiB) and four16KiB vectors. All inputs are initialized: x1=i/N,x2=(i+1)/N,y1=(i+3)/N,y2=(i+4)/N,A[i,j]=i*j/N (S:36-51). CPU reference implements both loops (S:55-74). Unlike ATAX, x2 does not consume x1.

## 2. Actual source authority and build

**S** denotes [MVT/mvt.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/MVT/mvt.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/MVT/mvt.cu`, SHA256 `83764e6633f3a0976423e0ba7ab351ac42b0eeb249bf59a9e3531c639d4923d6`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/MVT/mvt.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 227 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

The separate M5 pin `sgrauerg/polybenchGpu@5584aaa7.../CUDA/MVT/mvt.cuh` lines49-50 uses32x8, not S block256x1. Its mvt.cu lines100,115 index only bx/tx; absent overrides this predicts128 CTAs with eight ty threads per output, unlike the frozen16-CTA headers. This is a source-level duplicate-writer risk for that separate branch, not a measured failure or a property of the selected trace. Geometry/ABI identity must accompany source version.

## 3. Host control and kernel execution sequence

main allocates/initializes, selects GPU0, executes mvtCuda, then CPU/comparison (S:181-226). GPU copies five objects (S:149-158), sets block256/grid16, launches kernel1 then kernel2 on default stream and synchronizes once (S:160-166), reads both outputs and frees (S:170-177). No separate streams or host loop. Algebraic independence does not mean simultaneous execution here.

## 4. Every unique kernel implementation

mvt_kernel1 (S:109-121) maps i=256*bx+tx, guard i<N, j=0..4095: x1[i]+=a[i*N+j]*y1[j]. mvt_kernel2 (S:124-136) uses same output mapping/loop: x2[i]+=a[j*N+i]*y2[j]. Each thread owns one output with serial accumulation. No shared tile, device barrier, atomic, texture or parallel reduction.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

Let q=q0+lane,t=j. Phase1: A=BA+4*(q*4096+t),y1=By1+4*t,x1=Bx1+4*q; lane16384/0/4 B, loop4/4/0 B. Phase2: A=BA+4*(t*4096+q),y2=By2+4*t,x2=Bx2+4*q; lane4/0/4 B,loop16384/4/0 B (S:111-133). Eight warps/CTA span256 rows/columns respectively; x outputs never overlap. Across CTAs read vectors are shared.

## 6. Dataflow, locality, coalescing and concurrency

Phase1 fixed-t warp reads32 lines/sectors, cold unit amplification32x/8x for128 useful bytes; consecutive loop positions fill one row line over32 iterations/sector over8. Phase2 aligned warp uses1 line/4 sectors while each thread strides16KiB. Uniform y operand needs1 sector/line for4 unique bytes, revisited across warps/CTAs. A repeats across kernels, but64MiB reuse does not prove cache persistence. Outputs have no producer/consumer edge. Only16 CTAs/128 warps per phase, active-SM coverage<=min(16,SMcount). Independent multiplicand addresses coexist with recurrent output chains. Loop length creates work, not additional CTAs.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-26`. Parameters `20260825-b07c0ad-full; NO_ARGS`; frozen input digest `f437190767aaed4921e11e6b85f80fb3348da90ec0f18fa8fa1bdfcd76ae3079`; bundle `460901d4173352b272caa6876db2119b88a9e0471c6f6fa2f8f8477edef9c5a0`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/460901d4173352b272caa6876db2119b88a9e0471c6f6fa2f8f8477edef9c5a0/tree/kernelslist.g`, kernelslist SHA256 `f3f1e934a86753827094baaf935235d056d88241aec50ba7ccff99425c869944`.

This audit read kernelslist and <=4096 header bytes per member (2 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z11mvt_kernel1PfS_S_` | 1 | `(16,1,1)` | `(256,1,1)` | 22 |
| `_Z11mvt_kernel2PfS_S_` | 1 | `(16,1,1)` | `(256,1,1)` | 22 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1: compare row-line tag retention with phase2 coalescing and test whether16-CTA supply limits dominate. Broadcast vectors offer candidate pending overlap conditional on timing. EP-L2: compare phase-specific sector traffic and A reuse between kernels without asserting hits. Keep MVT distinct from ATAX: both outputs are initialized and x2 is independent of x1.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: capture ELF/original numeric bytes/body completeness unresolved. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
