# dwt2d - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

Three-channel two-dimensional integer5/3 lifting transform. CPU reads exactly width*height*components raw bytes with `open/read` (`main.cu:52-67,359-365`); **no BMP header parser** is used even though the file is named192.bmp. Channels become centered integers r-128,g-128,b-128 (`components.cu:48-52`). Each level performs vertical then horizontal predict/update and packs LL,HL,LH,HH; recurse only on LL. Predict c-=(p+n)/2 and update c+=(p+n+2)/4 use C++ integer division (`fdwt53.cu:81-93`), so do not replace with an abstract floating wavelet. The active depth is3 on each channel.

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d), suite Rodinia 3.1. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/dwt2d` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/3.1/cuda/dwt2d/` at this fixed commit. Historical capture-to-source/executable binding is separate.

`Makefile:17` links forward/reverse 5/3 and9/7 implementations. Selected `-f -5` chooses int5/3 (`main.cu:260-271,368-378`), not float9/7. Release uses `-O2`, host strict-aliasing disabled, `OUTPUT=-DOUTPUT` (`Makefile:59-83,101-108`); GENCODE from common config includes70/75 and is overridable. `GPU_DWT_TESTING` would wrap operations in31-iteration testing loops (`dwt_cuda/common.h:49-65,181-182`), but default Makefile's definition is commented75-77 and selected10-launch trace has no such repeated group. Exact capture compiler/env/ELF still absent.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/main.cu) | `4f9bd5280561f1342f0d9ff021280fddd22c0a66` | `7c8278f352ca43f992ca9da380011fe82a831d93a0e6a7e4e2e6ddf4fdf56ed6` |
| [components.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/components.cu) | `b9721ce03e750b0652292f2fa8f24f631088eeb8` | `fd481745f1c5078a23b71a99791beeafb1264491d705d5a9ded6c7c907658a15` |
| [dwt.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/dwt.cu) | `a684589f2df23f584bdc18c45e229909acba6291` | `9916aa020cf15c31ead61d7f6498c504d4d435391acbea03fbd57b64d6a93158` |
| [dwt_cuda/fdwt53.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/dwt_cuda/fdwt53.cu) | `32acd22f65c8a9f97a0e86c0bda43c926050537f` | `34456c3db48753a9bafa9d318f337e2f09915e9e7833922fdf85bc958eec473b` |
| [dwt_cuda/io.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/dwt_cuda/io.h) | `f0eb59eb4824ebfb989cdaaa24990d8955db2312` | `e19de17e7480dacfe27b71f832601be46e76de946cdb0098ffcf0d81c4f676ac` |
| [dwt_cuda/transform_buffer.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/dwt_cuda/transform_buffer.h) | `e566089163474b1d20cdb2ea0520dee8de19a7a4` | `ff98a90ea28fbfe6a4ebcb7163eb20488aa337c4424c5e7daf9e6f048dfbd5dc` |
| [dwt_cuda/common.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/dwt_cuda/common.h) | `273d824767658b72c0bd5269aeac4fff00fe06ba` | `1dc992307fd69203888d3fb478bc139a4c5383ca810f569e39e1e54e967f83fe` |
| [dwt_cuda/common.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/dwt_cuda/common.cu) | `8ce4984fac65d156a9eb2176f7532e9ba3b1de52` | `71e0d900449fd7de8eaf5f045c5773a0cabbbbb48e1cd9750986ef7b10ddbed1` |
| [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/dwt2d/Makefile) | `1ffd3c77588cd08134444c758f3de96b899a5baf` | `048ad7d5c759d009e8898e19f1e4436162ffdd36d74198f8871d29d8e9c9ae9b` |

## 3. Host calls and kernel order

Host allocates per-channel input/output and a reusable backup, splits RGB once (`main.cu:101-138`). Then R3levels -> G3levels -> B3levels. `nStage2dDWT` first D2D-copies the whole channel to backup (`dwt.cu:75-89`); that backup is not the actual recursion input. `fdwt53:369-389` launches current level, copies the contiguous LL prefix output->input using `memCopy`, and recursively halves dimensions by ceil. Selected dimensions192->96->48: each chooses<64,8>. Exactly1 component kernel +3*3 transform launches=10. Optional CPU output conversion/writes follow under OUTPUT; one-channel,9/7 and reverse routes are alternative branches and not part of this selected trace. Device2D kernels in those other files must not be added to the active count.

## 4. Detailed kernel implementation

Component kernel `components.cu:69-99` uses256 threads/CTA,768 shared bytes, first192 threads load4 bytes each as float bitwise storage, barrier, all256 threads unpack RGB and write one element to each int plane. Grid ceil(192*192/256)=144.

`fdwt53Kernel:318-324` is one templated definition; run declares shared FDWT53 object and selects checked load/write behavior for bottom/right edges (`:274-301`). Launcher steps=ceil(sy/(15*8)), grid=(ceil(sx/64),ceil(sy/(8*steps))) (`:336-353`). Active grids are(3,12),(2,12),(1,6), block64. Each thread owns one column; first3 also load left/right halo columns (`:194-205`). Three carried rows plus8 new rows form shared transform buffer, vertical lifting uses per-column register/shared values; barrier, horizontal odd predict, barrier, even update, barrier; outputs alternate low/high rows; barrier before next sliding window (`:149-173,224-259`). At192,steps2;96/48,steps1. Boundary pixels mirror, not zero-pad (`io.h:49-79,183-212`). No atomic or texture access in active kernels.

## 5. Thread and address formulas

