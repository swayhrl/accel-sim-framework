# Parboil cutcp

## 1. Program and algorithm

Cutoff electrostatic potential on a3D lattice: sum `q/r*(1-r^2/cutoff^2)^2` for atoms inside cutoff, followed by exclusion removal for lattice points too close to atoms. CPU reads PQR atoms, derives bounding box/padding/lattice, geometrically bins atoms, builds neighbor offsets and handles bin overflow atoms. GPU computes bounded8-atom bins; the whole application includes CPU contributions and final region-to-lattice conversion (`main.c:121-169`, `cutoff6overlap.cu:417-464,605-666`).

## 2. Actual source authority and build information

Audited local root: `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/parboil/benchmarks/cutcp/src/cuda`. Fixed upstream repository `accel-sim/gpu-app-collection`, commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. All nonhidden files in this program directory match upstream SHA256 byte-for-byte; see [source hashes](../../contributions/parboil/source_hashes.json). The enclosing local tree has no `.git`; `offline/manifest.lock` declares the commit, and independent content comparison supplies the stronger content evidence. Suite is Parboil; exact original Parboil release and historical capture source revision remain uncertified. `cuda_base` is a separate implementation and is not substituted here.

Build uses the program Makefile and `common/mk/cuda.mk:12-28,112-113`: configurable nvcc flags with default gencode targets 50/60/61/62/70/75. Historical effective command, compiler version, macro overrides, ELF SHA and PTX/SASS provenance are not recovered by reading these defaults. Trace headers record binary version 70, NVBit1.4 and tracer3; that is architecture metadata, not ELF identity.


## 3. Host calls and kernel sequence

Lattice is padded to multiples8; CPU bins atoms into bins of8 float4 records and stores extras separately. Bin spacing4 and constant neighbor list max11^3 are source constants. It uploads binned atoms and neighbor symbols, then launches `cuda_cutoff_potential_lattice6overlap` once per z region plane with grid `(ceil(nx/8),ceil(ny/8))`, block `(8,2,8)` (`cutoff6overlap.cu:340-360,554-602`). CPU computes extras while queued GPU work proceeds; after synchronization, DtoH region data is transposed/added into lattice, CPU exclusions removed and summary output written. A stream is created, but launch uses the default stream, not that handle (`:591-622`); the final device synchronization is the substantive completion barrier.

## 4. Detailed kernel implementation

Single unique kernel has128threads,4096B shared AtomBinCache plus shared metadata. A CTA owns8x8x8 region512 points; each thread computes4 y positions separated2h (`:135-153,168-174,234-262`). Half-warps cooperatively load up to32 neighbor bins/batch to shared. All threads evaluate cached atoms, stop each bin at zero charge, branch by cutoff distance, accumulate4 energy registers, and barrier before cache overwrite. `#undef NEIGHBOR_COUNT` fixes electrostatic mode in file despite alternate count code. CPU overflow path must not be omitted from algorithm description.

## 5. Thread and address formulas

Flatten `t=tx+8ty+16tz`, tx0..7,ty0..1,tz0..7. Region base short form `R=((zPlane*Gy+by)*Gx+bx)*512` floats. Physical point coordinates `(8bx+tx,8by+ty+2s,8zPlane+tz)*h`, s0..3. Output address is `Pregion+4[R+64*floor(t/16)+(t%16)+16s]` (`:147-153,274-277`). Adjacent lanes within each halfwarp delta4B, but at lane15 -> 16 jumps196B for fixed s. Each instruction writes two64B runs separated256B starts: aligned each run is two32B sectors and one128B line; together four sectors/two lines (line utilization50% for that instruction). Across s0..3, each halfwarp fills a contiguous256B region; this is aggregate spatial coverage, not one-instruction coalescing.

Neighbor q=t>>4 starts nbrid, then increments8 across four cached bins. Logical bin integer `b=((k*binDim_y+j)*binDim_x+i)` with offsets from constant NbrList. Global float address `Pbin+4*(32b+(t&15)+16v)`, v0/1 (`:183-199`). A halfwarp loads64B per v; the two v fill one aligned128B bin of8float4 atoms. Different halfwarps select different neighbor bins, so warp contains two independent64B spans; neighbor bins need not be adjacent. Same-thread next load v moves64B; next bincnt changes bin according to neighbor offset, not a fixed lane stride. Constant NbrList has halfwarp-uniform indices; exact constant-cache serialization is implementation-dependent.

