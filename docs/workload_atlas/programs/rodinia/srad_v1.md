# srad_v1 - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

Speckle-reducing anisotropic diffusion. CPU reads502x458 image.pgm, resizes to requested Nr,Nc, builds clamped neighbor-index arrays. GPU extract maps I->exp(I/255). Every iteration computes sumI/sumI?; CPU derives q0?=variance/mean?; GPU srad computes N/S/W/E differences, local gradient/Laplacian and clamped coefficient c; srad2 updates I+=lambda*divergence/4. Final compress maps log(I)*255, CPU writes image_out.pgm (`main.cu:162-228,359-444`). Frozen100,0.5,502,458 gives Ne229916.

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1), suite Rodinia 3.1. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/srad/srad_v1` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/3.1/cuda/srad/srad_v1/` at this fixed commit. Historical capture-to-source/executable binding is separate.

Authority is `srad_v1`, not sibling v2 or v1_k1. define.c7-9 fixes FP32 and512 threads; makefile1-34 uses NVCC -O3 and common GENCODE flags. Main includes all six kernel files. Binary70 metadata agrees with an available target; actual compiler environment, ELF and original-image/capture linkage remain unresolved.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/main.cu) | `778b6f75bd38c19a900eaaeb338442673d18c09c` | `7b9dd42ed57d554b34ce281eb1db5fddfec63ff9679c2c6e0f029d8d69f8c3e2` |
| [define.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/define.c) | `7e2dd77b89f5b095a41874d4e0ecef60b49f838e` | `0ee5faefa693c924fe65b36d595528c6afb280d54744952ef978a5cab1bb7b6b` |
| [extract_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/extract_kernel.cu) | `4d97122d351f87d48a3752f724349c92f98dd076` | `94dc1329742b5b192001e83ef261e1f5ec811d05c3d1c5360d406c327800c23a` |
| [prepare_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/prepare_kernel.cu) | `d6c84ce1d33e304a443a0d1874de7186b4902002` | `861337a2101ad23a8df6207d9d0d763d6f4bb0d0062c1342c8a9cf5a1cebad13` |
| [reduce_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/reduce_kernel.cu) | `864cd397503c04ba5ec02a9c9c5aa5f75baac52b` | `48dc76746fc5f83b030e88df3848cdb57059101a081d2d7deef43c9fff6c0634` |
| [srad_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/srad_kernel.cu) | `3f7cb59faeac1dc137cbc1d8e94eca3e4ba536ec` | `5739dfdc4cfcbed2bbf702757b01eebb2bc50b96d741d33a766344703c53897d` |
| [srad2_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/srad2_kernel.cu) | `82bb52350346cbf3f36701eec711220e971ce907` | `2dfb3660fc1eed707ec0fcafdb21a7711479d61f78a28c33f05a5571d4d9db2a` |
| [compress_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/compress_kernel.cu) | `84a778223d61ab94d7d982209faec22ca348111a` | `6343624f054900b23bbfcb31085b6bb3801c2706a1af1107ce845aecc362f4d9` |
| [makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/srad/srad_v1/makefile) | `6899f1f7a9c3969fdee58d21a3debea49a0dd3f5` | `ce9ed6f06af5d26bf73fd7376fc6d3cf2e785ed6f45f261573968cee4282c3bc` |

## 3. Host calls and kernel order

CPU setup and H2D data; extract once. For iter0..99: prepare -> repeated reduce until one CTA -> D2H sum/sumsq and CPU q0? -> srad -> srad2. Then compress -> D2H image/output (`main.cu:268-429`). Block512 yields ceil229916/512=450 CTAs. Reduce first runs450 CTAs with no229916,mul1, then1 CTA with no450,mul512. Source count is1+100*(1+2+1+1)+1=502 launches across6 unique global definitions. Kernel ordering and blocking statistic copies synchronize dependencies. Statistical ROI covers the full image (`main:198-204`), distinct from trace-capture ROI.

## 4. Detailed kernel implementation

extract/compress map one bounded element/thread with exp/log. prepare writes sum=I,sum2=I? to contiguous arrays. reduce (`reduce_kernel.cu:2-104`) loads partials into two512-element shared buffers, performs a modulo-selected binary reduction with barriers, writes at bx*mul*512; last CTA uses largest power-of-two df<=nf and a scalar remainder loop. srad (`srad_kernel.cu:21-80`) maps row/column, loads center/four clamped neighbors, computes differences/c, writes five arrays. srad2 (`:20-50`) reads own N/W coefficient, south/east coefficients and four differences, then updates I. No GPU atomic or texture.

Static source risk: reduce initial loads `d_sums[ei*d_mul]` at25, but final-block remainder94-95 loads `d_sums[i]` without d_mul. First pass mul1 is consistent; second selected pass mul512,no450,df256 reads unscaled indices256..449 instead of the expected spaced partials131072..229888. This contradicts the partial layout. Preserve the discrepancy; do not patch code or retroactively assert the historical binary had this numerical defect without capture ELF binding.

