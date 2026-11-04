# fastWalshTransform - source and behavior audit

## 1. Program and algorithm

Dyadic/XOR convolution R[i]=sum(j<K) D[i xor j]*K[j]. Pad K with zeros to D elements; compute FWT(D), FWT(K), elementwise multiply divided by D, then FWT(D). The final unnormalized Hadamard transform combined with1/D restores convolution. CPU direct convolution is the numerical reference.

## 2. Source authority and build

Reviewed candidate: accel-sim/gpu-app-collection commit `b059fdae25c2aabf737486aada743fca114469ce`, path prefix `src/cuda/sdk/4.2/`. The freeze records a `cudasdk/9.1` capture path; these identities are not automatically equivalent. SOURCE_VERIFIED below means this immutable candidate implementation was read, not that capture source was certified. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) records file SHA-256 and Git blob IDs. Per-program Makefiles enumerate CU/CC inputs and include ../../common/common.mk. Capture-time nvcc command, expanded macros, architecture flags and ELF SHA remain unbound. Trace binary version=70 records a code target, not a compiler/build recipe. fastWalshTransform.cu:60-75,94-104 parses-logK/-logD; kernel.cu:25 sets elementary threshold11. Candidate launch geometry agrees with11/19 trace, but does not establish capture binary ancestry.

## 3. Host control and launch order

Host :128-156 seeds srand2007, generates K/D, zeroes all device K, copies short K/full D; transform D, transform K, modulate D by K, transform D; DtoH and CPU reference. Each transform reduces logN by2,N by4 and increases M by4 while logN>11, launching fwtBatch2 each iteration; fwtBatch1 finishes.11/19 gives(4global+1shared)*3+modulate=16;7/21 gives(5+1)*3+1=19. logK changes nonzero input content, not the transform length.

## 4. Distinct kernels

fwtBatch2(kernel.cu:84-110): four global inputs/thread, register radix4 butterfly, four in-place stores, no barrier. fwtBatch1(:27-77): one CTA per vectorN<=2048; coalesced shared staging, barriers at each radix4 step, an extra radix2 step for odd logN, then barrier/writeback. For logN11 there are5 radix4 and1 radix2 stages. modulate(:139-150): fixed128x256 grid-stride, two global loads and one D store per element, no shared/atomic.

## 5. Thread and address formulas

Global pass p=256*bx+tx, l=p&(s-1), i0=4*(p-l)+l, iq=i0+q*s(q0..3); byte address A+4*(by*Nglobal+iq), Nglobal=4*256*grid.x. Host grid is constructed outside its loop(kernel.cu:120) and stays unchanged, so every global pass covers the full vector despite decreasing local N/M variables. Shared-pass global address A+4*(b*N+tx+k*T), T=N/4,k0..3. Shared butterfly uses the same iq form. Modulation pos=256*b+tx+k*32768, same-thread stride131072B, adjacent-lane delta4B.

## 6. Dataflow, coalescing, locality and concurrency

11/19: D524288, s131072,32768,8192,2048 in four grid512x1/block256 passes; finalN2048,M256,T512/shared8192B. At these power-of-two strides a warp stays within each contiguous iq stream:128B-aligned stream=1line/4sectors, four q streams=4lines/16sectors for512 useful bytes. q distance4s is not lane stride. Shared staging same-thread step2048B still has contiguous lanes. Modulation handles16 elements/thread (64 for7/21). Kernel boundaries serialize dependent in-place passes; CTAs are independent per pass.512-thread/8192B final CTAs impose resource limits; real concurrent requests and blocking cycles are unmeasured.

## 7. Frozen input and trace binding

Frozen selected f7f22a2ccc836a8a9b2096d4df50caf00a2c4bcebc7b16d064b8b0287ce593d3,11/19,bundle7295c0b7... . HtoD8192B=2^11*4 and2097152B=2^19*4. Header order4G+S,4G+S,M,4G+S exactly matches16-launch recipe. Alternate6e35d612... is7/21 and must remain separate from main; EP-L2 FWT_7_21 requires member-hash/ROI comparison before equivalence.

Independent cross-project review recomputed EP FWT_7_21 digestf3695b85379fb762faaf9830bda449e0a5f1e4d3e351774cf33d90850059b460 from DTC alternate6e35d612...20members. It matches the alternate, not DTC selected11/19. See [independent cross-review](../../contributions/cuda_samples/EP_CROSS_REVIEW.json).

## 8. Source-proven architectural features

Three unique kernels; repeated dense in-place sweeps, four separated but warp-contiguous input streams, shared butterflies, stream-ordered dependencies and reads of zero-padded K are established. Zero data does not imply absent requests.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: four independent global loads supply potential instruction-level memory parallelism; butterfly dependencies and later passes can expose tag coverage, PIB wait and wakeup effects. EP-L2: repeated D/K scans and modulation read/modify/write may affect phase retention and write-buffer occupancy.11/19 versus7/21 changes working set and global-pass count; mechanism and cache hits require runtime evidence.

## 10. Evidence and limitations

Fixed source fastWalshTransform/fastWalshTransform.cu:60-75,94-104,128-156; fastWalshTransform_kernel.cu:25-77,84-131,139-150. SOURCE_VERIFIED=yes(candidate); INPUT_BOUND=yes(shape/record); BINARY_BOUND=no; TRACE_SCOPE_BOUND=16-launch source-consistent recipe, capture command/ELF/content not newly certified; RUNTIME_MEASURED=no new measurements.

Immutable source files (all references above use this commit and their stated line numbers): [fastWalshTransform.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/fastWalshTransform/fastWalshTransform.cu), [fastWalshTransform_gold.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/fastWalshTransform/fastWalshTransform_gold.cpp), [fastWalshTransform_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/fastWalshTransform/fastWalshTransform_kernel.cu).
