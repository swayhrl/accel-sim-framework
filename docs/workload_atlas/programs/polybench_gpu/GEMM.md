# GEMM: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

C=2123*C+32412*A*B with NI=NJ=NK=512 FP32 row-major matrices,1MiB each. init sets A[i,k]=i*k/NI,B[k,j]=(k*j+1)/NJ,C[i,j]=(i*j+2)/NJ (S:63-90); CPU follows scale/product (S:44-60). This is per-output naive GEMM, not a tiled library/Tensor Core/cuBLAS implementation.

## 2. Actual source authority and build

**S** denotes [GEMM/gemm.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/GEMM/gemm.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/GEMM/gemm.cu`, SHA256 `1728a0f34c0ef150be6e4ba481f43298753fbcc814e402f853fc0c63a3c3dfbb`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/GEMM/gemm.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 210 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

Neither inspected M5 PolyBench build list includes GEMM; a name-matched GEMM must not be assigned the M5 recovery/capture recipe or another program scalar constants. Source-default S remains the audited mapping for this frozen trace, with source-to-capture ELF identity unresolved.

## 3. Host control and kernel execution sequence

main allocates/initializes, selects GPU0, calls GPU then CPU/comparison (S:176-209). GPU allocates/copies three arrays,grid(16,64),block(32,8),one gemm_kernel/synchronize,DtoH/free (S:141-173). Grid source uses NI on x/NJ on y despite j/i mapping; equal512 masks generalized mismatch. No host iteration.

## 4. Every unique kernel implementation

Only gemm_kernel,S:124-138: j=32*bx+tx,i=8*by+ty; bounds i<NI,j<NJ; scale C[i,j] then k=0..511 accumulating ALPHA*a[i,k]*b[k,j]. One output/thread,no shared tile/barrier/texture/atomic/reduction tree. C source += does not determine emitted load/store counts; compiler alias rules matter.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

For lane l, i fixed,j=j0+l: A=BA+4*(i*512+k),B=BB+4*(k*512+j0+l),C=BC+4*(i*512+j0+l). Lane deltas0/4/4 B;loop4/2048/0 B. Eight CTA warps vary i but share identical B row segment at each k; A rows differ2048B. Different x CTAs reuse A rows; different y CTAs reuse B (S:126-135).

## 6. Dataflow, locality, coalescing and concurrency

Aligned full warp:A broadcast1 line/sector for4 unique bytes,B contiguous1 line/4 sectors for128 unique bytes,C same. A next k reuses line32 positions/sector8; B steps2KiB per thread. Eight warp B-line reuse is exact at source level but timing determines hits/merges. Cross-CTA A/B reuse is not cooperatively staged. Total3MiB objects does not prove residence under any cache policy.1024 CTAs/8192 warps supply broad work; two multiplicand addresses independent,output recurrence512 steps. Header24 registers alone does not establish occupancy or outstanding requests.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-15`. Parameters `NO_ARGS`; frozen input digest `fc0705ae3721e999217d849a3821ce25c92b8f1a5efcfd5020845641cb891318`; bundle `22bf4bd8147c1fe7c4b3aef0119ee319e7c334455bc2e01ef495ecbadbf791f5`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/22bf4bd8147c1fe7c4b3aef0119ee319e7c334455bc2e01ef495ecbadbf791f5/tree/kernelslist.g`, kernelslist SHA256 `fd9a9430fc95eb0af4c73b9710db271f8e32bff4ea2f5dd08a4e8e17c9b02057`.

This audit read kernelslist and <=4096 header bytes per member (1 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z11gemm_kernelPfS_S_` | 1 | `(16,64,1)` | `(32,8,1)` | 24 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1: same-CTA B-line reuse and cross-x-CTA A reuse offer conditional pending overlap; distinguish tag lifetime from physical-line lifetime and recurrent C dependencies. EP-L2: test L1 absorption, C write allocation/eviction and base-dependent set conflicts under actual hash/policy. Static repeats cannot establish hash interference or measured gain.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: capture-time ELF/build invocation, numeric input bytes and body coverage unresolved. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
