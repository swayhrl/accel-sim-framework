# particlefilter_float - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

Particle filtering of a CPU-generated noisy moving disk. Unlike naive, GPU computes random motion, per-particle likelihood, weight reduction/normalization, CDF and resampling. It uses frame-interleaved unsigned-byte video rather than naive int video (`ex_particle_CUDA_float_seq.cu:420-595,633-701`). Likelihood is the same mathematical contrast sum divided by countOnes, but byte wrapping/noise, RNG execution and the implementation's synchronization must be treated independently.

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/particlefilter), suite Rodinia 3.1. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/particlefilter` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/3.1/cuda/particlefilter/` at this fixed commit. Historical capture-to-source/executable binding is separate.

`Makefile:14-15`: NVCC `-g -lm -O3 -use_fast_math`, overridable multi-architecture GENCODE; thread count512 is `ex_particle_CUDA_float_seq.cu:14`. The implementation's positions, weights, likelihood and CDF are **double**, video is `unsigned char`, offsets/indices/seed int. Name `float` does not authorize FP32 assumptions. Trace binary version70 is target metadata, not an ELF hash.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [ex_particle_CUDA_float_seq.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/particlefilter/ex_particle_CUDA_float_seq.cu) | `b37cbcc14b69ed5f380bc712020adb85a6f638b6` | `13cfa4496bbfec6b76e47b81c750b4bf8a15376165704c8cc986feca06ad4917` |
| [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/particlefilter/Makefile) | `c7cccf04b4bb74797f96d3a2eef9b1981528231f` | `3c97a48b2c0b551f60ac45491da2b121cdfce34172152355c1b05ca528618f11` |

## 3. Host calls and kernel order

CPU allocates state and countOnes*P index array, initializes xj/yj to center, copies I,offsets,weights,xj,yj,seed once (`:686-726`). For k=1..F-1, launches exactly **likelihood_kernel -> sum_kernel -> normalize_weights_kernel -> find_index_kernel**, each grid ceil(P/512) (`:729-737`). Default-stream kernel order separates phases. Final sync, D2H X/Y/weights and CPU location estimate follow (`:741-779`). Selected P1000,F10 gives36 launches across four definitions; no helper is an extra launch. `findIndexBin` exists but launched resampling uses a linear loop.

## 4. Detailed kernel implementation

`likelihood_kernel:332-395`: one thread/particle, writes X=xj,Y=yj, resets weight1/P, advances seed with Box-Muller motion, creates all disk indices, loads video through those indices, computes likelihood/exp, fills shared double buffer[512] with zero for inactive lanes, performs binary-tree reduction with CTA barriers, and lane0 writes partial_sums[CTA]. `sum_kernel:299-312` launches2CTAs yet only global i0 sums the ceil(P/512)=2 entries and overwrites partial_sums0. `normalize_weights_kernel:266-297` stages total and u1 in shared doubles, divides weights, i0 serially constructs CDF and generates u0, then all active threads fill thresholds. `find_index_kernel:238-264` scans CDF linearly and gathers positions; all threads reach its final CTA barrier. No atomics. Shared barriers are CTA-local.

**Source correctness audit, not a measurement:** normalize's barrier at280 does not order another CTA's writes before i0 reads all weights at283. Likewise u0 is written only by global i0 at284, but other CTA's lane0 may read u0 at290 without a grid barrier. P1000 yields2CTAs, so the apparent global dependence is real in this source. Record this risk; do not silently fix the source or reclassify historical accepted results.

## 5. Thread and address formulas

For i=512b+t, state `double[i]` addresses B+8i (lane+8B), seed Bseed+4i (lane+4B), shared buffer Bsh+8t. `countOnes=C=69` follows integer disk points dx,dy=-4..4 with dx^2+dy^2<25. Index matrix address is `Bind+4*(69*i+y)` (`:353-360`): lane delta276B at fixed y; thread y-loop delta4B. A full warp at fixed y touches32 distinct128B lines and32 distinct32B sectors (4B scalar aligned), even though each thread's complete69-int slice is contiguous across its own loop. Warp spacing in a CTA is8832B for this matrix, CTA spacing141312B. This is a specific lane/loop transposition, not a generic random index-store pattern.

