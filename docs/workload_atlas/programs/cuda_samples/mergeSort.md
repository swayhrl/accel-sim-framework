# mergeSort - source and behavior audit

## 1. Program and algorithm

Ascending key/value merge sort: sort fixed1024-element tiles in shared memory; for strides1024,2048,... merge pairs of sorted ranges. Sample every128 keys to partition each merge into independently handled small intervals. Inclusive versus exclusive binary searches give stable placement for equal keys. Values move with keys and are validated after the GPU result is copied back.

## 2. Source authority and build

Reviewed immutable candidate accel-sim/gpu-app-collection@b059fdae25c2aabf737486aada743fca114469ce under src/cuda/sdk/4.2/. The freeze records cudasdk/9.1 capture paths, not certified source ancestry. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) contains file SHA-256 and Git blob IDs. Makefiles list CU/CC files and include ../../common/common.mk; capture-time nvcc flags, expanded macros and ELF SHA are not bound. Header binary version70 does not certify a compiler or build recipe. SOURCE_VERIFIED means this candidate implementation was read. mergeSort_common.h:19-20 fixes SHARED_SIZE_LIMIT1024 and SAMPLE_STRIDE128. main.cpp:31-34 fixes N8192,DIR1,numValues65536. sortDir is a host-selected template specialization1 (ascending) or0 (descending),not a runtime address-independent label. bitonic.cu defines alternative bitonicSortSharedKernel and bitonicMergeElementaryIntervalsKernel, but the reviewed mergeSort() path calls merge kernels, and neither appears in this trace.

## 3. Host control and launch order

main.cpp:45-83 seeds2009, generates keys modulo65536 and associated values, copies two arrays, initializes rank/limit buffers, calls mergeSort once, copies keys/values and validates. mergeSort.cu:505-545 computes stage count3 and chooses initial buffer parity so final output lands in Dst; initial shared sort, then each stride1024,2048,4096: generateSampleRanks,mergeRanksAndIndices(A),mergeRanksAndIndices(B),mergeElementaryIntervals,swap input/output buffers. Total1+3*4=13 launches. Partial unpaired tails use DtoD memcpy(:537-540); at8192 every stride divides N and the tail copy has0bytes.

## 4. Distinct kernels

mergeSortSharedKernel(:89-133):512threads each loads2 key/value pairs into shared arrays1024 each; for stride1..512,shared binary-search placement with barriers,then stores2 pairs. generateSampleRanksKernel(:166-204): each active thread samples one point per half, binary-searches opposite range and emits two rank arrays. mergeRanksAndIndicesKernel(:231-261): merges sample ranks by binary search into interval limits; invoked separately for A/B. mergeElementaryIntervalsKernel(:336-408): thread0 loads starts/ends from limits into6 shared scalars; participating threads load bounded A/B slices into shared key/value arrays256 each, binary-search merge there, barrier,write two contiguous result slices. Four unique definitions,13 launches; no atomic or cross-CTA barrier inside a kernel.

## 5. Thread and address formulas

Initial tile global indices1024*b+t+512*k(k0,1),lane delta1word, same-thread k step2048B. For rank p=256*b+t,i=p&((stride/128)-1),segmentBase=(p-i)*256; sampled key index segmentBase+i*128 or +stride+i*128; searches read opposite base+min(pos+searchStep,L)-1,with searchStep halved according to data comparisons. Rank arrays have offsets segmentBase/128+i and +stride/128+i. Rank-merge changes pointer offset2*(p-i),writes index binarySearch(other ranks)+i. Interval kernel j=b&((2*stride)/128-1),segmentBase=(b-j)*128; global A addresses base+4*(segmentBase+startA+t), B adds stride+startB+t; writes segmentBase+startA+startB+t and +lenA+t for A/B slices. start/len values are data dependent limits; shared searches operate on staged keys.

## 6. Dataflow, coalescing, locality and concurrency

Aligned initial loads/stores: each warp instruction1line/4sectors; two rounds cover1024 key/value pairs. Rank samples have512B spacing within each half,so32 lanes may touch up to32lines/sectors; segment-boundary and search convergence determine exact footprint. Binary-search addresses cannot be assigned a fixed stride or cache-hit rate. Interval loads/stores are contiguous active prefixes but arbitrary starting offsets can span extra sectors/lines: for m consecutive4B words starting bytea, lines=floor((a+4m-1)/128)-floor(a/128)+1 and sectors analogous32; unknown start alignment prevents exact count. Initial8CTAs of512threads/shared8192B; rank stages only1CTA256threads with32 active; each elementary stage64CTAs128threads/shared2072B. Kernel boundaries order rank->limit->interval; stages serialize sorted-range dependence. Many keys can be repeatedly searched but real pending overlap and occupancy remain unknown.

## 7. Frozen input and trace binding

Selected dd9f695c4f53b08394e7fd53a9eecedfd8372aa5cda7aae047f8a70162a40c48,NO_ARGS,bundle0c9aff46... . Two HtoD32768B prove8192words per key/value input. Header sequence initial grid8/block512 then3*(rank1x256,limits1x256 twice,interval64x128),templateLj1; initialshared8192/interval2072. This is a full source-consistent8192 sort sequence,not a single sorting kernel. Original content/capture build remain uncertified.

## 8. Source-proven architectural features

Multi-phase key/value ping-pong, data-dependent global binary searches, shared fine-grained merges, narrow rank-phase concurrency, stable equal-key search asymmetry and nonzero-sized whole-range input streaming. Global search phases and shared merge phases must be analyzed separately.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: global rank searches may converge on identical lines, creating potential tag sharing and pending merge; search iterations form load-to-branch-to-address dependency chains. The small rank grid can limit concurrent pressure despite expensive searches. EP-L2: repeated stage ping-pong, rank/limit objects and interval output stores may change residency/write buffering. Cacheline conflicts, search sharing, queue occupancy and blocked cycles need runtime address/timing evidence; sortedness alone predicts none of these.

## 10. Evidence and limitations

Fixed mergeSort/main.cpp:31-34,45-100; mergeSort_common.h:19-20; mergeSort.cu:56-82,89-158,166-291,298-449,505-545. SOURCE_VERIFIED=candidate; INPUT_BOUND=yes(shape/record); BINARY_BOUND=no; TRACE_SCOPE_BOUND=13-launch recipe consistent; RUNTIME_MEASURED=no new measurements. Uncalled bitonic alternatives are not promoted into the actual sequence; descending specialization and partial tails remain source branches,not observed selected-input behavior.

Immutable source files (all references above use this commit and their stated line numbers): [bitonic.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/mergeSort/bitonic.cu), [main.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/mergeSort/main.cpp), [mergeSort.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/mergeSort/mergeSort.cu), [mergeSort_common.h](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/mergeSort/mergeSort_common.h), [mergeSort_host.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/mergeSort/mergeSort_host.cpp), [mergeSort_validate.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/mergeSort/mergeSort_validate.cpp).
