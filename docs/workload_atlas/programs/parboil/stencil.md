# Parboil stencil

## 1. Program and algorithm

3D seven-point Jacobi update on a float grid with fixed boundary values: `next=(six axial neighbors)*c1-center*c0`, c0=1/6,c1=1/36. CPU reads nx*ny*nz floats, command line supplies dimensions and iteration count. Two grids are ping-ponged; host terminates after exactly iteration launches (`main.cu:66-77,125-132`).

## 2. Actual source authority and build information

Audited local root: `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/parboil/benchmarks/stencil/src/cuda`. Fixed upstream repository `accel-sim/gpu-app-collection`, commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. All nonhidden files in this program directory match upstream SHA256 byte-for-byte; see [source hashes](../../contributions/parboil/source_hashes.json). The enclosing local tree has no `.git`; `offline/manifest.lock` declares the commit, and independent content comparison supplies the stronger content evidence. Suite is Parboil; exact original Parboil release and historical capture source revision remain uncertified. `cuda_base` is a separate implementation and is not substituted here.

Build uses the program Makefile and `common/mk/cuda.mk:12-28,112-113`: configurable nvcc flags with default gencode targets 50/60/61/62/70/75. Historical effective command, compiler version, macro overrides, ELF SHA and PTX/SASS provenance are not recovered by reading these defaults. Trace headers record binary version 70, NVBit1.4 and tracer3; that is architecture metadata, not ELF identity.


## 3. Host calls and kernel sequence

Allocate two arrays, copy input to d_A0, then device-to-device duplicate into d_Anext so both boundaries exist (`main.cu:101-107`). Build block32x4 and grid `(ceil(nx/64),ceil(ny/4))`, shared1024B. Each iteration invokes the same `block2D_hybrid_coarsen_x` once and swaps pointers. After loop an extra swap makes d_Anext point at final result, then DtoH/write (`:111-148`). The declaration in unused kernels.h has a stale signature; main includes kernels.cu directly (`:16`).

## 4. Detailed kernel implementation

`kernels.cu:12-102` coarsens x by2. Each thread owns two x points separated32 and walks k=1..nz-2. Bottom plane values live in registers, current xy plane in shared memory, top plane streams from global. Interior x/y neighbor reads use shared; CTA edge halos read global. Two barriers per z iteration protect shared overwrite; two setup barriers initialize/fill. No global atomic. Predicates suppress boundary stores while loading valid halo coordinates. Arrays retain fixed boundary values through ping-pong copies.

## 5. Thread and address formulas

For CTA bx,by and thread tx,ty: `i=64bx+tx`, `i2=i+32`, `j=4by+ty`; linear index `I=i+nx*(j+ny*k)` (`common.h:11`, `kernels.cu:16-20`). Byte address `P+4I`. Shared current addresses are `4*(tx+64ty)` and that+128B. Top load uses k+1; output uses k. y halo shifts +/-4nxB, x halo +/-4B, bottom/top planes +/-4nxnyB. Within a warp ty fixed and tx spans0..31: adjacent lanes delta4B; same-thread z loop delta4nxnyB; coarsened second point delta128B. Other warps cover consecutive y rows separated4nxB. Adjacent bx CTAs share x halos; by CTAs share y halos; all own disjoint outputs.

For fixed plane and array, each aligned fullwarp load/store is128B = one128B line/four32B sectors. Interior-store predicates make edge warps partial; the first/last i masks cannot be replaced by fullwarp traffic. y halos retain lane contiguity; x halo accesses occur only tx0 or31 in first/second coarsened region, so one4B useful access may fetch a32B sector, subject to cache/combining. At nx128,ny128 the z-loop stride is65536B and plane alignment is preserved, not evidence of measured set conflict. Source refs `kernels.cu:41-98` establish all paths.

## 6. Dataflow, locality, merging and concurrency

The rolling plane avoids reloading center and z-neighbors from global every stencil evaluation. CTAs duplicate halo loads; within CTA shared reuse spans four warps. Per-z barriers couple warp progress, while64 observed CTAs can run independently subject to hardware resources. Across100 observed launches, each output becomes next input; boundaries remain unchanged. Static repeating footprints provide potential temporal reuse, not exact reuse distance or hit rate.

## 7. Frozen input and trace binding

Frozen `P42-38` from `DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, atlas base `3b28d3064`. Registered input identity `c885293ad99e21ee6f270647dc47f1e6b214c71856b189cd011266ce4ae21266`; bundle `a42e996921c44fb398e05d3f791995022b5c5c3980047817e81dab111b598a20`. Parameter encoding `_i___data_small_input_128x128x32_bin__o_128x128x32_out____128_128_32_100`. This is registered identity, not newly certified original dataset-content SHA. [Ordered small-header metadata](../../contributions/parboil/trace_metadata.json) records 100 launches:

| Unique kernel | Grid | Block | Launches |
|---|---|---|---|
| `_Z24block2D_hybrid_coarsen_xffPfS_iii` | `(2,32,1)` | `(32,4,1)` | 100 |

Only kernelslist and first20 header lines per listed trace were read; no bulk raw trace was scanned. Scope remains `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`; capture-time binary, original input bytes, actual arguments and full application completion are not newly certified. Frozen member hashes remain authoritative. No existing identity or scientific result was changed.

Frozen parameters12812832100 and observed grid2x32 block32x4 are consistent with full100-iteration loop and30 interior z slices/point, but historical binary/data/full completion remain independent evidence gaps.

## 8. Source-provable architecture features

Regular coalesced planes, x coarsening, shared xy reuse, register z reuse, boundary-only halo global reads and100 dependent ping-pong launches. Fixed-plane power-of-two strides are demonstrable; specific bank/hash conflicts are not.

## 9. DTC-L1 / EP-L2 hypotheses requiring validation

DTC-L1: isolate halo overlap and main plane streams to test whether physical retention or Tag demand matters despite shared reuse; pending requests across CTAs may arrive too far apart to merge. EP-L2: test repeated whole-grid ping-pong retention, writeback bursts and line ownership across phase changes. Exact queue occupancy and return lifetime need trace/runtime evidence; barriers do not imply all CTAs are synchronized inside a launch.

## 10. Evidence and limitations

`SOURCE_VERIFIED=true` for the fixed content and source behavior below; `INPUT_BOUND=registered_identity_only`; `BINARY_BOUND=false`; `TRACE_SCOPE_BOUND=registered_sequence_only`; `RUNTIME_MEASURED=false` in this audit; `UNRESOLVED=true` for historical content/ELF/full-application linkage. These are independent dimensions. No GPU, native benchmark, capture, simulator or performance experiment was executed. No cache hit, MSHR merge, occupancy, latency, reuse distance or throughput was inferred as measured.


Fixed source references (all at commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`):

- [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/stencil/src/cuda/main.cu)
- [kernels.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/stencil/src/cuda/kernels.cu)
- [common.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/stencil/src/cuda/common.h)
- [kernels.h](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/stencil/src/cuda/kernels.h)
- [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/stencil/src/cuda/Makefile)
