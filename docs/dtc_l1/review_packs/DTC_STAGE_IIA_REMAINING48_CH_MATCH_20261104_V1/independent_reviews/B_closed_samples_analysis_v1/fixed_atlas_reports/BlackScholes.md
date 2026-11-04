# BlackScholes - source and behavior audit

## 1. Program and algorithm

Price independent European calls and puts from arrays stock S,strike X,years T with scalar riskfree R=.02 and volatility V=.30. d1=(log(S/X)+(R+V^2/2)T)/(V sqrt(T)),d2=d1-V sqrt(T); call=S*CND(d1)-X*exp(-RT)*CND(d2),put=X*exp(-RT)*(1-CND(d2))-S*(1-CND(d1)). CND uses a polynomial approximation and sign branch.

## 2. Source authority and build

Reviewed candidate: accel-sim/gpu-app-collection commit `b059fdae25c2aabf737486aada743fca114469ce`, path prefix `src/cuda/sdk/4.2/`. The freeze records a `cudasdk/9.1` capture path; these identities are not automatically equivalent. SOURCE_VERIFIED below means this immutable candidate implementation was read, not that capture source was certified. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) records file SHA-256 and Git blob IDs. Per-program Makefiles enumerate CU/CC inputs and include ../../common/common.mk. Capture-time nvcc command, expanded macros, architecture flags and ELF SHA remain unbound. Trace binary version=70 records a code target, not a compiler/build recipe.

## 3. Host control and launch order

BlackScholes.cu:54-60 fixes100000 options/one iteration; :133-147 seeds5347 and generates S in[5,30],X[1,100],T[.25,10], copies three arrays. :155-168 launches480CTA x128threads once. :183-207 copies call/put, computes CPU reference and error; host handles allocation/device choice and cleanup. No GPU warmup appears in this loop.

## 4. Distinct kernels

Only BlackScholesGPU(kernel.cuh:71-98). Grid-stride loop covers exactlyoptN, calls inline BlackScholesBodyGPU(:42-65); cndGPU(:17-35) uses fabs/exp/polynomial and d>0 branch. No shared memory, barriers, atomics, texture or inter-thread reduction. Inputs and outputs are separate arrays.

## 5. Thread and address formulas

tid=128*b+t, Tgrid=480*128=61440; opt=tid+k*61440 while opt<100000. Each input address Xbase+4*opt; each result C/Pbase+4*opt. Warp lanes differ4B; same thread next option245760B away. First38560 threads handle2 options, remaining22880 handle1. CTA warps access successive128B segments of each array, CTA boundaries contiguous. Branch condition depends on numerical d, but addresses remain regular.

## 6. Dataflow, coalescing, locality and concurrency

For aligned full warps, each of3 input loads and2 result stores covers1line/4sectors for128 useful bytes per array; tail100000 is a multiple32, so no partial warp in this case. There is no cross-option temporal reuse; same-thread successive elements are far apart. Three input loads may be independent before arithmetic; log/sqrt/exp and CND dependencies limit overlap.480CTAs provide schedulable work,4warps each; actual occupancy/MLP depends on hardware and compiled23-register header, not source alone.

## 7. Frozen input and trace binding

Selected digestb31a85e4eb8d32ef5d706c2a84c999f6e3af598b1df43c85e149d03fa1568ac0,NO_ARGS,bundlee99c1422... . Three HtoD transfers400000B each,oneBlackScholesGPU grid480/block128/shmem0,nregs23. These agree with100000 candidate options; original random-content SHA and capture ELF remain unbound.

## 8. Source-proven architectural features

Three streaming read arrays,two write arrays,scalar coefficients,independent outputs and expensive per-option arithmetic. Repeated option execution is not hidden in the single host iteration. Source has no global atomic or shared reuse.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: streaming provides a control case for allocation/retirement and unrelated pending lines; independently loaded S/X/T do not imply same-address merge. EP-L2: read/write balance and stream concurrency can test tag/data and write-buffer service. Whether arithmetic limits memory pressure,or allocations pollute cache,requires runtime counters; simple coalescing does not predict speedup.

## 10. Evidence and limitations

Fixed paths BlackScholes/BlackScholes.cu:54-60,133-168,183-207; BlackScholes_kernel.cuh:17-35,42-98. SOURCE_VERIFIED=candidate; INPUT_BOUND=recorded100000; BINARY_BOUND=no; TRACE_SCOPE_BOUND=single launch source-consistent; RUNTIME_MEASURED=no new measurements. Same name in other CUDA Samples releases may use float2 kernels and must not replace this scalar grid-stride implementation.

Immutable source files (all references above use this commit and their stated line numbers): [BlackScholes.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/BlackScholes/BlackScholes.cu), [BlackScholes_gold.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/BlackScholes/BlackScholes_gold.cpp), [BlackScholes_kernel.cuh](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/BlackScholes/BlackScholes_kernel.cuh).
