# heartwall - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

Tracks endocardial/epicardial landmark motion in AVI frames using normalized cross-correlation of51x51 templates against81x81 search windows; later frames use convolution, integral sums/squares, a motion mask and maxima. Initial landmarks are hardcoded; CPU AVI decoding and outputs/bytewise goldfile comparison surround GPU processing (`main.cu:75-113,120-268,577-651`). Crucial selected-path boundary: command processes **one frame**, frame_no starts0. This only initializes templates/point outputs; the actual tracking/convolution branch requires frame_no!=0 (`kernel.cu:83-145`). A source-consistent one-frame capture is not an execution of the full tracking algorithm across time.

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/2.0-ft/heartwall), suite Rodinia 2.0-ft. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/2.0-ft/heartwall` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/2.0-ft/heartwall/` at this fixed commit. Historical capture-to-source/executable binding is separate.

Selected authority is **Rodinia2.0-ft**, `src/cuda/rodinia/2.0-ft/heartwall`, not similarly named3.1. `Makefile:37-52` builds heartwall-rodinia-2.0-ft from main.cu,AVI sources/define.c through ../../../common/common.mk; main includes kernel.cu. define.c7-13 fixes float,512threads,20endo+31epi=51points. Common build environment/target flags and capture ELF are not newly bound. Trace binary version70 and kernel(void) agree with this constant-parameter source form.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/2.0-ft/heartwall/main.cu) | `111c47f2a39e2de67cd9ef532b37da7d4e133e2a` | `0ae408b0619c83d199bd7ba14fcd688479684e42fb69a3d9b3d78c3f297cc152` |
| [kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/2.0-ft/heartwall/kernel.cu) | `df550a62daa49b956316507e4f2fb7cb81c62e9f` | `5ef164410a6ccbcb473f09a6068b046f05338e84de46ee78d442acd9b97cab5a` |
| [define.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/2.0-ft/heartwall/define.c) | `44b9e1f0c51073ecc05d7226e8e26d61d2c74b56` | `3777059f44aaf8c1d6a5b60b5565d6f442962ebe91289d24eafef7c681caa3e3` |
| [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/2.0-ft/heartwall/Makefile) | `75b4a0c79ccb631b626b5e97b00070b8d6f6b392` | `c17a8db4f375cac761ec2ef5293a3c78410719f0c929b9c0cc89dccabffe9568` |

## 3. Host calls and kernel order

Host reads AVI dimensions/count, allocates per-point scratch/template and location arrays, fills hardcoded landmarks and common sizes. Copies common/unique structs to device constant symbols (`main.cu:563-564`). For frame_no0..frames_processed-1: decode frame, copy FP32frame, copy common_change constant struct, launch kernel<<<51,512>>> (`:577-591`). After loop copy location arrays back and write/compare result. Selectedframes_processed1 yields exactlyone launch. There is no separate convolution/prefix/max kernel: those are phases inside the same unique global kernel for later frames.

## 4. Detailed kernel implementation

One CTA/landmark, constant d_unique[bx] points at point-specific arrays and the appropriate endo/epi template slab; d_common has sizes and d_common_change current frame pointer/index (`main.cu:25-32`, `define.c`). Frame0 kernel: lane0 writes initial row/col coordinates, all lanes traverse e=tx+512q<2601 and copy a51x51 frame patch into template (`kernel.cu:90-134`). This branch performs no CTA barrier or normalization/reduction.

For excluded later-frame capability (`:145-1288`): extract81x81search region; rotate template into shared d_in_mod_temp[2601]; direct convolution into131x131global scratch; padded vertical cumulative sums and horizontal cumulative sums/subtractions; square search image and repeat sum pipeline; shared partial template sums/squares, two-lane final sum, normalize convolution; motion mask convolution; per-column maxima then lane0 final maximum/point update. CTA barriers separate phases. Every10thnonzero frame refreshes template alpha0.87 (`:1299-1329`). Shared scratch includes51-entry partials and131-entry maxima (`:52-64`); no atomics or texture. Do not treat allocated scratch sizes or dormant code as selected GPU traffic.

## 5. Thread and address formulas

