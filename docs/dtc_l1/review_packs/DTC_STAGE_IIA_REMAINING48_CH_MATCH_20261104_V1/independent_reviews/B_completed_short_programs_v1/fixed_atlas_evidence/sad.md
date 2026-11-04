# Parboil sad

## 1. Program and algorithm

Variable block size motion estimation: for each4x4 current-image block, evaluate SAD `sum(abs(reference_pixel-current_pixel))` for1089 displacements in a33x33 search window, then sum elementary SADs into4x8,8x4,8x8,8x16,16x8,16x16 shapes. Images are16bit pixels with16bit width/height headers (`image.c:30-36`). Output stores selected six macroblock rows, not the whole result (`main.cu:141-188`), although device computes all macroblocks.

## 2. Actual source authority and build information

Audited local root: `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/parboil/benchmarks/sad/src/cuda`. Fixed upstream repository `accel-sim/gpu-app-collection`, commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. All nonhidden files in this program directory match upstream SHA256 byte-for-byte; see [source hashes](../../contributions/parboil/source_hashes.json). The enclosing local tree has no `.git`; `offline/manifest.lock` declares the commit, and independent content comparison supplies the stronger content evidence. Suite is Parboil; exact original Parboil release and historical capture source revision remain uncertified. `cuda_base` is a separate implementation and is not substituted here.

Build uses the program Makefile and `common/mk/cuda.mk:12-28,112-113`: configurable nvcc flags with default gencode targets 50/60/61/62/70/75. Historical effective command, compiler version, macro overrides, ELF SHA and PTX/SASS provenance are not recovered by reading these defaults. Trace headers record binary version 70, NVBit1.4 and tracer3; that is architecture metadata, not ELF identity.

## 3. Host calls and kernel sequence

`main.cu:263-326` requires equal image dimensions divisible16, uploads current image as global linear memory and reference as CUDA array bound to texture, and zeros the41-shape SAD allocation. Exactly three dependent launches follow: `mb_sad_calc`, `larger_sad_calc_8`, `larger_sad_calc_16` (`:331-352`). All SADs are copied back, then optional output samples six rows. No iterative search termination: finite pixel loops and search domain determine work.

## 4. Detailed kernel implementation

`sad4.h:26-31` fixes POS_PER_THREAD18, THREADS_W=THREADS_H=1; `sad.h:10-19` fixes range16,1089 positions, stride1096. `mb_sad_calc` uses61 threads/CTA. The first16 copy one4x4 block to32B shared `frame_loc`; CTA barrier follows. Each thread computes up to18 positions in groups of3, sharing six reference texture fetches per row to form3 neighboring SADs; it writes shared `sad_loc`, then barriers and first32 threads copy8B vectors to global (`sad4.cu:62-218`). Dynamic SAD shared storage is2192B. Only1089 search positions are computed; the vector copy also moves the seven uncomputed padding shorts, whose values must not be interpreted as valid SAD results. No global atomics.

`larger_sad_calc_8` uses `(32,4)` threads: y decomposes into tx=y&1 and ty=y>>1 selecting a2x2 group of4x4 subblocks; each lane processes packed pairs of16bit SADs and writes five packed combinations. `_16` uses32 threads and combines four8x8 input rows into larger shapes (`largerBlocks.cu:19-125`). They use uint pair arithmetic to reduce instruction count; no barrier is needed because inputs are produced by prior kernels.

## 5. Thread and address formulas

Let W=16*mb_width, M=mb_width*mb_height, P=1096, macroblock index m=mb_y*mb_width+mb_x. Current pixel read by first16 threads g is `PF+2[(4by+floor(g/4))*W+4bx+(g%4)]` for this1x1 tile; lane delta2B within each4-pixel row but jumps `2W-6`B between rows (`sad4.cu:81-102`). It is four8B runs, not a contiguous32B16-lane load.

Compute thread t owns search base18t; loop adds3. For position s, logical reference coordinates are `(4bx-16+s%33+dx,4by-16+floor(s/33)+dy)`, dx0..5,dy0..3 for fused triple. Adjacent compute lanes shift search base18, wrap33; consecutive same-thread loop shifts3 with row wrap. Texture array physical layout, clamp/address-mode behavior and cache route cannot be converted into a flat-global coalescing count from this expression alone.

4x4 SAD global short base offset is `O=(25M+16m+4*block_y+block_x)*P`; first32 transfer threads lane l store `PS+2O+8(l+32r)`. Lane delta8B, same-thread transfer loop delta256B; an aligned full warp spans256B = two128B lines/eight32B sectors per8B vector operation (compiler splitting can change instruction granularity). The2192B row stride is17*128+16, so successive subblock alignment rotates by16B rather than preserving line alignment.

