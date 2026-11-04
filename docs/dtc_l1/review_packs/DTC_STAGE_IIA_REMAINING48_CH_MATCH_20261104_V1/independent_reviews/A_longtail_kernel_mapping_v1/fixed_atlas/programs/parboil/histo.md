# Parboil histo

## 1. Program and algorithm

Histogram image uint32 values into byte bins saturated at255. Input header contains image width/height and histogram width/height, followed by uint32 values (`main.cu:100-125`). It estimates a central value range, maps each input into a packed descriptor, builds per-CTA shared partial histograms for central bins plus global tails/overflows, then reduces and saturates output. It differs from CUDA Samples histogram in data representation, range selection, atomics and launch sequence.

## 2. Actual source authority and build information

Audited local root: `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/parboil/benchmarks/histo/src/cuda`. Fixed upstream repository `accel-sim/gpu-app-collection`, commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. All nonhidden files in this program directory match upstream SHA256 byte-for-byte; see [source hashes](../../contributions/parboil/source_hashes.json). The enclosing local tree has no `.git`; `offline/manifest.lock` declares the commit, and independent content comparison supplies the stronger content evidence. Suite is Parboil; exact original Parboil release and historical capture source revision remain uncertified. `cuda_base` is a separate implementation and is not substituted here.

Build uses the program Makefile and `common/mk/cuda.mk:12-28,112-113`: configurable nvcc flags with default gencode targets 50/60/61/62/70/75. Historical effective command, compiler version, macro overrides, ELF SHA and PTX/SASS provenance are not recovered by reading these defaults. Trace headers record binary version 70, NVBit1.4 and tracer3; that is architecture metadata, not ELF identity.


## 3. Host calls and kernel sequence

`main.cu:128-149` pads input width to even and height to16, allocates mapping and histogram buffers, uploads actual rows, then repeats numIterations times (`:153-201`): initialize range -> prescan -> DtoH min/max -> clear partial buffer -> intermediates -> main -> final. Four distinct kernels occur per iteration, not four independent benchmark programs. Main y grid is data-dependent selected range count; final combines14 x partitions. Final also clears global tail/overflow regions for the next iteration. Optional output copies and writes saturated bytes after all repetitions. Only argv1 is consumed as iteration count; an additional frozen trailing4 is not used by this main.

## 4. Detailed kernel implementation

Prescan (`histo_prescan.cu:15-84`) uses64x512 threads. Each CTA samples only first1/8 of its stripe, each thread scans with stride512 twice for average and standard deviation; shared reductions then thread0 atomicMin/Max updates two range words using10-sigma heuristic. These range estimates choose algorithm path and launches, not a complete input histogram.

Intermediates (`histo_intermediates.cu:14-66`) uses ceil(height/16) CTAs and ceil(width/2) threads. uint2 loads produce descriptors uchar4 `(range,indexhi,indexlo,bitoffset)` for each value. A16-row unroll has no explicit last-height guard; width odd skips final second descriptor. Descriptor allocation is only true image size, so nonmultiple16 height is a source boundary risk needing actual input/ELF evidence.

Main (`histo_main.cu:118-189`) uses14 x partitions, selected-range y partitions,768threads (KB24). Every y partition scans the same x-partition descriptor stream, testing whether descriptor belongs to its24KiB-bin range. Shared array is24x256 uint =24576B: each word packs four8bit bins. atomicAdd on a shared packed word increments selected byte; overflow at255 emits global corrections, potentially cascading. Only y0 also updates outside-range global tails with packed16bit atomicAdd. After barrier, each CTA copies6144 uint words to its private subhistogram slice.

Final (`histo_final.cu:12-108`) has42x512 threads: low/high ranges load packedushort4 tails, clear them and saturate to uchar4; central range loads/clears uint4 overflow, loops over14 partial histograms, extracts packed bytes, accumulates, saturates and writes uchar4. No GPU global inter-CTA synchronization inside a phase; kernel boundaries enforce dependencies.

## 5. Thread and address formulas

Prescan stripe S=floor(num_elements/64), address index `a=bx*S+tx+512r`, bound bx*S+S/8. `input=P+4a`; adjacent lanes delta4B, same-thread loop2048B; same array is scanned twice. Partial reduction then atomics target `Prange+0` and+4 (two words, source may share sector).

Intermediates line=16bx, pitch=ceil(width/2) uint2. At unroll row r, load `Pinput+8*((16bx+r)*pitch+tx)`; lane delta8B, loop delta8pitchB. Descriptor stores `Pmap+4*((16bx+r)*width+tx)` and +4*blockDim.x for second value. Aligned32lane uint2 load spans256B/two128B lines/eight32B sectors; each descriptor instruction spans128B/one line/four sectors. Odd width changes store mask and row alignment.

Main descriptor index `a=768bx+tx+10752r`; `Pmap+4a`, lane delta4B, same-thread iteration43008B. Different y CTAs with same bx read identical descriptors; different x CTAs partition stream. For descriptor `(rx,hi,lo,off)`, shared atomic word is `Pshared+4*(256hi+lo)` and addend `1<<off`; the logical bin `b=24576rx+off/8+4lo+1024hi`. Out-of-range tail atomic address is `Ptail+4*floor(b/2)` with shift0/16, overflow atomic is `Pover+4*b` plus possible neighboring corrections (`histo_main.cu:14-98`). Lane delta for these targets is data-dependent; no claim of uniform or random bin distribution is justified.

