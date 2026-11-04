# histogram - source and behavior audit

## 1. Program and algorithm

Two histogram algorithms over the same byte array:64bins count the top6bits of each byte;256bins count all8bits. Each first-pass CTA forms a partial histogram in shared memory and writes global partials; one CTA per bin reduces all partials to final counters. CPU references and comparisons follow each algorithm,so the64bin and256bin outputs are separate tests.

## 2. Source authority and build

Reviewed immutable candidate accel-sim/gpu-app-collection@b059fdae25c2aabf737486aada743fca114469ce under src/cuda/sdk/4.2/. The freeze records cudasdk/9.1 capture paths, not newly certified source ancestry. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) provides file SHA-256 and Git blob IDs. Makefiles list CU/CC files and include ../../common/common.mk; capture-time nvcc flags, architecture macros and ELF SHA are not bound. Header binary version70 is metadata, not a build recipe. SOURCE_VERIFIED refers to this candidate only. histogram_common.h:18-44 defines bins64/256,64threads for64bin and6warps=192threads for256bin. histogram256.cu:22 sets USE_SMEM_ATOMICS0: default uses volatile tagged warp-local retries(:27-33),not atomicAdd. Alternate=1 uses shared atomicAdd(:35-43),with CUDA_NO_SM12_ATOMIC_INTRINSICS compile guard. Neither branch is a global atomic. Actual capture branch is not proven by kernel name.

## 3. Host control and launch order

main.cpp:163,175 fixes numRuns1,byteCount65536; optional sizemult1..10 scales input. srand2009 generates bytes. After HtoD,init64; iter=-1,0 each calls histogram64(first then merge),copies64bins and CPUchecks,closes64; init256 then iter=-1,0 calls histogram256(first then merge),copies256bins and CPUchecks. Total8launches with warmup included matches entry.64bin first grid ceil(B/(64*240))=5,256bin first grid always240.

## 4. Distinct kernels

histogram64Kernel(:73-122) loads uint4,updates16byte counts in per-thread byte-sized shared histograms with threadPos permutation; no atomic contention between threads. Max per-thread submissions are constrained by histogramCount formula(:194). After barrier,threads0..63 sum all thread counters for one bin and store partials. mergeHistogram64Kernel(:135-154) reads one bin across partials,shared256-way reduction,thread0 store. histogram256Kernel(:53-81) uses6warp-local256bin shared histograms,updates4bytes per uint via tagged retry or shared atomics,barrier,merges6warps per-bin to global. mergeHistogram256Kernel(:92-111) analogously reduces240partial histograms. These are4 unique kernels,each twice.

## 5. Thread and address formulas

64input address D+16*(64*b+t+k*64*G),G5. threadPos=(t&~63)|((t&15)<<2)|((t&48)>>4); shared byte address H+threadPos+64*bin. Output partial P+4*(64*b+bin).256input D+4*(192*b+t+k*192*240),shared word index256*(t>>5)+bin wherebin is data dependent; output P+4*(256*b+bin),bin=t or t+192 whenvalid. Merge forH64/256 reads P+4*(bin+(t+256*k)*H),writes O+4*bin onlyt0. Merge lane strides256B/1024B,while same-thread iterations step65536B/262144B; these are not input load strides.

## 6. Dataflow, coalescing, locality and concurrency

Aligned64first-pass uint4 footprint512B/warp=4lines/16sectors if compiled as16B vector accesses; per-component scalarization can change instruction-level sectors.256first-pass warp128B=1line/4sectors.64first grid5 supplies just10warps; each thread loads12or13uint4 (192/208bytes),and byte counters stay below255.256grid 240 has dataCount16384words:86CTAs have any input (last64threads active),154CTAs still initialize/write zero partials. Merge64 has only5active source lanes/CTA,5different lines/sectors per bin; merge256 has240lanes,full warps touch32different lines/sectors,128usefulB/1024sectorB (8xsector amplification). Adjacentbin CTAs may reuse sectors across time; this is not measuredhit/merge. Shared update dependencies and barriers bound concurrency.

## 7. Frozen input and trace binding

Selected3722a5c85d91a9482233c2bf128a6721e3fb194db3e5e54be6cbec9598518a58,NO_ARGS,bundleb30068c7... . HtoD65536B; observed64first/merge repeated2 then256first/merge repeated2; grids5,64,240,256,blocks64,256,192,256. Headers shared4096,1024,6144,1024. Input-byte count and launchpattern consistent; capture branch/ELF/content not certified.

## 8. Source-proven architectural features

Four-stage-type program, data-dependent shared addresses and retries, regular global input streams, strided cross-partial global merge, repeated whole algorithms and output reuse. Sparse activeinput CTAs in256first pass and tiny64first grid limit usefulparallelism. No source-supported globalatomic claim.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: global merge's sparseper-warp sectors and interCTA bin-neighbor overlap may affect searchabletag demand and pendingline sharing,while shared counters mostly bypass globalcache. EP-L2: partial histogram write/read,240zero-inclusivepartial CTAs and stridedmerge may affect tag/data occupancy and write buffering. Data distribution controls shared retry contention; source does not yield retrycounts or L2atomictransactions. Capture branch must be resolved before attributing timing.

## 10. Evidence and limitations

Fixed histogram/main.cpp:163-175,207-229,232-311; histogram64.cu:60-121,135-154,194-210; histogram256.cu:22-43,53-111,118,159-175; histogram_common.h:18-44. SOURCE_VERIFIED=candidate; INPUT_BOUND=yes(shape/record); BINARY_BOUND=no; TRACE_SCOPE_BOUND=8launch recipe consistent; RUNTIME_MEASURED=no new measurements. Warp-synchronous volatile algorithm assumptions and capture compiler/branch remain separate risks.

Immutable source files (all references above use this commit and their stated line numbers): [histogram256.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/histogram/histogram256.cu), [histogram64.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/histogram/histogram64.cu), [histogram_common.h](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/histogram/histogram_common.h), [histogram_gold.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/histogram/histogram_gold.cpp), [main.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/histogram/main.cpp).
