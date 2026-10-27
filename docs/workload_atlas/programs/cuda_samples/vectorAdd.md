# vectorAdd - source and behavior audit

## 1. Program and algorithm

For Nfloat elements, C[i]=A[i]+B[i]. CPU initializes random A/B, GPU adds once, CPU copies C back and validates absolute difference<=1e-5. This is a streaming boundary/control case,not a proxy for the complex atlas workloads.

## 2. Source authority and build

Reviewed candidate: accel-sim/gpu-app-collection commit `b059fdae25c2aabf737486aada743fca114469ce`, path prefix `src/cuda/sdk/4.2/`. The freeze records a `cudasdk/9.1` capture path; these identities are not automatically equivalent. SOURCE_VERIFIED below means this immutable candidate implementation was read, not that capture source was certified. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) records file SHA-256 and Git blob IDs. Per-program Makefiles enumerate CU/CC inputs and include ../../common/common.mk. Capture-time nvcc command, expanded macros, architecture flags and ELF SHA remain unbound. Trace binary version=70 records a code target, not a compiler/build recipe.

## 3. Host control and launch order

vectorAdd.cu:86-119 initializes defaultN50000, ParseArguments(:170-183) overrides --size/-size; allocates A/B/C, copies A/B,launches ceil(N/256)CTAs of256threads once. :127-133 copies C and verifies all elements; no iterative GPU loop or convergence condition.

## 4. Distinct kernels

Only VecAdd(:78-83),one index/thread and predicate i<N. No shared,barrier,atomic,reduction,texture or additional GPU validation kernel. Error handling and randomInit(:162-167) are host work.

## 5. Thread and address formulas

i=256*blockIdx.x+threadIdx.x; A/B load addresses base+4*i,Cstore base+4*i for i<N. Lane stride4B,no per-thread address loop. Adjacent warps differ128B and adjacentCTAs1024B. For N6000000,grid23438 has128 active threads in its final256-threadCTA,4 active and4 inactive warps; N divisible32 yields no partially active warp.

## 6. Dataflow, coalescing, locality and concurrency

Aligned full warp: each input/output instruction covers1line/4sectors and128 useful bytes; three distinct arrays mean384 useful bytes/warp,not a single shared line. No cross-CTA logical data reuse; stores follow two independent loads then one arithmetic dependency.23438CTAs allow extensive potential scheduling,while compiled resources/SM limits bound residence. No runtime request concurrency follows directly from the large grid.

## 7. Frozen input and trace binding

Selected e7bb67e63e3c38478ff50db4dcc25dee9262fe195b30589547b1ac5e2bc3d799,__size_6000000,bundled57ff01e... . Two HtoD24000000B,oneVecAdd grid23438/block256/shmem0/nregs12. Alternate3aac3b72... N4000000 has a distinct digest/bundle and is not automatically pooled with selected6M or EP-L2 input.

Independent cross-project review recomputed EP vectorAdd_4M digest138f33b61fffe99c5e9c31a5943a96edcab180e6aaaa5ed4714021249c0d2940 from DTC alternate3aac3b72...2members. It does not match selected6M.4M has15625 fullCTAs;6M has23438CTAs and a half-active finalCTA. See [independent cross-review](../../contributions/cuda_samples/EP_CROSS_REVIEW.json).

## 8. Source-proven architectural features

Two regular independent reads,one output store,tail predication,zero sharing or global atomic. Input total48MB/output24MB are source/shape-derived bytes,not measured L2/DRAM traffic or cache miss counts.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: test overhead/retirement behavior under coalesced streaming and absence of intentional same-address reuse; pending/tag coverage must be measured. EP-L2: read/write service and write buffering may limit throughput; cache pollution and allocation effects are hypotheses. Compare4M/6M only with explicit input andtrace binding.

## 10. Evidence and limitations

Fixed vectorAdd/vectorAdd.cu:78-83,86-133,162-183. SOURCE_VERIFIED=candidate; INPUT_BOUND=yes(shape/record); BINARY_BOUND=no; TRACE_SCOPE_BOUND=single source-consistent launch; RUNTIME_MEASURED=no new measurements. Historical native correctness,simulator completion andsource reading are separate proof dimensions.

Immutable source files (all references above use this commit and their stated line numbers): [vectorAdd.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/vectorAdd/vectorAdd.cu).
