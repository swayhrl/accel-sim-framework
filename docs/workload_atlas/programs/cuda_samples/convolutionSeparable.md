# convolutionSeparable - source and behavior audit

## 1. Program and algorithm

Separable 2-D float convolution: B[y,x]=sum(j=-8..8) K[8-j]*I[y,x+j], O[y,x]=sum(j=-8..8) K[8-j]*B[y+j,x], with zero padding. CPU generates 17 coefficients and image, runs a reference two-pass convolution and relative L2 comparison. GPU stages cooperatively load tiles rather than issuing 17 global loads per output.

## 2. Source authority and build

Reviewed candidate: accel-sim/gpu-app-collection commit `b059fdae25c2aabf737486aada743fca114469ce`, path prefix `src/cuda/sdk/4.2/`. The freeze records a `cudasdk/9.1` capture path; these identities are not automatically equivalent. SOURCE_VERIFIED below means this immutable candidate implementation was read, not that capture source was certified. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) records file SHA-256 and Git blob IDs. Per-program Makefiles enumerate CU/CC inputs and include ../../common/common.mk. Capture-time nvcc command, expanded macros, architecture flags and ELF SHA remain unbound. Trace binary version=70 records a code target, not a compiler/build recipe. Candidate main.cpp:80-85 parses size3072 into384x192, iterations1, conflicting with frozen3072x3072 metadata. Kernel geometry is defined in convolutionSeparable.cu:33-36,111-114; KERNEL_RADIUS=8 in common.h. Candidate host is not the capture host authority.

## 3. Host control and launch order

main.cpp:104-140 initializes srand200, copies constant K and I, then loops i=-1,0: rows(I->B), columns(B->O), total4 launches. It then copies O to CPU, computes reference rows/columns, checks L2 and frees. Older local4.2 host has17 pairs. Frozen entry has just one rows and one columns launch: one complete spatial pair is observed, but warmup/timing capture selection is unresolved.

## 4. Distinct kernels

rows (convolutionSeparable.cu:38-80): block16x4, shared[4][160]=2560B; each thread loads8 main and up to2 halo elements, one barrier, computes8 results using17 shared/constant taps each. columns (:116-156): block16x8, shared[16][81]=5184B;8 main plus2 halo loads, one barrier,8 results. The81-entry pitch pads shared banks. Neither kernel uses global atomics. K accesses are same-index across lanes for a given j and use the constant path.

## 5. Thread and address formulas

Let tx,ty be thread coordinates, P=W. Rows x0=128*bx-16+tx, y=4*by+ty; global A+4*(y*P+x0+16*i), main i1..8, halo i0,9 predicated; shared[ty][tx+16*i+j]. Columns x=16*bx+tx, y0=64*by-8+ty; A+4*((y0+8*i)*P+x); shared[tx][ty+8*i+j]. Adjacent lanes differ4B within a16-lane half warp, but lane15->16 jumps4*(W-15)B to next row. Same-thread i steps64B in rows,32W B in columns. A column filter is therefore not warp-strided by W.

## 6. Dataflow, coalescing, locality and concurrency

For W3072 and128B-aligned bases, each64B half warp footprint uses1 line/2 sectors, so a warp uses2 lines/4 sectors across two rows for128 useful bytes. Rows i alternates64B halves of each line; columns i advances8 rows. Neighbor row CTAs overlap32 input columns around a128-column output boundary; neighboring column CTAs overlap16 rows around64 output rows. Interior row CTA loads640float/writes512, column loads1280/writes1024:1.25 input-cover ratio, reduced by edge zero padding. This is static redundancy, not measured miss/merge. Trace has18432 row and9216 column CTAs. CTAs are independent within each phase; columns waits for B from prior stream-ordered phase. Shared footprint, registers and barriers constrain residence, but no runtime MLP follows from CTA counts.

## 7. Frozen input and trace binding

Frozen digest4114a3dc0d06b55bc11aac0d0e4e209d5b640e8ec90fd84d8b4615871033f449, parameter __size_3072, bundle869cdb79... . HtoD68B and37748736B=3072^2*4; rows grid24x768/block16x4, columns192x48/block16x8. These establish recorded shape and pair coverage, not original generator-content SHA or application iteration count.

Independent cross-project review recomputed EP digest620f80f945d8ddbcef639e7e374fd2cb7122f8b07f239c82ccd32a2c4d90e79f from the same3 registered DTC members. EP and DTC selected input share registered trace content; this does not repair host/ELF provenance. See [independent cross-review](../../contributions/cuda_samples/EP_CROSS_REVIEW.json).

## 8. Source-proven architectural features

Regular cross-CTA halo overlap,17-tap shared reuse, constant coefficients, B write-then-read between kernels, two-row warp geometry and half-line segments are source-provable. Header shared allocation agrees with tile formulas. No global atomic or texture access is present.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: overlapping halo CTAs and later i accessing another half of an existing line may offer pending-line sharing, tag coverage and physical-line retention opportunities. EP-L2: B stage write/read, I/B/O working set108MiB and halo overlap may affect residency and write buffering. These need per-kernel request/sector, pending lifetime, PIB wait/wakeup and queue evidence; column naming or a speedup cannot prove a mechanism.

## 10. Evidence and limitations

Citations at the fixed commit: convolutionSeparable/convolutionSeparable.cu:23-26,38-103,116-179; main.cpp:80-85,104-140,148-177. SOURCE_VERIFIED=yes(candidate); INPUT_BOUND=yes(record/shape); BINARY_BOUND=no; TRACE_SCOPE_BOUND=one pair/full host unresolved; RUNTIME_MEASURED=no new measurements. Preserve host shape/iteration contradiction independently of accepted science.

Immutable source files (all references above use this commit and their stated line numbers): [convolutionSeparable.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/convolutionSeparable/convolutionSeparable.cu), [convolutionSeparable_common.h](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/convolutionSeparable/convolutionSeparable_common.h), [convolutionSeparable_gold.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/convolutionSeparable/convolutionSeparable_gold.cpp), [main.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/convolutionSeparable/main.cpp).