## 5. Thread and address formulas

i=512b+t,r=i%502,c=floor(i/502) (equivalent source arithmetic srad34-39). Image address=`BI+4*(r+502c)=BI+4i`: lane+4B, next warp+128B, next CTA+2048B. At aligned full warp,1 line/4 sectors. Extract, prepare, compress and difference/coefficient streams follow this formula. N/S=`BI+4*(iN/S[r]+502c)`; W/E=`BI+4*(r+502*jW/E[c])`. Interior accesses are shifted contiguous streams i?1 and i?502. For aligned center warp, ?1 shifts4B ->2 lines/5 sectors; ?502 shifts2008B ->5 sectors and2 lines for an aligned center warp. Column-crossing/clamped warps need explicit address unions. iN/iS load consecutive indices until row wrap; jW/jE are broadcast among lanes sharing a column. Index-array loads precede dependent image addresses.

Reduction mul=m loads `Bsum+4*m*(512b+t)`: lane delta4mB; output is `Bsum+4*m*512b`. First pass m1 coalesces. Second m512 gives lane delta2048B: full active warp touches32 distinct lines/32 sectors for128B useful. First-pass tail CTA has28 live threads; second pass450 live. Shared tree stride changes by reduction step and barriers order updates. The scalar tail actually uses+4B buggy addresses; do not describe it as an ideal strided partial scan. Outer iterations rewrite the same allocations. srad2 I output feeds prepare/stencil next iteration.

## 6. Dataflow, locality, coalescing and concurrency

Image phases450 CTAs, last28 active threads; reduction450->1 and CPU statistic round trip serialize every iteration. Several neighbor/coefficient/difference loads can be independent, but index and center dependencies constrain them. No shared stencil tile is used, so neighboring warps/CTAs reread pixels. In-place update is structurally safe for the stencil because separate srad completes reads before srad2 writes, and srad2 reads neighbor c rather than neighbor I. Four difference arrays,c,I,two sums are8 full FP32 arrays, approximately7.02MiB (7.36MB) excluding neighbor indices. Cross-kernel producer/consumer reuse is possible, not a cache-hit guarantee.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-37`: `IDENTITY_FROZEN`; parameters `["100_0_5_502_458"]`.
- Selected input digest `0e62c67daa020853cf8a90b9f20a42d7e960e4d6c6e1db09173de1a58af199c4` is the registered identity, not automatically original-file SHA.
- Bundle `a8c0d45c76edfd13b02c26ae28e75588b83ff36e22337146b45ce64b509be641`.
- Trace entry `/root/workspace/assets/traces/bundles/a8c0d45c76edfd13b02c26ae28e75588b83ff36e22337146b45ce64b509be641/tree/kernelslist.g`.
- Existing scope `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: Only ordinary trace identity for this program in the72-input matrix; no outcome-dependent replacement. Keep its recorded source/command/content identity. Exact capture-time executable/input-content and full-application provenance are not newly certified.

Header inventory: 502 kernel entries, 507 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z7extractlPf` | `(450,1,1)` | `(512,1,1)` | 1 |
| `_Z7preparelPfS_S_` | `(450,1,1)` | `(512,1,1)` | 100 |
| `_Z6reduceliiPfS_` | `(450,1,1)` | `(512,1,1)` | 100 |
| `_Z6reduceliiPfS_` | `(1,1,1)` | `(512,1,1)` | 100 |
| `_Z4sradfiilPiS_S_S_PfS0_S0_S0_fS0_S0_` | `(450,1,1)` | `(512,1,1)` | 100 |
| `_Z5srad2fiilPiS_S_S_PfS0_S0_S0_S0_S0_` | `(450,1,1)` | `(512,1,1)` | 100 |
| `_Z8compresslPf` | `(450,1,1)` | `(512,1,1)` | 1 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

SOURCE_VERIFIED:6 definitions/502 launches,100 iterations, full-image statistical ROI, FP32 column-major stencil, shifted contiguous neighbors, shared reduction with coalesced first pass and2048B-strided second pass, CPU statistic barrier; apparent unscaled reduction-tail defect. v1_k1 and v2 remain distinct identities.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1: shifted stencil neighbors may create pending-line overlap across warps/CTAs; second reduction uses many distinct lines with only one CTA. Separate tag coverage, physical retention and PIB dependency by phase. EP-L2: derivative writes followed by next-kernel reads, image updates and moment copies create phased read/write/residency demands. Sector amplification, outstanding response lifetimes and queue occupancy need existing identity-bound runtime evidence. Correctness/source-binary risk remains independent of mechanism interpretation.

## 10. Evidence and limits

The sanitized100_0_5_502_458 command is interpreted as100 iterations,lambda0.5,502x458, consistent with the recorded recipe; capture command and ELF remain provenance requirements. Header sequence fits502 launches. Original image bytes, resizing/output correctness and capture ELF were not newly certified. Tail/address concern has independent conditional-agent review. No new execution or input promotion occurred.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
