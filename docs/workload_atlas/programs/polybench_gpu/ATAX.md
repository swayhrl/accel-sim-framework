# ATAX: source and behavior audit

## 1. Program and algorithm

**Scope:** the following algorithm/source facts refer to recovered source S; capture-time source/ELF binding remains unresolved. Section2 distinguishes the known corrected/M5 source variants.

Nominal ATAX forms tmp=A*x then y=A^T*tmp. A is4096x4096 row-major FP32 (64MiB), x/y/tmp each4096 floats (16KiB). init_array sets x[i]=i*pi,A[i,j]=i*j/NX (S:42-54). IMPORTANT numeric gap: host y/tmp are malloc allocations, not initialized before HtoD (S:189-198,153-156), whereas GPU uses += without clearing (S:93,107). Literal GPU semantics include unspecified tmp0/y0. CPU reference explicitly zeros both (S:113-136). Preserve this distinction from mathematically correct ATAX.

## 2. Actual source authority and build

**S** denotes [ATAX/atax.cu at fixed commit dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/polybench-gpu-1.0/CUDA/ATAX/atax.cu), local path `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/polybench-gpu-1.0/CUDA/ATAX/atax.cu`, SHA256 `bca826a6e4fbdad67b11400ef2193210f43d8181441a0b9883e19445db049cfb`. All `S:line` references in this report name that exact file. The full audited content is preserved in [local snapshot](../../contributions/polybench/source_snapshot/ATAX/atax.cu); [source_manifest.json](../../contributions/polybench/source_manifest.json) records its 215 lines and SHA. The root coordinator independently matched the local Git blob to the fixed upstream commit ([SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json)); this certifies source bytes, not capture provenance. The suite header identifies PolyBench/GPU1.0. No arbitrary current upstream version was downloaded or substituted.

Makefile lines1-4 select this CU file/executable; `CUDA/common.mk` lines1-14 (SHA256 `0ec82001b07ad57057518e2e5b88a7bad6692f1fb1ab70a29b1ec9e89730d73d`) invoke `nvcc -O3` with configurable GENCODE macros sm10/13/20/30/35/50/60/62/70/75 and `NVCC_ADDITIONAL_ARGS`. This recipe is not the retained capture build command. Dimensions/FP32 are source definitions; no input-size CLI is parsed. Actual overrides, exact capture CUDA flags/architecture selection and capture ELF hash remain unresolved. Inspected cache bin/12.4 contains Rodinia binaries, no matching PolyBench ELF, and is not evidence for historical capture ELF. A capture path11.0 is a toolchain label, not suite version.

**Build-authority boundary.** S is a recovered, exact fixed-commit source candidate whose formulas agree with selected header geometry. It is not a certified capture-time source/ELF. A separate historical M5 branch pins `sgrauerg/polybenchGpu@5584aaa7d0be810ff5eb0b61c49fb64ecc81ba4c` (framework3b28d3064ab2d38a76bd826359f8aac9d8ecced2, M5_COMPUTE_WORKLOAD_MANIFEST.md lines9-16). The sm52 recipe lines31-32 and sm70 recipe lines11-22 have different flags/repair rules. See [BUILD_VARIANT_AUTHORITY.md](../../contributions/polybench/BUILD_VARIANT_AUTHORITY.md) for exact fixed source/script links and evidence. The chosen headers report NVBit1.4/tracer3, while the M5 contract declares NVBit1.8; M5 native/checker results cannot certify these historical traces. Source defects below are scoped to S unless explicitly tied by repair/source/ELF/trace hashes.

The separately pinned M5 source `sgrauerg/polybenchGpu@5584aaa7.../CUDA/ATAX/atax.cu` explicitly clears tmp/y inside kernels (lines82,97), unlike S. Its `atax.cuh` lines54-55 uses block32x8; GPU indexing ignores ty, so absent an override that source predicts128 CTAs and eight ty threads mapping each output. The frozen headers instead have16 CTAs,block256x1 and pointer-only kernel ABI. The unspecified-accumulator finding therefore belongs to S, not a proven defect in this captured ELF. M5 source, geometry and ABI cannot be substituted.

## 3. Host control and kernel execution sequence

main initializes A/x, selects device0, invokes GPU, then CPU reference and comparison (S:179-214). GPU allocates/copies four objects, launches atax_kernel1 then synchronize, atax_kernel2 then synchronize, DtoH y/free (S:139-176). Blocks(256,1), grids(16,1) for both;128 warps per phase. No host iteration. DtoH uses NX at S:170 although y length NY; equality4096 masks this generalized-dimension issue.

## 4. Every unique kernel implementation

atax_kernel1 (S:84-96): i=256*bx+tx, guard i<NX, loop j=0..4095, tmp[i]+=A[i*NY+j]*x[j]. atax_kernel2 (S:98-110): j=256*bx+tx, guard j<NY, loop i=0..4095, y[j]+=A[i*NY+j]*tmp[i]. Kernel2 consumes kernel1 tmp. One thread owns one output; each reduction is a serial per-thread recurrence. No shared tile, barrier, texture, atomic or reduction tree.

## 5. Thread mapping and address formulas

Address notation: allocation bases BA/Bx/etc; FP32 element4B; warp32 lanes and x-fast CUDA linearization. Counts below assume a full active warp,4B-aligned elements,128B-aligned bases/row starts and stated source dimensions. For address set U, theoretical units touched are `|{floor(a/L):a in U}|`, L=128 or32; include every byte of a multi-byte element. Unique useful bytes, line footprint and sector footprint are separate quantities. These counts are not measured traffic, hits, MSHR merges, reuse distance or DRAM repeated requests.