For `_8`, short input base `I=(25M+8ty+2tx)P+16mP`; each uint access is `PS+2I+4(l+32r+dP/2)` with d0,1,4,5. `_16` uses `I=(5M+4m)P`, d0,1,2,3. Both have lane delta4B and loop delta128B: an aligned32lane instruction covers one128B line/four sectors; arbitrary alignment can require two/five. Exact output bases are `largerBlocks.cu:43-58,99-107`; they are disjoint shape regions of the same allocation. Other warps in `_8` access different subblock groups. Adjacent4x4 CTAs overlap reference search regions and usually share current-frame lines, while SAD outputs are disjoint but can share boundary lines.

## 6. Dataflow, locality, merging and concurrency

Texture overlap is substantial logically; shared frame reuse is61 threads across1089 positions. Kernel1 produces16 elementary shape rows per macroblock; kernel2 produces20 intermediate rows; kernel3 produces5 largest rows. Kernel completion orders these consumers. Thousands of small61-thread CTAs expose potential concurrency but only two warps per CTA with partial final warp. Packed reduction stages have four/one warp per CTA and contiguous global streams. Actual ordinary-L1 demand excludes or includes texture traffic according to simulator path; do not count every tex2D as ordinary L1.

## 7. Frozen input and trace binding

DTC frozen selection is `P42-33` from `DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json` at atlas base `3b28d3064`. Logical input digest `db89be14146b916373c1adb28803767aa725a592119901ffd78d9c223e1611a9`; bundle `178d2727ac4c62dcdf43759fad32f91229d01e916f7b7b10877bbfa99ae2acb2`. Recorded parameter encoding: `_i___data_default_input_reference_bin___data_default_input_frame_bin__o_out_bin`. This digest is the registered identity; it is not newly certified SHA256 of original input bytes.

Only small `kernelslist.g` and first20 header lines per listed trace were read. Ordered header evidence is in [trace_metadata.json](../../contributions/parboil/trace_metadata.json); the frozen file inventories and content hashes remain in the original freeze. 3 launches are listed:

| Unique trace kernel | Grid | Block | Launches |
|---|---|---|---|
| `_Z11mb_sad_calcPtS_ii` | `(44,36,1)` | `(61,1,1)` | 1 |
| `_Z17larger_sad_calc_8Ptii` | `(11,9,1)` | `(32,4,1)` | 1 |
| `_Z18larger_sad_calc_16Ptii` | `(11,9,1)` | `(32,1,1)` | 1 |

Frozen scope is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`. No new certification of capture-time executable or original input bytes. Matching names and dimensions support an implementation correspondence, not proof of full application completion, exact arguments, data values, or native correctness. No source, binary, input, trace or accepted performance evidence was changed.

Observed grid44x36 for1x1 four-pixel tiles and macroblock grid11x9 agree with176x144 pixels under this source, but do not certify original image bytes.

## 8. Source-provable architecture features

Mixed texture/global/shared paths, read overlap between neighboring search windows,61-thread base CTAs, vector8B output copies,1096short row padding, and dependent multi-kernel packed reductions. Output checker scope is six macroblock rows; it does not independently certify all device results.

## 9. DTC-L1 / EP-L2 hypotheses requiring validation

DTC-L1: isolate base texture accesses from ordinary global frame/SAD accesses; test whether packed SAD producers and consumers stress searchable Tag coverage and physical retention differently. Identical source addresses at different kernel phases do not imply simultaneous pending requests. EP-L2: inspect overlapping reference windows, vector output traffic, and cross-kernel SAD residency/evictions. Same-name EP sad requires identical image SHA, texture configuration, source variant, launch sequence and ROI before a shared runtime claim.

## 10. Evidence and limitations

`SOURCE_VERIFIED=true` for the fixed content and source behavior below; `INPUT_BOUND=registered_identity_only`; `BINARY_BOUND=false`; `TRACE_SCOPE_BOUND=registered_sequence_only`; `RUNTIME_MEASURED=false` in this audit; `UNRESOLVED=true` for historical content/ELF/full-application linkage. These are independent dimensions. No GPU, native benchmark, capture, simulator or performance experiment was executed. No cache hit, MSHR merge, occupancy, latency, reuse distance or throughput was inferred as measured.

Every source reference below uses fixed commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`; line ranges in the text refer to these exact files.

- [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sad/src/cuda/main.cu)
- [sad4.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sad/src/cuda/sad4.cu)
- [sad4.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sad/src/cuda/sad4.h)
- [sad.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sad/src/cuda/sad.h)
- [largerBlocks.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sad/src/cuda/largerBlocks.cu)
- [image.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sad/src/cuda/image.c)
- [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sad/src/cuda/Makefile)

Historical capture binary and original input linkage are unresolved even though fixed source contents and launch geometry correspond.
