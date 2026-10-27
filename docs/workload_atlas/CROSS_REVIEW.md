# Independent source and address cross-review

Coordinator review is independent of the suite report author. The coordinator directly read the fixed local source files below, independently derived addresses, and checked finite sets with `tools/review_address_sets.py`. The exact-byte upstream comparison in `SOURCE_BLOB_VERIFICATION.json` fixes all cited PolyBench/Rodinia files to GPU App Collection `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. This is a CPU-only algebra check, not native execution or performance validation.

## ATAX, MVT, BICG: lane direction is not loop direction

- `src/cuda/polybench-gpu-1.0/CUDA/ATAX/atax.cu:84-109,148-166`: kernel1 one thread per row, address `A+4*(i*4096+j)`, lane delta16384B, loop delta4B. Kernel2 one thread per column, `A+4*(i*4096+j)`, lane delta4B, loop delta16384B. Each launch has only16 CTAs of256 threads at4096, so grid parallelism is bounded even though each CTA has8 warps. Kernel2 consumes tmp from kernel1; the host synchronization creates a real phase boundary.
- `.../MVT/mvt.cu:109-166`: first kernel row-thread stride16384B across lanes; second kernel contiguous columns across lanes. Both matrix operations read the same matrix but update different vectors. The default-stream launch order is sequential; the two kernels lack ATAX's tmp producer/consumer dependency. A dependency analysis must not treat these applications as identical because their address formulas resemble each other.
- `.../BICG/bicg.cu:99-130,177-185`: source order is contiguous kernel1 for `s=A^T*r`, then strided kernel2 for `q=A*p`; this reverses ATAX/MVT's ordering. Outputs are explicitly zeroed inside these kernels (lines105,123), unlike ATAX's uninitialized accumulators. Host synchronization follows each launch.

For a full32-lane FP32 memory instruction with4096 row pitch, strided A touches32 distinct128B lines and32 distinct32B sectors. Contiguous aligned A touches1 line and4 sectors. Useful per-lane bytes total128B. If every touched unit were fetched once, geometric line footprints are4096B vs128B, sector footprints1024B vs128B. These ratios are footprints for one instruction, not measured traffic or miss rates. In the strided version, each thread's successive loop positions are adjacent, making temporal reuse of a fetched line possible; that does not prove its retention. Unknown base alignment changes contiguous counts and must stay conditional.

## 2DCONV: repeated offsets and halo union

`.../2DCONV/2DConvolution.cu:108-143`: warp has fixed `i` and `j=j0+lane`, block32x8, grid128x512 at4096 square. Each tap address is `A+4*((i+dy)*4096+j+dx)`, dy,dx in{-1,0,1}. Lane delta4B; adjacent warps move a row16384B. It is one launch with no shared-memory tiling or CTA barrier, not a row/column separable convolution.

For an interior full warp with j0 a multiple32 and aligned row base, center tap touches1 line/4 sectors; either horizontal halo tap touches2 lines/5 sectors. The union of the nine tap addresses is3 rows x34 FP32 values =408 distinct useful bytes, spanning9 lines/18 sectors because a one-word halo crosses BOTH aligned row-chunk ends. This union is not the sum of nine independently issued instruction footprints and not a measured request count. Eight adjacent warps in a full interior CTA have a union10x34 values,30 lines/60 sectors. CTA boundaries may reuse halo data but scheduling/cache state is unknown. Boundary masks reduce the active address sets.

## GEMM: broadcast and row streaming without software tiling

`.../GEMM/gemm.cu:124-162`: `j=32*bx+tx`, `i=8*by+ty`, with one output per thread and512 iterations. `A+4*(i*512+k)` is uniform within a warp; `B+4*(k*512+j)` is contiguous across lanes and strides2048B across loop iterations. C is read/scaled/accumulated at a fixed per-thread address in source. No source shared-memory tile or barrier exists. Compiler register promotion and precise SASS load/store frequency cannot be inferred from the `+=` spelling alone.

At512 square, grid16x64 yields1024CTAs. The same A row values can be requested by16 x-direction CTAs, and the same B values by64 y-direction CTAs; these are static sharing opportunities, not simultaneous pending merges or L1 hits. Hash/set conflict requires actual address mapping and mapping policy, which source indexing alone does not establish.

## particlefilter_naive: uniform CDF walk, dependent coordinate gather

`src/cuda/rodinia/3.1/cuda/particlefilter/ex_particle_CUDA_naive_seq.cu:32,113-133,473,543-569`: block128, one particle per thread, `Nfr-1` launches. CPU performs motion, likelihood, weights, CDF and thresholds; GPU performs resampling only. Each active lane at a particular loop iteration reads `CDF+8*x` (uniform) and `u+8*i` (contiguous FP64), then breaks depending on its threshold. CDF loop delta8B; arrayX/Y gather is `base+8*index(i)`, value-dependent. Output xj/yj is contiguous FP64. Under a valid monotonic CDF and ordered thresholds, selected indices are correlated/nondecreasing, so calling all CDF accesses random is incorrect. Numerical validity and precise gather-sector counts are not established by source alone.

At a full aligned32-lane step, one uniform CDF word touches1 line/1 sector; a contiguous32-lane FP64 output touches2 lines/8 sectors. A single outstanding dependent search per thread and divergence can limit independent work despite repeated same-address scans. Pending overlap, merge counts and PIB waiting remain hypotheses.

## Identity and scope checks

The coordinator confirmed the inherited ATAX prefix proof distinguishes full grid16 from a body-prefix derivative whose grid was rewritten2. The ordinary identity is preserved. Header compatibility cannot reconstruct missing capture ELF or original input bytes. Every conditional program remains unselected. The EP specialist independently recomputes EP's canonical member-list composite from DTC member metadata, while the CUDA/Parboil specialists review source reuse; this checks complete member metadata rather than names or unequal top-level digest strings. See the cross-project evidence and review status for exact matches, alternates and unresolved cases.

## Reproduction

Run `python3 docs/workload_atlas/tools/review_address_sets.py` from the isolated tree. `ADDRESS_REVIEW_VALIDATION.json` records explicit conditions and12 enumerated cases. The suite authors' additional checks live under `contributions/`; findings that would change accepted science are logged separately in `EVIDENCE_GAPS.md`.
