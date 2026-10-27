# lavamd - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

Short-range molecular interaction surrogate over cubic boxes and100 particles per box. Each home particle accumulates forces/energy from100 particles in itself and each neighboring box (up to26). `main.c:171-221` builds neighbor lists with no periodic wrap; boundary boxes have fewer. Coordinates/charges are CPU rand() values seeded by time (`:228-251`), alpha0.5. In device arithmetic, r2=rA.v+rB.v-dot(rA.xyz,rB.xyz), vij=exp(-2alpha^2*r2), force contributions scale differences and neighbor charge (`kernel_gpu_cuda.cu:166-181`). FOUR_VECTOR is4 doubles=32B, not float4.

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lavaMD), suite Rodinia 3.1. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/lavaMD` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/3.1/cuda/lavaMD/` at this fixed commit. Historical capture-to-source/executable binding is separate.

`main.h:5-19` sets fp=double,100 particles/box and default128threads, optionally overridden by RD_WG_SIZE. `makefile:19,52-63` NVCC compiles wrapper at-O3 with GENCODE targets supplied through common configuration; host gcc-O3. OUTPUT is optional. Trace128threads and binary70 match available recipe; architecture flags/env/ELF identity unbound.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [main.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lavaMD/main.c) | `b79bc582bd34288443685926fa116a43c926ffaf` | `9a3f73ab16fc40d8a27e926096cbb73013f570b01f1f5fc7b9cc6802185a12a7` |
| [main.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lavaMD/main.h) | `42def86ed1651049b1f2974c1f968d28758d62ff` | `1242c89965144f3e1a9597731209f961840de659082e9c75376d2f72d6ad5ec1` |
| [kernel/kernel_gpu_cuda_wrapper.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lavaMD/kernel/kernel_gpu_cuda_wrapper.cu) | `6feab499fe03dc3255cb3330da3ee00f605b5aa6` | `e30ad2fa7624cb7adfd8ad9a41b6e71a7ef2069395851db817c21e3b53c62cdb` |
| [kernel/kernel_gpu_cuda.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lavaMD/kernel/kernel_gpu_cuda.cu) | `42028f2cf19e05e07b117898f61d78c751781ca0` | `4ef60591c16b61b60b1ca5ce10e8e3f31210172c05f0dc12605384d7c83347df` |
| [makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lavaMD/makefile) | `a93489169bb214034db6249762ee538e6d887e30` | `5ef9d6a29d0a708e3a490cbc8d11d8bf5c92b503a843ad61798201366df8632c` |

## 3. Host calls and kernel order

Host parses-boxes1d10 ->1000 boxes/100000particles, builds box offsets and random arrays, zeros force, wrapper allocates/copies box,r,q,f, launches **one** kernel with1000CTAsx128threads, synchronizes, copies f back and frees (`wrapper.cu:84-87,145-207`). There is no time-step loop in this program. Optional output emits result.txt; no native reference checker invoked by default.

## 4. Detailed kernel implementation

CTA bx owns home box. All lanes read home box offset; first100 lanes stage home FOUR_VECTOR into shared rA[100]; barrier. For k=0..nn: k0self else neighbor index, load neighbor box offset, first100 lanes stage rB[100],qB[100]; barrier; first100 lanes each process their home particle against j0..99 shared neighbors and update its own fA fields; barrier before overwriting neighbor shared arrays (`kernel:72-194`). Each lane uses wtx+=NUMBER_THREADS loops, so nondefault block sizes can assign multiple particles/thread. Default128 leaves28 lanes inactive in particle work but reaching barriers. No atomic: different home CTAs write disjoint f ranges; each directed interaction may be evaluated independently by the opposite home box.

## 5. Thread and address formulas

Home particle global index h=100bx+t for t<100; neighbor index n=100*neighborBox+t. Field c (0..3) vector address=`Br+32*h+8c` and force `Bf+32*h+8c`; lane stride32B. For one scalar field of32active lanes,32 distinct32B sectors and8 aligned128B lines are touched (256B useful versus1024B sector footprint); combined four fields cover contiguous1024B so subsequent field loads may reuse sectors. Do not assert scalar code lowers to a vector instruction without SASS. Charge address=`Bq+8*n`, lane+8B =>2alignedlines/8sectors. Home/neighbor box starts100*32=3200B=25lines, well aligned if base aligned; charge box stride800B can shift128B alignment.

Shared neighbor at fixed j is same-address across home lanes for each field; j->j+1 moves32B (charge8B). rA_shared[t] varies by32B across lanes and is reused for100*neighborCount pair evaluations. fA source updates have same global address for each lane across j and k; compiler may retain accumulators, so source `+=` count is not a global-memory instruction count. Metadata address=`Bbox+bx*sizeof(box_str)+offsetof(field)`; same-address per CTA, next-neighbor metadata index is indirect. Different CTAs with overlapping spatial neighborhoods load the same r/q neighbor boxes, but write disjoint f. Default each home lane performs100*(1+nn) interactions; no lane-to-lane data dependence.

## 6. Dataflow, locality, coalescing and concurrency

Interior boxes26neighbors, surface smaller;1000CTAs offer abundant grid work but variable CTA lengths. Home inputs staged once, neighbor inputs staged each k and reused100times; barriers and neighbor loop serialize stages within CTA. Repeated home-force accumulation is per-thread dependence, not atomic contention. Independent global metadata and coordinate/charge accesses become dependent through neighbor pointers. Actual SM placement and simultaneity of overlapping neighborhoods are unobserved. Coordinate AoS field-sector inefficiency and shared broadcast should be distinguished.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-22`: `IDENTITY_FROZEN`; parameters `["_boxes1d_10"]`.
- Selected input digest `ddb6806316876a85cdea5766f2e1fc88bf9d4b699066a522eb5a5b9ff17a10d8` is the registered identity, not automatically original-file SHA.
- Bundle `52ba77f34965dda4a6e2e7b972949135001f1c9ebd4f32ad5c0e18749298ac56`.
- Trace entry `/root/workspace/assets/traces/bundles/52ba77f34965dda4a6e2e7b972949135001f1c9ebd4f32ad5c0e18749298ac56/tree/kernelslist.g`.
- Existing scope `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: Only ordinary trace identity for this program in the72-input matrix; no outcome-dependent replacement. Keep its recorded source/command/content identity. Exact capture-time executable/input-content and full-application provenance are not newly certified.

Header inventory: 1 kernel entries, 5 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z15kernel_gpu_cuda7par_str7dim_strP7box_strP11FOUR_VECTORPdS4_` | `(1000,1,1)` | `(128,1,1)` | 1 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

SOURCE_VERIFIED:FP64 vectors,32B AoS record;1000CTAs/128threads/one launch;100particles/home; bounded-neighbor gather; shared all-pairs reuse; disjoint stores and no global atomics; time-based random realized input. This differs from a generic MD multi-time-step application.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1: neighbor boxes shared by several home CTAs might require physical-line retention and searchable tags while staged input diminishes subsequent global requests; test pending overlaps separately from cached spatial reuse. EP-L2: AoS scalar-field sectors and repeated neighbor reads/force writes can alter tag/data demand and buffering. Runtime evidence must resolve whether compiler accumulation, cache hits and scheduling suppress these opportunities; no source-derived queue occupancy or speedup.

## 10. Evidence and limits

Frozen-box count binds dimensions but random seed/coordinates/charge bytes and capture ELF are not certified. Struct ABI offsets require actual target binary before exact metadata byte footprint; formula retains sizeof/offsetof rather than inventing padding. Existing one-launch registration is compatible with host flow; output numerical correctness and full-body scope are not newly established. No execution occurred.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
