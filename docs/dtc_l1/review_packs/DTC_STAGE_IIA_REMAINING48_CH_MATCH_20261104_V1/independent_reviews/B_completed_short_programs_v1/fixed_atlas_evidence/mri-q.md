# Parboil mri-q

## 1. Program and algorithm

Construct complex Q at spatial positions x: `Q(x)=sum_k |phi(k)|^2 exp(i*2*pi*k dot x)`. Inputs hold k coordinates, spatial x/y/z and phi real/imag; outputs are Qr/Qi arrays. `main.cu:81-108` optionally limits numK via command-line integer, so a path name alone does not establish sample count.

## 2. Actual source authority and build information

Audited local root: `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/parboil/benchmarks/mri-q/src/cuda`. Fixed upstream repository `accel-sim/gpu-app-collection`, commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. All nonhidden files in this program directory match upstream SHA256 byte-for-byte; see [source hashes](../../contributions/parboil/source_hashes.json). The enclosing local tree has no `.git`; `offline/manifest.lock` declares the commit, and independent content comparison supplies the stronger content evidence. Suite is Parboil; exact original Parboil release and historical capture source revision remain uncertified. `cuda_base` is a separate implementation and is not substituted here.

Build uses the program Makefile and `common/mk/cuda.mk:12-28,112-113`: configurable nvcc flags with default gencode targets 50/60/61/62/70/75. Historical effective command, compiler version, macro overrides, ELF SHA and PTX/SASS provenance are not recovered by reading these defaults. Trace headers record binary version 70, NVBit1.4 and tracer3; that is architecture metadata, not ELF identity.


## 3. Host calls and kernel sequence

`main.cu:115-148` uploads phiR/I, runs PhiMag once, copies magnitudes back and assembles CPU AoS kValues. Then x/y/z upload, zero Q arrays, and `computeQ_GPU` loops over ceil(numK/1024) K tiles: copy up to1024 kValues to constant symbol ck and launch Q (`computeQ.cu:111-135`). Q is copied back and optionally written; preprocessing is partly CPU, not a GPU-only pipeline. Kernel boundaries and symbol copies serialize K-tile updates.

## 4. Detailed kernel implementation

`ComputePhiMag_GPU` (`computeQ.cu:38-46`) has512threads/CTA, one sample/thread, guarded tail, two global loads and one global store. Q (`:48-97`) has256threads/CTA, one spatial point/thread and no numX bounds check; safe coverage requires numX multiple256 or equivalent padded allocation. Despite comment saying shared memory, sX/Y/Z/Qr/Qi are scalar thread temporaries, not declared shared. Constant `ck[1024]` contains four floats/sample. An odd-numK prologue handles ck0 before pair-unrolled loop; each thread serially accumulates sin/cos contributions and stores Qr/Qi. There are no source atomics or CTA barriers inside Q.

## 5. Thread and address formulas

Phi sample u=512bx+tx: `phiR/I/Mag = P+4u`. Q spatial u=256bx+tx: x/y/z/Qr/Qi all `P+4u`. Adjacent lanes delta4B and different warps advance128B; aligned fullwarp accesses one128B line/four32B sectors per array instruction, unaligned potentially two/five. Q loop k has constant-member address `Pck+16k+4f` for field f0..3. At a fixed k all lanes have the same constant address (broadcast opportunity); same-thread consecutive paired iterations advance32B and inner paired member k+1 advances16B. It is not a lane-strided16B global load. Constant cache transactions cannot automatically be counted as normal global-L1 sectors.

Different CTAs have disjoint spatial outputs yet consume identical ck tile; successive Q kernels read/write identical Q arrays and reread x/y/z. PhiMag output reaches Q through GPU -> CPU transfer, CPU AoS packing and symbol upload; there is no direct persistent GPU phiMag-to-Q array reuse. These formulas follow `computeQ.cu:27-36,40-44,59-96,125-134`.

## 6. Dataflow, locality, merging and concurrency

x/y/z and partial Q are loaded once into registers per Q invocation, then used across up to1024 arithmetic iterations. Constant data is shared across lanes and CTAs. Independent spatial CTAs provide parallelism; per-thread Q accumulation is a dependency chain. Observed128 Q CTAs correspond to32768 spatial threads under this source; three Q launches imply2049..3072 samples if this unmodified ceil rule and full sequence apply, not an exact numK. PhiMag grid6 is compatible. Symbol upload between launches prevents concurrent independent K tiles of the same Q array.

## 7. Frozen input and trace binding

Frozen `P42-25` from `DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, atlas base `3b28d3064`. Registered input identity `dc7a91531846c1134c197a6e83509c91b2768151692a7b1286f6be9c431cabd4`; bundle `1ece1cea31a1048a3aab8bde6bc064c4aaf2b9ffeff64d2d18794157fb12e379`. Parameter encoding `_i___data_small_input_32_32_32_dataset_bin__o_32_32_32_dataset_out`. This is registered identity, not newly certified original dataset-content SHA. [Ordered small-header metadata](../../contributions/parboil/trace_metadata.json) records 4 launches:

| Unique kernel | Grid | Block | Launches |
|---|---|---|---|
| `_Z17ComputePhiMag_GPUPfS_S_i` | `(6,1,1)` | `(512,1,1)` | 1 |
| `_Z12ComputeQ_GPUiiPfS_S_S_S_` | `(128,1,1)` | `(256,1,1)` | 3 |

Only kernelslist and first20 header lines per listed trace were read; no bulk raw trace was scanned. Scope remains `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`; capture-time binary, original input bytes, actual arguments and full application completion are not newly certified. Frozen member hashes remain authoritative. No existing identity or scientific result was changed.

## 8. Source-provable architecture features

Two distinct kernels, CPU feedback preprocessing, constant-memory broadcast, regular global streams, repeated Q partial sums across K-tile launches, no explicit atomics. Boundary assumptions and optional numK override are part of correctness/scope audit.

## 9. DTC-L1 / EP-L2 hypotheses requiring validation

DTC-L1: separate ordinary global Q/x arrays from constant path and test whether small streaming bursts or repeated partial-Q retention create Tag/physical-line demand; constant logical overlap does not prove PIB merges. EP-L2: quantify global Q read-modify-write traffic across tiles, constant fill traffic and cross-kernel residency. Long compute loops may alter overlap, but latency or memory-boundedness requires actual runtime counters.

## 10. Evidence and limitations

`SOURCE_VERIFIED=true` for the fixed content and source behavior below; `INPUT_BOUND=registered_identity_only`; `BINARY_BOUND=false`; `TRACE_SCOPE_BOUND=registered_sequence_only`; `RUNTIME_MEASURED=false` in this audit; `UNRESOLVED=true` for historical content/ELF/full-application linkage. These are independent dimensions. No GPU, native benchmark, capture, simulator or performance experiment was executed. No cache hit, MSHR merge, occupancy, latency, reuse distance or throughput was inferred as measured.


Fixed source references (all at commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`):

- [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/mri-q/src/cuda/main.cu)
- [computeQ.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/mri-q/src/cuda/computeQ.cu)
- [file.cc](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/mri-q/src/cuda/file.cc)
- [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/mri-q/src/cuda/Makefile)