Component load byte address=`Bsrc+3*(256b)+4t` for t<192: lane+4B,6 full coalesced warps cover768B (6 aligned128B lines/24 sectors). Output to each plane=`Bc+4*(256b+t)`: lane+4B, each full warp1line/4sectors,8warps/CTA. Shared unpack reads bytes3t+c; no global3-byte scalar stride.

Transform input for ordinary column is `Bin+4*(mirror(64bx+t,sx)+sx*y)` (`fdwt53.cu:117-137`, `io.h:100-105,183-212`): interior lane+4B, same thread successive vertical load+4sx (768,384,192B across the three levels); mirror changes sign at boundary. Two warps/CTA load adjacent32-column segments; neighboring CTAs overlap three halo columns and vertical carry neighborhoods. Horizontal lifting itself is shared, not global. Buffer has VERTICAL_STRIDE=2+64/2=34; SIZE_Y=11; arch>=200 bank count32, BUFFER_SIZE374, padding26, ODD_OFFSET400, total774ints=3096B (`transform_buffer.h:55-80,132-135`). Column shared offset=`(t+2)/2+((t+2)&1)*400`, row adds34.

Output column permutation p(t)=2t-63*floor(t/32) (`common.h:125-127`): warp0 writes even source columns, warp1 odd. For even dimensions, define x=64bx+p(t), y=firstY+8w+q (firstY=by*8*steps, q=0..7); the packed offset is `x//2 + (x%2)*(sx/2)*(sy/2) + (y//2)*(sx/2) + (y%2)*(sx*sy/2)`. More generally use `io.h:245-287` for odd sizes. The shared r index2..9 corresponds q=r-2. Within either warp at fixed q, p delta2 means packed address delta4B. Thus packed stores are contiguous,1line/4sectors if aligned, despite parity separation. Thread's alternating low/high stores jump by the band stride; consecutive same-parity rows move sx/2 words. Level48's row stride24words=96B causes changing128B alignment; a full valid span may cross a line. Counts are conditional on actual alignment/active edge lanes, not blanket one-line assertions.

## 6. Dataflow, locality, coalescing and concurrency

Lifting converts repeated neighborhood references to shared reuse. Independent column loads precede vertical arithmetic, then barriers enforce horizontal dependencies. Adjacent CTAs may reread halo pixels; no inter-CTA shared storage exists. Channel allocations are independent but host launches channels sequentially; LL recursion consumes previous output and explicit D2D copies separate levels. Grid CTAs36,24,6 shrink with level, so late stages have little grid parallelism. The whole192-plane147456B and LL prefix36864B then9216B suggest residency opportunities without proving cache hits. Input source RGB bytes110592B; same source frame is split once, not reread independently per wavelet stage.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-12`: `IDENTITY_FROZEN`; parameters `["__data_192_bmp__d_192x192__f__5__l_3"]`.
- Selected input digest `e5638b94095098acf5186be97210cb371bb3f88dcc8ceefb7609b454ef5ce008` is the registered identity, not automatically original-file SHA.
- Bundle `52b17d988c23c61c0ad4756fa4a26cc9b77748cf646f3a0125ce3f0f3c4d06c6`.
- Trace entry `/root/workspace/assets/traces/bundles/52b17d988c23c61c0ad4756fa4a26cc9b77748cf646f3a0125ce3f0f3c4d06c6/tree/kernelslist.g`.
- Existing scope `SOURCE_CONSISTENT_3_CHANNEL_3_LEVEL`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: PRIOR_REFERENCE_SELECTED: Historical E1 source/input inventory nominates Rodinia3.1 192.bmp -d192x192 -f -5 -l3 (input reference595e63cc...). Trace copies110592=192*192*3 bytes, component split plus3channels*3levels=10 kernels. 1024 variant has unconfirmed source version and different kernel specializations; not treated as duplicate.

Header inventory: 10 kernel entries, 11 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z21c_CopySrcToComponentsIiEvPT_S1_S1_Phi` | `(144,1,1)` | `(256,1,1)` | 1 |
| `_ZN8dwt_cuda12fdwt53KernelILi64ELi8EEEvPKiPiiii` | `(3,12,1)` | `(64,1,1)` | 3 |
| `_ZN8dwt_cuda12fdwt53KernelILi64ELi8EEEvPKiPiiii` | `(2,12,1)` | `(64,1,1)` | 3 |
| `_ZN8dwt_cuda12fdwt53KernelILi64ELi8EEEvPKiPiiii` | `(1,6,1)` | `(64,1,1)` | 3 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

Verified active facts: int5/3,3channels/3levels; two unique active specializations;10 launches; padded RGB staging; column-contiguous global loads, halo/mirror handling, shared lifting and packed-contiguous per-warp subband stores. Reverse/9/7 and1024-image alternative traces are separate identities. No GPU atomic/texture path in this active recipe.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1: halo rereads across CTAs may create overlapping pending-line requests, while shared lifting reduces the number of global requests; per-level tag footprint and late-grid starvation should be separated. Physical-line retention and PIB waiter timing require existing valid runtime evidence. EP-L2: LL copies, packed subband writes and next-level LL reads create stage-dependent read/write residency and buffering opportunities; sector efficiency can differ by48-wide boundary alignment. Do not infer MSHR merging, reuse distance or DRAM request counts from the static halo overlap.

## 10. Evidence and limits

Canonical E1 source records input192.bmp SHA256595e63ccd303dcc3387d0fea97d96be524a6f32f5e7593ab09a2704c7571207e, but freeze explicitly does not newly certify capture-time original-input/ELF linkage. Byte-reader semantics must be retained in all cross-project mappings. Header grids and ten launches are source-consistent; they do not independently prove output correctness or every CTA body was retained. The formulas were checked directly against loader/writer/permutation code; no native/capture/simulator run occurred.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