Video load address is `BI + ind[69*i+y]`, where index=`abs(round(Xi)*Y*F+round(Yi)*F+k)` with disk offsets and out-of-range replacement0; data dependent across lanes. Fixed particle, neighboring disk y coordinates move by F=10 bytes (x coordinates by YF=1280B); byte sample sectors depend on actual positions. Uniform offsets `objxy[2y],objxy[2y+1]` are same-address across active lanes, next y delta8B. All double vector streams produce2 aligned128B lines/8 sectors per full warp; FP32 int streams1line/4sectors. CDF scan and coordinate gathers follow naive's formulas (double CDF same x across surviving lanes, 8B iteration delta). Serial CDF construction loads weights[x] and CDF[x-1], writes CDF[x] (8B increments), imposing prefix dependence. Sum phase has only one active lane reading partial_sums[x] sequentially. Alignment-independent counts use the union of byte-covered sector/line indices; exact runtime traffic is not derived.

## 6. Dataflow, locality, coalescing and concurrency

Motion/likelihood may expose independent vector/offset/index/video loads, but video depends on computed coordinates and ind loads; exponentials and per-thread loops precede tree reduction. GPU image/ind traffic is absent from naive. Only2CTAs per phase and a single active global reduction/CDF thread limit concurrency. The shared reduction reuses data within CTA; partial sums, normalized weights and CDF flow across kernels. Four phases repeat9 times using resident allocations, but cache survival is not guaranteed. Inter-CTA normalization race prevents assuming a unique source-defined numerical schedule.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-30`: `IDENTITY_FROZEN`; parameters `["_x_128__y_128__z_10__np_1000"]`.
- Selected input digest `b41cc74c66ca6ed4975948bdce35825381473e5cf44c53f9dc9740ac3e0115b4` is the registered identity, not automatically original-file SHA.
- Bundle `b648c06ef33fcf9e6f0c223c066910c21193da27cf04821dc344f4a65d145bde`.
- Trace entry `/root/workspace/assets/traces/bundles/b648c06ef33fcf9e6f0c223c066910c21193da27cf04821dc344f4a65d145bde/tree/kernelslist.g`.
- Existing scope `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: Only ordinary trace identity for this program in the72-input matrix; no outcome-dependent replacement. Keep its recorded source/command/content identity. Exact capture-time executable/input-content and full-application provenance are not newly certified.

Header inventory: 36 kernel entries, 42 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z17likelihood_kernelPdS_S_S_S_PiS0_S_PhS_S_iiiiiiS0_S_` | `(2,1,1)` | `(512,1,1)` | 9 |
| `_Z10sum_kernelPdi` | `(2,1,1)` | `(512,1,1)` | 9 |
| `_Z24normalize_weights_kernelPdiS_S_S_Pi` | `(2,1,1)` | `(512,1,1)` | 9 |
| `_Z17find_index_kernelPdS_S_S_S_S_S_i` | `(2,1,1)` | `(512,1,1)` | 9 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

SOURCE_VERIFIED: four unique global definitions,36 source-consistent trace launches; FP64 states; byte-video gather; 69-wide AoS index slabs with276B fixed-loop lane stride; shared512-element reduction; serial global sum and CDF; CTA-only barriers. Structural race at P>512 is a code fact about missing grid ordering, not proof a particular captured result is wrong. No measured pending occupancy/latency is claimed.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1: compare streaming sparse-sector ind stores against high sharing in offsets/CDF and irregular video loads; image dependency and serial prefix may dominate even with more tags/PIB. EP-L2: phase-specific write/read residency for ind,weights,CDF and line footprint can change downstream traffic and buffering needs. Treat texture/atomic mechanisms as absent here. Any request amplification, merge latency, hash conflict or speedup needs identity-bound timing evidence; correctness risk must be considered separately.

## 10. Evidence and limits

Runtime RNG seed, realized byte video and intermediate arrays are not input-content bound. `-use_fast_math`, device math and the normalization ordering issue preclude declaring float and naive numerically equivalent from dimensions. Read all selected CUDA bodies and host flow; inactive binary-search/device utility definitions do not affect the selected launch inventory. No experiment was started.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