Other CTA warps load distinct bins into shared but all128 threads reuse each cached atom while evaluating their4points. Neighboring regions and z-plane launches can read overlapping bins. Different CTAs write disjoint512float regions; cross-kernel bin reuse exists without producer/consumer output dependency. No source global atomic. Source refs `:164-201,209-271` support the distinction between loading and evaluating loops.

## 6. Dataflow, locality, merging and concurrency

Shared cache amortizes each atom load over512 lattice evaluations. Distance predicates and zero-charge early exit are input-dependent. Independent CTA regions offer concurrency; one CTA's shared barriers couple warp progress per batch. Across planes, bin data may remain reusable, but actual residency and pending overlap depend on working set/scheduling. The CPU fallback can overlap GPU computation; GPU trace timing cannot represent the whole CPU+GPU application by itself.

## 7. Frozen input and trace binding

Frozen `P42-11`, input identity `af7320f9d9dc662971b1856cac87f29f9b8e4b2a65a7f9d4223bb7a74803fef8`, bundle `c8d37e06b1bc773df62f434a04c1052dd647ab85bc1ab1f181c576e8f2685b2a` from `DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json` at atlas base `3b28d3064`. Parameter encoding `_i___data_small_input_watbox_sl40_pqr__o_lattice_dat`. Registered input identity is not newly certified original data-byte SHA. Small ordered header evidence: [trace_metadata.json](../../contributions/parboil/trace_metadata.json).

| Unique kernel | Grid | Block | Launches |
|---|---|---|---|
| `_Z37cuda_cutoff_potential_lattice6overlapiiP6float4fffPfi` | `(11,11,1)` | `(8,2,8)` | 11 |

Scope remains `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`. Only kernelslist and first20 trace-header lines were read; capture-time ELF, original dataset-content linkage and full application completion remain uncertified. No raw output, workload identity or accepted result was modified.

Eleven recorded11x11 grids agree with11 z planes and88x88x88 padded lattice under this source. Original unpadded extents, atom distribution and CPU extra-atom contribution are not determined by trace geometry alone.

## 8. Source-provable architecture features

Geometric bin gather,128B per8-atom bin, shared cooperative cache, four outputs/thread, halfwarp contiguous global paths, constant neighbor offsets and repeated plane launches. No source atomic; nontrivial CPU computation lies outside GPU trace.

## 9. DTC-L1 / EP-L2 hypotheses requiring validation

DTC-L1: test repeated neighboring-bin lines for pending overlap versus physical retention, with halfwarp instruction coverage distinguished from all-output coverage. EP-L2: test bin sharing across regions/planes, output store/writeback pattern and source-to-model line mapping. Resource lifetime, queue demand, exact cache conflicts and numerical correctness require runtime/binary evidence; static spatial overlap is insufficient.

## 10. Evidence and limitations

`SOURCE_VERIFIED=true` for the fixed content and source behavior below; `INPUT_BOUND=registered_identity_only`; `BINARY_BOUND=false`; `TRACE_SCOPE_BOUND=registered_sequence_only`; `RUNTIME_MEASURED=false` in this audit; `UNRESOLVED=true` for historical content/ELF/full-application linkage. These are independent dimensions. No GPU, native benchmark, capture, simulator or performance experiment was executed. No cache hit, MSHR merge, occupancy, latency, reuse distance or throughput was inferred as measured.


Fixed source references at commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`:

- [main.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/cutcp/src/cuda/main.c)
- [cutoff6overlap.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/cutcp/src/cuda/cutoff6overlap.cu)
- [cutoff.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/cutcp/src/cuda/cutoff.h)
- [cutcpu.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/cutcp/src/cuda/cutcpu.c)
- [excl.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/cutcp/src/cuda/excl.c)
- [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/cutcp/src/cuda/Makefile)