Let output coordinate q=q0+lane and reduction index t. Phase1: A=BA+4*(q*4096+t), x=Bx+4*t,tmp=Bt+4*q. Lane deltas16384/0/4 B; loop deltas4/4/0 B. Phase2: A=BA+4*(t*4096+q),tmp=Bt+4*t,y=By+4*q. Lane deltas4/0/4 B; loop deltas16384/4/0 B (S:86-107). Eight CTA warps cover256 rows in phase1/256 columns in phase2. Different CTAs own disjoint output and share the broadcast vector.

## 6. Dataflow, locality, coalescing and concurrency

At fixed t a full phase1 warp touches32 distinct128B lines and32 sectors for128 unique useful bytes: cold transfer-unit amplification32x/8x. Consecutive t then uses each row line over32 positions/sector over8; poor lane coalescing coexists with loop spatial reuse. Phase2 aligned contiguous warp uses1 line/4 sectors; a thread strides16KiB. Uniform vector operand uses1 line/sector for4 unique bytes, revisited by warps/CTAs. Phase1 CTA source traversal spans4MiB A. Both phases revisit64MiB A, and tmp has a producer/consumer edge; retention is conditional. Only16 CTAs/128 warps exist per phase, so active-SM coverage<=min(16,SMcount), regardless of4096 loop length. Independent A/vector addresses coexist with recurrent accumulation; actual outstanding requests require compiled scheduling/runtime evidence.

## 7. Frozen input and trace binding

DTC-L1 authority is fixed review commit `3b28d3064`, `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, program `P42-04`. Parameters `NO_ARGS`; frozen input digest `eededb785179fc0488c5a01d95154f6748ea45a2ea7bb18ecdbc316cf5166950`; bundle `2d610fb9d5b893ee16a8af0e178214d8a19715efb7709949ff6c89a57ce60561`. This digest identifies the registered trace input, not the original numeric matrix bytes. Trace entry `/root/workspace/assets/traces/bundles/2d610fb9d5b893ee16a8af0e178214d8a19715efb7709949ff6c89a57ce60561/tree/kernelslist.g`, kernelslist SHA256 `b6dcd0e3807bd71449d2283f97ba43a91868cb761e7b4924dd3d3063340a94ba`.

This audit read kernelslist and <=4096 header bytes per member (2 launches), not instruction bodies. HtoD command sizes match source object dimensions. All read headers: SM/binary version70, shared memory0,stream0,NVBit1.4,tracer3.

| Header symbol | Count | Grid | Block | Registers |
|---|---:|---|---|---:|
| `_Z12atax_kernel1PfS_S_` | 1 | `(16,1,1)` | `(256,1,1)` | 22 |
| `_Z12atax_kernel2PfS_S_` | 1 | `(16,1,1)` | `(256,1,1)` | 22 |

`SOURCE_VERIFIED=FIXED_GIT_BLOB_MATCH`; `INPUT_BOUND=FROZEN_TRACE_IDENTITY_ONLY`; `BINARY_BOUND=UNRESOLVED`; `TRACE_SCOPE_BOUND=HEADER_SEQUENCE_CONSISTENT_BODY_UNRESOLVED`; `RUNTIME_MEASURED=NOT_NEWLY_MEASURED`. Names/counts/grids match source, but headers cannot prove all CTA/warp bodies, scalar arguments, numeric contents, capture ROI command or source-to-ELF identity. Existing freeze label is `SOURCE_CONSISTENT_TWO_FULL_GRIDS` and explicitly does not newly certify exact executable/input linkage. EP-L2 requires its own frozen authority; no same-name cross-project equality is inferred.

The frozen ATAX excludes digest `dd8955feff97ab8c2013c32daccb3e916dc7dce6d435c913b4eaa0a61e64f308`. Existing `ATAX_PREFIX_PROOF.json` proves both bodies are exact prefixes of the selected full identity, with grid rewritten16->2 but unchanged4096-size copies. This is trim provenance, not a separately captured smaller application. This audit uses the existing proof without a new body scan.

## 8. Code-established architecture features

Code-established facts: source uses ordinary global pointer loads/stores, with no explicit shared array, CUDA constant/texture object, device local array or atomic in these definitions. Scalar state is register-eligible; actual register promotion, spills/local traffic, memory opcode selection and accumulator RMW frequency require emitted-code evidence. Pointer parameters are not restrict-qualified, so source += cannot be assumed to become one register accumulator plus one final store. Shared memory0 is independently reported by headers. Source-derived potential concurrency is distinct from actual simultaneous outstanding requests, queue occupancy, average latency and stall duration; none is measured here.

## 9. DTC-L1 and EP-L2 hypotheses requiring validation

DTC-L1: distinguish successive sectors of a retained row line from same-line pending merges; test searchable-tag and physical-line lifetime separately. The16-CTA ceiling may limit supply even with ample tags. PIB waiting may reflect recurrent output dependencies. EP-L2: compare32-sector scatter versus4-sector contiguous access, and tmp/A persistence across the phase boundary. No merge rate, hash-conflict rate or performance improvement follows from static source.

## 10. Evidence and limitations

Complete CU,Makefile,helper were read and preserved under [source_snapshot](../../contributions/polybench/source_snapshot); all unique kernel definitions and all launch sites were covered. CPU init/reference/comparison establish numeric/CPU boundaries. [trace_metadata.json](../../contributions/polybench/trace_metadata.json) preserves bounded-header observations and frozen record; [source_manifest.json](../../contributions/polybench/source_manifest.json) preserves hashes. Source commitment is independently verified by the coordinator, not inferred from name. Remaining gaps: UNINITIALIZED_TMP_Y; capture ELF/numeric contents/body completeness unresolved. No simulation/native/capture/experiment was started; no controller,registry,UUID,raw output,budget,existing input or accepted result was modified. Contradictions are audit findings, not retroactive rewriting of evidence.
