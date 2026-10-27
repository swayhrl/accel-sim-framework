# SYRK: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

Full dense C=4546*C+12435*A*A^T,N=M=1024,FP32 row-major A/C,4MiB each (S:26-38,61-84). All N^2 outputs computed,no triangular condition. init A[i,k]=i*k/N,C[i,j]=(i*j+2)/N (S:42-58). Init uses C stride M,update N;N=M masks generalized inconsistency. Symmetry does not halve launched work.

## 2. Actual source authority and build

**S** denotes [SYRK/syrk.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/SYRK/syrk.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/SYRK/syrk.cu`, SHA256 `976d43bddecf931f4abe38e1c554809d73d62881a53b1a78b590a094dcf47c7c`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/SYRK/syrk.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 195 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

The separately pinned M5 source `sgrauerg/polybenchGpu@5584aaa7.../CUDA/SYRK/syrk.cu` initializes alpha32412,beta2123 (lines39-40), C=i*j/ni (line53), and uses the passed scalar parameters (lines115-126). S instead uses compile-time12435/4546 and C=(i*j+2)/N. Same1024 dimensions/32x8 block do not imply same numeric workload or binary. Those M5 scale/input changes are not silently applied here.

## 3. Host control and kernel execution sequence

main initializes,selects GPU0,GPU then CPU/comparison (S:165-194). GPU allocates/copies two4MiB arrays,grid(32,128),block(32,8),one syrk_kernel(alpha,beta,A,C),synchronize,DtoH/free (S:138-162). No iterative host launch/termination.

## 4. Every unique kernel implementation

Only syrk_kernel(DATA_TYPE ALPHA,DATA_TYPE BETA,a,c),S:120-135:j=32*bx+tx,i=8*by+ty,bounds i/j<N,scales c[i*N+j] by lowercase compile-time beta,then k=0..1023 adds lowercase alpha*a[i*M+k]*a[j*M+k]. Uppercase scalar kernel parameters are unused;macros at S:34-35 drive arithmetic. One output/thread,no shared tile,barrier,texture,atomic or parallel reduction. Source C += does not fix emitted memory counts.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

i=8*by+ty,j=j0+lane. First A=BA+4*(i*1024+k),lane0/loop4 B. Second A=BA+4*((j0+lane)*1024+k),lane4096/loop4 B. C=BC+4*(i*1024+j0+lane),lane4/loop0 B. Eight CTA warps vary i,repeat same32-row second-A set. x CTAs vary j row sets but share first-A rows;y CTAs revisit second A. Diagonal i=j lanes have identical A operands;footprint union must account for this (S:123-132).

## 6. Dataflow, locality, coalescing and concurrency

First A broadcast1 line/sector for4 unique bytes. Second A touches32 distinct lines/sectors for128 useful bytes,cold amplification32x/8x;consecutive k reuses row line32 positions/sector8. Eight CTA warps share this32-row set,not a single coalesced line. C contiguous1 line/4 sectors. First A may coincide with second row set on diagonal tiles,so blindly summing overcounts. Total8MiB objects does not prove L2 residence.4096 CTAs/32768 warps supply broad work;1024-step recurrence,two independent operand addresses,no cooperative/symmetry work reduction. Header24 registers is insufficient for occupancy/runtime concurrency.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-40`. Parameters `20260825-b07c0ad-full; NO_ARGS`; frozen input digest `b51811aca9dc70cfe109fad8de73d5305647bc16d70b9289c1c918f4d3ab5d39`; bundle `82d001fc8941d5715620b6e8793091dfbf4749eccc1364c60b42a469894a2fa8`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/82d001fc8941d5715620b6e8793091dfbf4749eccc1364c60b42a469894a2fa8/tree/kernelslist.g`, kernelslist SHA256 `1e2783e4e092143278ae7a70c6d4c4c18596be7cd069899b0715b8a995cf96af`.

This audit read kernelslist and <=4096 header bytes per member (1 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z11syrk_kernelffPfS_` | 1 | `(32,128,1)` | `(32,8,1)` | 24 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1:test searchable tag retention of32-row sets repeated across warps,separate pending merge from loop-sector reuse/hits. EP-L2:assess A reuse against C dirty/write-allocation/eviction under actual hash. Unlike GEMM coalesced B,the second operand here is scatter despite matrix-product naming.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: capture ELF/original initialized bytes/body completeness unresolved;scalar header argument values not checked. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
