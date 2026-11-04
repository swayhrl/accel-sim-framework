# scalarProd - source and behavior audit

## 1. Program and algorithm

Compute vectorN independent dot products C[v]=sum(j=0..elementN-1) A[v*elementN+j]*B[v*elementN+j]. A/B are contiguous row-major vectors. Host generates floats, runs one GPU reduction, copies C and compares CPU dot products. There is no inter-vector mathematical dependency.

## 2. Source authority and build

Reviewed immutable candidate accel-sim/gpu-app-collection@b059fdae25c2aabf737486aada743fca114469ce under src/cuda/sdk/4.2/. The freeze records cudasdk/9.1 capture paths, not newly certified source ancestry. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) provides file SHA-256 and Git blob IDs. Makefiles list CU/CC files and include ../../common/common.mk; capture-time nvcc flags, architecture macros and ELF SHA are not bound. Header binary version70 is metadata, not a build recipe. SOURCE_VERIFIED refers to this candidate only. scalarProd.cu:66-74 parses --size as VECTOR_N, :90-98 fixes ELEMENT_N1024. kernel.cu:22 uses __mul24 for vectorBase and :33 sets ACCUM_N1024. For selected13920*1024=14254080, operands fit signed24-bit multiplication input bounds; different larger shapes need rechecking.

## 3. Host control and launch order

Host :126-146 seeds123, fills A/B in[0,1], copies each full array, synchronizes then launches scalarProdGPU<<<128,256>>> once; DtoH and CPU reference follow(:150-164). VECTOR_N13920 overrides default64. The single launch internally cycles vectors; do not equate128CTAs with128output vectors.

## 4. Distinct kernels

scalarProdGPU(kernel.cu:34-79) owns shared accumResult[1024]=4096B. Each CTA loops vec=b;vec<vectorN;vec+=128. Each thread initializes4 accumulators iAccum=t+256*k,each accumulates positions separated1024. A barrier at each stride512,256,...,1 protects shared tree reductions. Thread0 writes C[vec]. On the next vector, threads overwrite distinct accumulators and encounter a barrier before reduction. No global atomic or second reduction kernel is used.

## 5. Thread and address formulas

vec=b+128*r; base=elementN*vec; iAccum=t+256*k(k0..3). Load addresses A/B+4*(base+iAccum+1024*q) while pos<base+elementN; selected elementN1024 permits onlyq0. Lane delta4B, same-thread k step1024B, outer-vector step4*1024*128=524288B. Reduction uses shared[iAccum] and shared[stride+iAccum],with participating loop t<stride. Output C+4*vec is issued only by thread0,not coalesced acrossCTA lanes.

## 6. Dataflow, coalescing, locality and concurrency

For aligned A/B,each full warp load uses1line/4sectors; four k rounds cover each4096B vector once per array. CTA warps read adjacent128B chunks; no cross-CTA vector overlap. CTA b0..95 handles109vectors and b96..127 handles108 because13920=128*108+96. Barriered reductions and serial outer loop limit progress despite large input. Only128CTAs are schedulable,8warps each; residency also constrained by4096Bshared and23-register header. AcrossCTAs consecutive scalar outputs share cachelines but are separate stores; cannot infer write merge without runtime evidence.

## 7. Frozen input and trace binding

Selected2b93f70cd0666c5112f5550aae7b3a8d0565de1de40604d494bdc36c503f6954, __size_13920,bundlee3365640...; A/B HtoD57016320B each=13920*1024*4. Header single scalarProdGPU grid128/block256,shared4096,nregs23. Alternatefd0772a8... has a different input identity. Recorded shape/launch agree with candidate parser and kernel; exact original content and capture ELF not newly certified.

## 8. Source-proven architectural features

Two streaming reads per dot-product element, shared reduction, repeated vectors within a persistent fixed grid, scalar output stores and no global atomics. Small fixed CTA count versus totalvectors is an essential concurrency boundary.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: independent A/B loads followed by reduction and repeated CTA-ownedvectors may expose PIB wait and retirement at barrier phases; no intended input same-address sharing exists. EP-L2: scalar stores from manyCTAs may share output sectors while input streams dominate; tag/data/write-buffer impacts require measured transactions. Long outer loops do not themselves mean high MLP.

## 10. Evidence and limitations

Fixed scalarProd/scalarProd.cu:66-74,90-98,126-164; scalarProd_kernel.cu:22,33-79. SOURCE_VERIFIED=candidate; INPUT_BOUND=yes(shape/record); BINARY_BOUND=no; TRACE_SCOPE_BOUND=single source-consistent launch; RUNTIME_MEASURED=no new measurements. Floating reduction order differs from sequential CPU,which is why existing numerical correctness is a separate proof dimension.

Immutable source files (all references above use this commit and their stated line numbers): [scalarProd.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/scalarProd/scalarProd.cu), [scalarProd_gold.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/scalarProd/scalarProd_gold.cpp), [scalarProd_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/scalarProd/scalarProd_kernel.cu).