CTA partial store uint index is `bx*(Hh*Wh/4)+(range_min+by)*6144+tx+768r`; lane delta4B, loop3072B. Final thread index u=512bx+tx and grid stride21504. Tail ushort4 index i produces address `Ptail+8i`, final uchar4 address `Pfinal+4i`; central overflow uint4 address `Pover+16i`, partial histogram address `Psub+4*(i+j*Hh*Wh/4)` for j0..13. Lane delta8/4/16/4 respectively; same-thread inner j partial-load stride Hh*Wh bytes. These vector expressions refer to source operations, not guaranteed single SASS instruction widths.

For aligned fullwarps, float/uint/uchar4 streams cover one128B line/four32B sectors;8B streams two/eight,16B streams four/sixteen. Base/row misalignment and partial masks change counts. Atomic target footprint may collapse many lanes to one word/sector or spread across32; exact sector count requires data. Across main y CTAs descriptor overlap is a source-proven opportunity; simultaneous MSHR merging is not.

## 6. Dataflow, locality, merging and concurrency

Prescan result returns to host and controls main-grid y count. Intermediates produces one mapping reused by all selected-range partitions, trading repeated scans for shared-atomic histogram privatization. Shared contention concerns packed word, even different logical byte bins may collide. Global atomics are conditional tails/overflow, so frequency depends on value distribution and accumulated counts. Final streaming reduction traverses14 disjoint partial slices with per-bin arithmetic dependencies. Barriers couple CTA phases; grids permit many independent CTAs but actual residency must account for24KiB shared and compiled register demand.

## 7. Frozen input and trace binding

Frozen `P42-18`, input identity `2c506bf13c81ff5dd4c286fa2f6d7a9edea513a5c8f38c60cfc746e36e9c5f64`, bundle `7e62ee69713480076957f59f2cdc346681853f67fff52449cc82cafede3a7ccc` from `DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json` at atlas base `3b28d3064`. Parameter encoding `_i___data_default_input_img_bin__o_ref_bmp____20_4`. Registered identity is not newly certified original input-content SHA. [trace_metadata.json](../../contributions/parboil/trace_metadata.json) preserves ordered small headers. Scope `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`; capture ELF, input-byte linkage and full application completion remain unresolved. Only kernelslist and first20 header lines were inspected, with no raw bulk scan or runtime action.

Observed80 launches are20 repetitions of prescan -> intermediates -> main -> final. Prescan grid64 block512; intermediates grid65 block498; main grid14x3 block768; final42x512. This is consistent with20 requested iterations and three selected ranges, but width is only constrained by ceil(width/2)=498 and height by ceil(height/16)=65 under this source. Raw original header was not newly bound. Main allocation sizes use img_width in several places where kernel indexing uses histo_width (`main.cu:140-143`); padding, original header and binary identity are needed to certify bounds, rather than assuming these widths equal.

## 8. Source-provable architecture features

Four dependent stages, small shared reduction, uint2 mapping loads, replicated descriptor scans, packed shared atomics, conditional global RMW tails/overflow, partial histogram stores and a14-way final reduction. Central shared histogram operations do not all reach L2. Input distribution changes both launch grid and transaction mix.

## 9. DTC-L1 / EP-L2 hypotheses requiring validation

DTC-L1: test replicated descriptor streams for pending same-line overlap and retained lines, separating shared atomics from ordinary-L1 requests. Final strided partial slices may produce different Tag demand than input scans. EP-L2: distinguish global tail/overflow RMWs, bulk partial writes and final reduction reads; test cross-phase residency and atomic hot bins. Range count alone does not measure contention, cache conflicts or queue occupancy.

## 10. Evidence and limitations

Independent source audit issue: `main.cu:137-166` allocates `global_histo` and `global_overflow` without explicitly clearing them before the first iteration, while main/final may read them (`histo_main.cu:32-37,94-97`, `histo_final.cu:32,53`). Later final kernels clear visited regions. This is an input/path-dependent initialization risk in the audited source; capture binary equivalence and native validity are not established here, so this does not invalidate or rewrite existing accepted results.

`SOURCE_VERIFIED=true` for the fixed content and source behavior below; `INPUT_BOUND=registered_identity_only`; `BINARY_BOUND=false`; `TRACE_SCOPE_BOUND=registered_sequence_only`; `RUNTIME_MEASURED=false` in this audit; `UNRESOLVED=true` for historical content/ELF/full-application linkage. These are independent dimensions. No GPU, native benchmark, capture, simulator or performance experiment was executed. No cache hit, MSHR merge, occupancy, latency, reuse distance or throughput was inferred as measured.


Fixed source references at commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`:

- [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/histo/src/cuda/main.cu)
- [histo_prescan.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/histo/src/cuda/histo_prescan.cu)
- [histo_intermediates.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/histo/src/cuda/histo_intermediates.cu)
- [histo_main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/histo/src/cuda/histo_main.cu)
- [histo_final.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/histo/src/cuda/histo_final.cu)
- [util.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/histo/src/cuda/util.h)
- [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/histo/src/cuda/Makefile)
