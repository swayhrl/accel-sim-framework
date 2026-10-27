# 3MM: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

Nominal E=A*B,F=C*D,G=E*F. NI/NJ/NK/NL/NM all512,FP32 row-major,seven1MiB matrices (S:26-37). init fills only A/B/C/D (S:41-76). IMPORTANT: E/F/G malloc but uninitialized before copies and GPU += (S:271-280,223-229,119/135/151),so literal GPU E=E0+AB,F=F0+CD,G=G0+EF with unspecified E0/F0/G0. CPU explicitly zeros intermediates/output (S:157-199). Do not assume demand-zero malloc or claim fresh numeric validation.

## 2. Actual source authority and build

**S** denotes [3MM/3mm.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/3MM/3mm.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/3MM/3mm.cu`, SHA256 `23b6e114e96c0d85d58b01a49019856e67e9b42cc9db81eed05292862caaca5e`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/3MM/3mm.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 307 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

The separate sgrauerg/polybenchGpu5584aaa7... source explicitly zeroes E/F/G inside its three kernels (CUDA/3MM/3mm.cu lines103,119,135), unlike S. It retains512 dimensions and32x8 blocks in 3mm.cuh lines36-41,72-73. However neither inspected M5 build list includes3MM, so this is an available corrected source variant, not an established M5 capture. S initialization gap is not proven in the selected binary.

## 3. Host control and kernel execution sequence

main allocates eight host buffers,initializes four inputs,selects GPU0,runs GPU then CPU/comparison (S:258-306). GPU allocates/copies seven arrays (S:215-229),then kernel1/synchronize,kernel2/synchronize,kernel3/synchronize,DtoH G/free (S:231-254). All grid(16,64),block(32,8),1024 CTAs. Three unique definitions,three launches. Kernels1/2 mathematically independent yet serialized;kernel3 needs both.

## 4. Every unique kernel implementation

mm3_kernel1,S:109-122: E[i,j]+=A[i,k]*B[k,j],k<NK. mm3_kernel2,S:125-138: F[i,j]+=C[i,k]*D[k,j],k<NM. mm3_kernel3,S:141-154: G[i,j]+=E[i,k]*F[k,j],k<NJ. All j=32*bx+tx,i=8*by+ty with respective dimension bounds;one output/thread. No shared tiles,barriers,textures,atomics or parallel reductions. Output source += does not fix generated load/store frequency.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

For every Z=X*Y with X row width R,Y/Z width C: X=BX+4*(i*R+k),Y=BY+4*(k*C+j0+lane),Z=BZ+4*(i*C+j0+lane). R=C=512 here for all three. Lane0/4/4 B,loop4/2048/0 B. Eight CTA warps vary i and share identical Y row segment; x CTAs share X rows,y CTAs share Y. Kernel3 changes bases/objects to E/F rather than index shape (S:111-151).

## 6. Dataflow, locality, coalescing and concurrency

Aligned full warp:X broadcast1 line/sector for4 unique bytes,Y1 line/4 sectors,Z1 line/4 sectors. X line spans32 k,sector8;eight warp Y reuse is exact source reuse conditional on timing. E/F transition from global writes to reads in kernel3,true producer/consumer reuse. Total7MiB objects/1MiB each does not prove retained data.1024 CTAs/8192 warps per phase offer supply;512-step output recurrence and independent X/Y addresses govern potential overlap. Explicit synchronizations prohibit1/2 overlap. Different bases may change mapping despite same shapes.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-03`. Parameters `NO_ARGS`; frozen input digest `977a2f7007cb1f9673fe3a5c17cdbb469335c619c172a0a882eb18410049eb3d`; bundle `d8416025cf18c9ff0e81c472982c10785a44cb99b1f496d402f0360180e9a46f`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/d8416025cf18c9ff0e81c472982c10785a44cb99b1f496d402f0360180e9a46f/tree/kernelslist.g`, kernelslist SHA256 `024b84b0fa33cfe4c63f026fd9be21469c7dd1d48ff4d6594ac613ee361d9fa8`.

This audit read kernelslist and <=4096 header bytes per member (3 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z11mm3_kernel1PfS_S_` | 1 | `(16,64,1)` | `(32,8,1)` | 26 |
| `_Z11mm3_kernel2PfS_S_` | 1 | `(16,64,1)` | `(32,8,1)` | 26 |
| `_Z11mm3_kernel3PfS_S_` | 1 | `(16,64,1)` | `(32,8,1)` | 26 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1: compare shared Y tag retention and accumulator dependencies across phases;separate searchable tags/data-line lifetime. EP-L2: assess dirty E/F/writeback state,producer-to-consumer residency and phase3 allocation pressure. Same dimensions do not imply same cache conflicts; numeric initialization gap must remain distinct from existing accepted timing evidence.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: UNINITIALIZED_E_F_G;capture ELF/realized numeric contents/body completeness unresolved. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