Frame is column-major: address=`BF+4*(col*H+row)`. Template e uses row=e%51,col=floor(e/51), landmark R,C with origin R-26,C-26, so selected input address=`BF+4*((C-26+floor(e/51))*H+R-26+(e%51))`, template store=`BT+4*(point_no*2601+e)` (`kernel.cu:116-132`). Let e=32w+l+512q. For lanes not crossing a51-row patch boundary, lane delta4B; at crossing50->0, delta4*(H-50), creating a second span. Same thread q->q+1 adds `4*(512+(H-51)*(floor((e+512)/51)-floor(e/51)))`, not simply2048B in input; output loop stride2048B. WithinCTA warps cover adjacent32template elements, with frame discontinuities at patch-column boundaries. At aligned contiguous32-element span ideal1line/4sectors; misalignment can yield2lines/5sectors. Crossing51 produces the union of two spans; count actual floor(address/128) and floor(address/32), rather than call it uniformly coalesced. Template stores may start at4*2601*point offset, so most point subarrays are not128B-aligned.

Landmark CTAs can read overlapping frame patches according to their hardcoded point positions. They write distinct2601-element template intervals and lane0 point/frame index=`point_no*no_frames+frame_no`, 4B element. No common neighboring-lane location stream for the lane0-only stores. For later phases, e=tx+512q uses contiguous scratch stores B+4e; vertical-prefix thread column c uses B+4*(c*rows+i): lane stride4rows, loop stride4. Horizontal-prefix row r uses B+4*(r+rows*i): lane stride4, loop4rows. Convolution global search address=B+4*(81*(jb-1)+ib-1), template shared address=4*(51*(ja-1)+ia-1), inner ia makes ib decrease1, so input thread-loop delta-4B while neighboring output e may follow separate row/column limits. These dormant formulas cannot describe selected frame0 traffic.

## 6. Dataflow, locality, coalescing and concurrency

Selected grid51CTAs, each copy2601float values (five full512-thread iterations plus41threads) plus coordinate metadata. Independent patch reads/stores and possible inter-landmark overlap are the main selected locality/concurrency sources. Long per-CTA convolution and prefix dependence are dormant. General later-frame path has multiple CTA-wide barriers, global scratch reuse and serial prefix loops, but no inter-CTA synchronization because point workspaces are private; only frame data can be shared. Constant metadata uniform within CTA can broadcast; constants are a distinct access path from ordinary L1 data, dependent on binary/model semantics.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-17`: `IDENTITY_FROZEN`; parameters `["__data_test_avi_1___data_result_1_txt"]`.
- Selected input digest `731af5428c4b81552d8750c8edf9eeb609b71bd4f3651ca378a4dd73b194d980` is the registered identity, not automatically original-file SHA.
- Bundle `04119459d74ef9a2afacaaa752a594cea7faec57a92b836cd8243c60cdaf7aed`.
- Trace entry `/root/workspace/assets/traces/bundles/04119459d74ef9a2afacaaa752a594cea7faec57a92b836cd8243c60cdaf7aed/tree/kernelslist.g`.
- Existing scope `SOURCE_CONSISTENT_ONE_FRAME_PROVENANCE_GAP`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: REFERENCE_CAPTURE_PROVENANCE_SELECTED: Both captures carry2.0-ft standard1-frame command. Choose the official archive/capture with SHA-preserved run.sh and known source-alias lineage over1299a96e, which has no retained capture script. Source loop launches one kernel per processed frame; chosen trace contains one full51-CTA grid. Byte/semantic equivalence to alternate capture is NOT asserted. Original video/executable SHA linkage remains provenance gap.

Header inventory: 1 kernel entries, 9 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z6kernelv` | `(51,1,1)` | `(512,1,1)` | 1 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

SOURCE_VERIFIED:2.0-ft parameterless global kernel usesconstant structs;51CTAs512threads; first-frame-only template initialization; FP32column-major frame input and point-private stores; overlapping patches conditional on landmark positions. TRACE_SCOPE_BOUND means one declared frame's geometry is compatible, not multi-frame tracking. No selected convolution, reduction or scratch-stream feature is admitted merely from source presence.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1: selected frame overlap may yield pending-line merging or cache residency across landmarks, conditional on CTA placement/timing. Dormant tracking features must not justify selected workload speedup. EP-L2: frame-read sharing, patch-column discontinuities and template-store alignment may create sector/tag/data differences; constant loads are separately modeled. Measure outstanding lifetime and exact request coalescing using existing bound evidence before claiming retention/queue advantages.

## 10. Evidence and limits

Freeze chooses official1-frame archive/capture with retained run.sh lineage over alternative capture, while original video/goldfile/ELF SHA linkage remains uncertified. Full grid/header is not body-level or numerical validation. The main tracking capability is described for source completeness but explicitly excluded from selected execution. No version3.1 substitution or new run was made.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
