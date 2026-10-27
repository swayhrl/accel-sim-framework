# BICG: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

This is the BiCG subkernel pair s=A^T*r,q=A*p, not an iterative BiCG solver. A is4096x4096 FP32 (64MiB), four vectors each16KiB. A,p,r are deterministically initialized (S:41-59); kernels explicitly zero s/q (S:105,123), so copied uninitialized host s/q are overwritten before use. CPU reference computes both sums (S:134-152).

## 2. Actual source authority and build

**S** denotes [BICG/bicg.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/BICG/bicg.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/BICG/bicg.cu`, SHA256 `c38c3b0bb1a543ce37ee6d4d7abe433a36574f05b49574e6bf1004c45b68f6fe`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/BICG/bicg.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 244 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

M5 uses the separate sgrauerg/polybenchGpu pin5584aaa7..., with dimension/header infrastructure and its own sm52 recovery/sm70 capture build. Same NX=NY4096 and block256x1 do not establish binary equality; the M5 manifest names source SHA e6a480c75f939958edd2633d7dc1be0a14d9890c6adb7b916b0db5e2c75965bd, different from S. Neither recipe repairs BICG. Do not import M5 recovery correctness as certification of the selected trace.

## 3. Host control and kernel execution sequence

main allocates, init_array(A,p,r), selects GPU0, calls bicgCuda, CPU reference/comparison (S:200-243). GPU copies five objects (S:166-175); kernel1/synchronize then kernel2/synchronize (S:177-185), reads both outputs/frees (S:189-196). Both grid16/block256. Exactly2 launches, no solver iteration. Independent products are explicitly serialized.

## 4. Every unique kernel implementation

bicg_kernel1 (S:99-113): j=256*bx+tx,j<NY,s[j]=0,loop i=0..4095,s[j]+=A[i*NY+j]*r[i]. bicg_kernel2 (S:117-131): i=256*bx+tx,i<NX,q[i]=0,loop j=0..4095,q[i]+=A[i*NY+j]*p[j]. One output/thread avoids write races. No atomics, shared tiles, barriers, textures or parallel reduction.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

Output q=q0+lane,loop t: kernel1 A=BA+4*(t*4096+q),r=Br+4*t,s=Bs+4*q; lane4/0/4 B,loop16384/4/0 B. Kernel2 A=BA+4*(q*4096+t),p=Bp+4*t,qvec=Bq+4*q; lane16384/0/4 B,loop4/4/0 B (S:101-128). Order is the reverse of ATAX/MVT. Eight CTA warps span256 adjacent columns first/rows second; CTAs share vectors and own disjoint outputs.

## 6. Dataflow, locality, coalescing and concurrency

Kernel1 aligned warp A uses1 line/4 sectors while a thread strides16KiB. Kernel2 fixed-t warp uses32 distinct lines/sectors, potential cold amplification32x/8x for128 useful bytes. Kernel2 consecutive t then fills each row line over32 iterations/sector over8. Vectors are warp uniform (1 line/sector for4 unique bytes), repeated across warps/CTAs. A repeats between phases, but64MiB traversal does not prove retained lines. Each phase offers only16 CTAs/128 warps, active-SM coverage<=min(16,SMcount). A/vector loads have independent addresses, accumulations recur, and full synchronization excludes phase overlap. Actual concurrency remains unmeasured.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-07`. Parameters `NO_ARGS`; frozen input digest `ae34174fbbdf83b20a72f44492665cf4b99ed35563f482f7d14763e89f398aef`; bundle `780d5828627b7e8f35f3da81572346940932deb01c9409b8ce9f272df6f752d1`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/780d5828627b7e8f35f3da81572346940932deb01c9409b8ce9f272df6f752d1/tree/kernelslist.g`, kernelslist SHA256 `388740a7be05d5596ffb77ff3f4812ff93f41afa0ee5082c1e179745cf5e0a4b`.

This audit read kernelslist and <=4096 header bytes per member (2 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z12bicg_kernel1PfS_S_` | 1 | `(16,1,1)` | `(256,1,1)` | 22 |
| `_Z12bicg_kernel2PfS_S_` | 1 | `(16,1,1)` | `(256,1,1)` | 22 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1: test row-scatter tag demand in phase2 against coalesced phase1 and conditional vector pending merges, separating tag search from physical-line retention. EP-L2: assess phase order and reuse of A lines left by phase1. Existing historical BICG results must remain separated by model identity; source inspection cannot establish model comparability. Source has no atomics, so atomic classification would require another binary/source.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: capture ELF/numeric bytes/body completeness unresolved; historical incompatible-model results not reused. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
