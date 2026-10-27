# GESUMMV: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

Nominal y=43532*(A*x)+12313*(B*x),two4096x4096 FP32 row-major matrices,64MiB each,and x/y/tmp16KiB each (S:27-38,42-58). IMPORTANT: init(A,x) initializes only A/x (S:61-74,167-177);B/y/tmp malloc then copied unspecified (S:130-140),GPU accumulates tmp/y without zero (S:113-116). CPU clears tmp/y but still reads unspecified B. Do not invent B distribution or numeric correctness.

## 2. Actual source authority and build

**S** denotes [GESUMMV/gesummv.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/GESUMMV/gesummv.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/GESUMMV/gesummv.cu`, SHA256 `29557f8c9c0d9de81180b26a7f3204dd9d8d1a10ef45faf7646123701d8d56f8`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/GESUMMV/gesummv.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 195 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

M5 pin `sgrauerg/polybenchGpu@5584aaa7.../CUDA/GESUMMV/gesummv.cu` initializes BOTH A and B (lines55-72; B at70), unlike S. The sm70 capture recipe additionally replaces tmp/y HtoD copies with zero cudaMemset in a prepared copy; the sm52 recovery recipe does not apply that transform. Thus S findings for B/tmp/y are not proof of a defect in an M5 repaired binary or the selected historical ELF. M5 requires repair provenance and a capture-binary SHA; neither has been tied to the selected input digest.

## 3. Host control and kernel execution sequence

main allocates,init(A,x),selects GPU0,GPU then CPU/comparison and host free (S:156-194). GPU allocates/copies five arrays,grid16/block256,one kernel/synchronize,DtoH y (S:120-153). This helper lacks cudaFree;process-lifetime allocation is separate from per-kernel cache behavior. No host iterative termination.

## 4. Every unique kernel implementation

Only gesummv_kernel,S:104-118:i=256*bx+tx,i<N,loop j=0..4095:tmp[i]+=a[i*N+j]*x[j],y[i]+=b[i*N+j]*x[j],then y[i]=ALPHA*tmp[i]+BETA*y[i]. Two thread-local ownership accumulation chains join at end. No shared tile,barrier,texture,atomic or parallel reduction. Compiler alias/promotion determines actual repeated x and accumulator memory instructions.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

q=q0+lane,t=j:A=BA+4*(q*4096+t),B=BB+4*(q*4096+t),x=Bx+4*t,tmp=Bt+4*q,y=By+4*q. Lane deltas16384/16384/0/4/4 B,loop4/4/4/0/0 B (S:106-116). Eight CTA warps cover256 separate rows of both matrices and share x. Different CTAs own disjoint output and matrix row ranges,share x.

## 6. Dataflow, locality, coalescing and concurrency

Each matrix fixed-t warp independently touches32 lines/sectors for128 useful bytes,cold amplification32x/8x. Two matrices double scatter-stream demand;set conflict requires mapping,not mere multiplicity. Consecutive t fills a row line over32 positions/sector8. x is warp uniform1 line/sector for4 useful bytes,source twice referenced but machine load count unresolved. Outputs contiguous across lanes.CTA traversal spans8MiB A/B,only16 CTAs/128 warps,active-SM coverage<=min(16,SMcount). Independent A/B/x addresses and two accumulation chains may expose parallelism,but each chain recurs4096 times. More streams do not prove more outstanding requests.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-16`. Parameters `NO_ARGS`; frozen input digest `769e6d9fd5f9cd5386556211112b1a1dec6d2b46bf69881db357257752aa22e4`; bundle `0620566b79b0cc21af493110e6acb6dd362e737c29671f86e8354ad4c8578827`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/0620566b79b0cc21af493110e6acb6dd362e737c29671f86e8354ad4c8578827/tree/kernelslist.g`, kernelslist SHA256 `ed0da283145c822bb1b9fc13c78fe41088b43478b706fcb17d078d83111044a8`.

This audit read kernelslist and <=4096 header bytes per member (1 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z14gesummv_kernelPfS_S_S_S_` | 1 | `(16,1,1)` | `(256,1,1)` | 22 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1:test two-row-stream tag demand/churn against single-matrix ATAX/MVT row phases,measure uniform x pending overlap and accumulator wakeup separately. EP-L2:assess read concurrency,y/tmp write traffic,and actual base/hash conflicts. Preserve frozen performance while documenting unspecified B/numeric values.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: UNINITIALIZED_B_TMP_Y;capture ELF/original numeric bytes/body completeness unresolved. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
