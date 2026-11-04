# 3DCONV: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

256^3 FP32 row-major A/B,64MiB each,k contiguous. This is NOT a canonical27-point stencil. Fifteen literal terms contain11 distinct coordinates (S:135-142): at k-1,(i-1,j-1) repeats3 times with c11/c21/c31, and(i+1,j-1) repeats3 with c13/c23/c33; at k there are3 j neighbors on plane i; at k+1 there are6 i?1,j-1/0/+1 neighbors. Coefficients c11=2,c21=5,c31=-8,c12=-3,c22=6,c32=-9,c13=4,c23=7,c33=10. CPU mirrors this (S:40-67). A=i%12+2*(j%7)+3*(k%13) (S:70-84); B only interior written/compared.

## 2. Actual source authority and build

**S** denotes [3DCONV/3DConvolution.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/3DCONV/3DConvolution.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/3DCONV/3DConvolution.cu`, SHA256 `e789d5804a19fc637d57b03a9437488728ed462c1e4ed69a6325fbd32c037457`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/3DCONV/3DConvolution.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 212 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

Neither inspected M5 PolyBench build list includes3DCONV; its254-plane selected trace must not inherit a supposed M5 build/repair identity. Source-default S remains the audited mapping, with source-to-capture ELF identity unresolved.

## 3. Host control and kernel execution sequence

main initializes only A, selects GPU0, calls GPU then CPU/comparison (S:181-211). GPU copies both A and initially unspecified B (S:154-157), launches for i=1..254 with plane scalar i, then one synchronize, DtoH/free (S:160-178).254 launches of one unique kernel, default stream. Each grid(8,32),block(32,8):256 CTAs. Interior never reads B, so initial unspecified B affects only unwritten boundaries, not interior dependency.

## 4. Every unique kernel implementation

Only convolution3D_kernel(A,B,int i),S:121-144. Host parameter supplies i; k=32*bx+tx,j=8*by+ty. Strict interior guard, one B[i,j,k] output/thread. No device loop, shared staging, barrier, texture or atomic. Repeated k-1 subexpressions may be compiler-eliminated;15 source terms do not establish15 machine loads. Local coefficients are register/immediate candidates.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

P=256*256=65536 floats. Neighbor A=BA+4*((i+di)*P+(j+dj)*256+k0+lane+dk), B=BB+4*(i*P+j*256+k0+lane). Fixed-operand lane stride4B; CTA warps advance j by1/output1024B. Consecutive host i launches advance plane262144B, not a per-thread loop. x CTAs share k halos,y CTAs j neighborhoods, successive plane launches share A planes but never read prior B (S:123-142,165-168).

## 6. Dataflow, locality, coalescing and concurrency

For aligned full interior warp, dk0 uses1 line/4 sectors,dk?1 uses2 lines/5 sectors. Full11-coordinate union is17 lines/42 sectors: two rows at i?1,j-1 span34 floats (3 lines/6 sectors each); four other i?1 rows span32 floats shifted+1 (2/5 each); three i-plane rows span32 unshifted floats (1/4 each). This is a union footprint, not measured transactions. Edge predicates reduce it. Inter-launch A-plane persistence depends on ordering/cache capacity. One plane provides256 CTAs/2048 warps;254 serialized launches do not provide concurrent cross-plane supply. Neighbor addresses are independent before arithmetic joins; no reduction recurrence.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-02`. Parameters `NO_ARGS`; frozen input digest `79f8ab6241faeed64b49d05deecb1ad239fac5f123c4ceec75f7e0f6a9c5166d`; bundle `535d0c585d491e8716797d8c25bc408e92497cf09c48905ac42cbec3d4417eff`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/535d0c585d491e8716797d8c25bc408e92497cf09c48905ac42cbec3d4417eff/tree/kernelslist.g`, kernelslist SHA256 `ca357a3312804307b48612d3e3999d2a798d62407b4502904d8ff31cb551de6f`.

This audit read kernelslist and <=4096 header bytes per member (254 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z20convolution3D_kernelPfS_i` | 254 | `(8,32,1)` | `(32,8,1)` | 26 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1: separate within-plane warp/CTA halo sharing, cross-launch A-plane reuse, and compiler elimination of repeated operands; actual load streams are needed for pending-merge claims. EP-L2: assess A-plane residency/B write allocation and downstream return lifetimes across254 launches. Launch ordering and cache-state boundaries can matter independently of tags.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: headers do not encode scalar i arguments or prove body coverage; capture ELF unresolved. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
