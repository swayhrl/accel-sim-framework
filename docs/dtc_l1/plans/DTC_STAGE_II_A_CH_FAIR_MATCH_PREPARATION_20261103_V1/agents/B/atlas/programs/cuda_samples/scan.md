# scan - source and behavior audit

## 1. Program and algorithm

Exclusive prefix scan for batches of arrays: O[a,j]=sum(k<j) I[a,k],32-bitunsigned arithmetic. Testdriver sweeps power-of-two array lengths. Short arrays fit aCTA's1024elements; large arrays first scan1024chunks,scan their chunk totals,then uniformly add per-chunk offsets. CPU computes eachbatched reference after GPUphase.

## 2. Source authority and build

Reviewed immutable candidate accel-sim/gpu-app-collection@b059fdae25c2aabf737486aada743fca114469ce under src/cuda/sdk/4.2/. The freeze records cudasdk/9.1 capture paths, not newly certified source ancestry. [Source manifest](../../contributions/cuda_samples/source_evidence/manifest.json) provides file SHA-256 and Git blob IDs. Makefiles list CU/CC files and include ../../common/common.mk; capture-time nvcc flags, architecture macros and ELF SHA are not bound. Header binary version70 is metadata, not a build recipe. SOURCE_VERIFIED refers to this candidate only. THREADBLOCK_SIZE256 in scan.cu:19 is authoritative; comment:17 saying512threads is stale. #if(0) naive fullCTA scan(:24-48) is disabled; active branch(:49-103) uses warpScanInclusive volatile shared and interwarpbarriers. Capture compile/warp execution assumptions require separate binding.

## 3. Host control and launch order

main.cpp:34 freezes candidate N26624=13*(1048576/2)/256,while frozenHtoD/grid proveN6815744=13*1048576/2,256xlarger. iCycles1(:56); lengths4,8,...1024 callscanExclusiveShort once each(9launches). Lengths2048,4096,...262144 each calllarge:scanExclusiveShared,scanExclusiveShared2,uniformUpdate(8triples=24). Thus trace33launches follows full9+8stage recipe at recorded N,but candidate host N differs. Driver copiesandvalidates between shapes; no convergence or input-dependent earlyGPUexit.

## 4. Distinct kernels

scanExclusiveShared(:136-153): loaduint4/thread,locally scan4registervalues,scan last component across threads using activewarp/shared codelets,subtractinput for exclusive result,storeuint4. scanExclusiveShared2(:156-181): each thread reads last inclusive totalof one1024chunk asDst[last]+Src[last],exclusive-scans chunk totals per originalarray,storesbufferwithpos<N predicate. uniformUpdate(:185-201): thread0loads onechunk offsetintosingle sharedword,barrier,all threadsread/modify/write theiruint4. Unique3kernels; repeatedshortlaunches differ scan size,not kerneldefinition.

## 5. Thread and address formulas

Let T256,p=256*b+t. Firstpassvectoraddress Src/Dst+16*p; atgivencomponentc address+4c; contiguousuint4/thread. Activewarpcodeletpos=2*t-(t&(size-1)),thenpos+=size; shared scan readspos-offset whileoffset doubles. Large second passscalaraddress Src/Dst+4*(1023+1024*p),buffer B+4*p,validp<batchSize*arrayLength/1024; lane stride4096B. Uniform vectoraddress D+16*p; offset B+4*b is loadedonly thread0 then sharedbroadcast. Same-thread no global input loop; loops inprefixcodelets operate shared/registerdata.

## 6. Dataflow, coalescing, locality and concurrency

Atrecorded N6815744first grid 6656/block256,second grid26/block256,uniform grid 6656. Alignedvectorwarp512B=4lines/16sectors if16Bvectorinstruction; scalarcomponentissuewouldtouch16sectors but only128usefulbytes percomponent,so compilerbinding matters. Secondpassfull warp reads32distinctlines/sectors per Src/Dst instruction due4096B stride:128usefulB/1024sectorB (8x). Neighborchunk totals are not adjacentwords; bufferstores are contiguous. Uniformfirstthread load sparse acrossCTAs may sharebuffersectors. Firstpass->totals->uniform is strictdependencychain; small26CTA middlephase,barriers and volatilewarp scan serializeparts. N6815744divides everytestedarraylength,so no remainderbatch atthisN.

## 7. Frozen input and trace binding

Selected6df3a84b612086e8c10f7f66978b6b995b459a38b00892152cf116e90db72e39,NO_ARGS,bundle9dafd3ce... . HtoD27262976B;33launches,headerfirst9short then8triples,first grid 6656,second26,uniform6656;shared2048/2048/4,nregs19/16/12. Source recipe explains sequencebutcandidate host N mismatchprevents exacthostbinding. Fullapplication correctness notcertified fromtracecompletion.

## 8. Source-proven architectural features

Three dependentkernels,vectorizedglobalstreaming,shared/registerscan,high-stridechunk-total gather,scalar offset broadcast and repeatedsize-sweep. The secondaryphase accesspattern differs fundamentallyfromfirst phase; one overalllabelwouldlose this distinction.

## 9. DTC-L1 and EP-L2 hypotheses

DTC-L1: stridedtotalsgather raises searchabletag/sectorcoverage demand,whileuniform'schunk-offsetloads maysharependinglines acrossCTAs; intraCTA shared scan waitingdoesnot itself implyL1PIBpressure. EP-L2: Dstwrite/readat1024boundaries,bufferproduce/consumeanduniformread-modify-write mayaffecttag/data/writequeues. Testwithper-phasecounterandrequestlifetime evidence; do notuse source-repeated reads as measuredcachehits.

## 10. Evidence and limitations

Fixed scan/main.cpp:34-35,56-65,104-112; scan.cu:19,24-103,105-201,240-310. SOURCE_VERIFIED=candidate; INPUT_BOUND=yes(recorded N)/candidate Ncontradiction; BINARY_BOUND=no; TRACE_SCOPE_BOUND=33-launch recipe consistent, exactdriverunresolved; RUNTIME_MEASURED=no new measurements. No added execution was used to resolve the mismatch.

Immutable source files (all references above use this commit and their stated line numbers): [main.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/scan/main.cpp), [scan.cu](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/scan/scan.cu), [scan_common.h](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/scan/scan_common.h), [scan_gold.cpp](https://github.com/accel-sim/gpu-app-collection/blob/b059fdae25c2aabf737486aada743fca114469ce/src/cuda/sdk/4.2/scan/scan_gold.cpp).
