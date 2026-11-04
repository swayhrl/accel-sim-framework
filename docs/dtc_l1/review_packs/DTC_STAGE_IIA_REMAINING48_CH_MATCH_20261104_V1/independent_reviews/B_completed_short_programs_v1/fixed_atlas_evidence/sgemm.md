# Parboil sgemm

## 1. Program and algorithm

Dense single precision product `C = alpha A B^T + beta C`, with column-major A, stored B^T, and C. Main supplies alpha1 and beta0; inputs are textual column-major matrices. This is Parboil register-tiled SGEMM, not PolyBench GEMM or a library SGEMM. `main.cu:45-68` requires three input names but reads only first and third; the second name is not a second data transfer.

## 2. Actual source authority and build information

Audited local root: `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/parboil/benchmarks/sgemm/src/cuda`. Fixed upstream repository `accel-sim/gpu-app-collection`, commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`. All nonhidden files in this program directory match upstream SHA256 byte-for-byte; see [source hashes](../../contributions/parboil/source_hashes.json). The enclosing local tree has no `.git`; `offline/manifest.lock` declares the commit, and independent content comparison supplies the stronger content evidence. Suite is Parboil; exact original Parboil release and historical capture source revision remain uncertified. `cuda_base` is a separate implementation and is not substituted here.

Build uses the program Makefile and `common/mk/cuda.mk:12-28,112-113`: configurable nvcc flags with default gencode targets 50/60/61/62/70/75. Historical effective command, compiler version, macro overrides, ELF SHA and PTX/SASS provenance are not recovered by reading these defaults. Trace headers record binary version 70, NVBit1.4 and tracer3; that is architecture metadata, not ELF identity.

## 3. Host calls and kernel sequence

`main.cu:60-91` reads A and B^T, allocates dA/dB/dC, uploads A and B^T, then calls `regtileSgemm` exactly once. `sgemm_kernel.cu:78-99` accepts N/T, constructs grid `(M/128,N/16)` and block `(16,8)` and launches `mysgemmNT`. Output copy/write is conditional on output filename. The size check prints an error but does not return; divisible sizes and K multiple8 are required for safe no-tail kernel accesses. dC is allocated without initialization; source expression reads C even with beta0 (`:74`), though compiler may remove that read. Actual SASS is needed to decide whether it issues.

## 4. Detailed kernel implementation

`sgemm_kernel.cu:46-75`: 128 threads compute 128 rows by16 columns per CTA. Each owns16 register accumulators `c[16]`. CTA cooperatively stages an8x16 B tile in512B shared memory; two CTA barriers per K tile protect consumption and overwrite. Each thread loads one A scalar per inner j and applies it to16 accumulators. There are no explicit global atomics, texture loads or inter-CTA synchronization. The conceptual register array is not proof that no local spill occurred.

## 5. Thread and address formulas

Let x=tx in[0,15], y=ty in[0,7], u=16y+x, M=lda=ldc, N=ldb. CTA `(bx,by)` owns row `m=128bx+u`; B staging column `n=16by+x`. For K tile i=0,8,..., `Baddr=PB+4[n+(i+y)N]`; inner j=0..7 `Aaddr=PA+4[m+(i+j)M]`; output q=0..15 `Caddr=PC+4[m+(16by+q)M]`. These are direct expansions of `:56-74`.

Warp linear lane l has x=l%16, y=2w+floor(l/16). A and each C instruction have lane delta4B across all32 lanes; aligned warp spans128B = one128B line/four32B sectors. Unaligned spans can cross two lines/five sectors. B has two16-lane contiguous64B runs separated by `4N-60`B at the half-warp boundary; each aligned run is two32B sectors, and one128B line may cover each run depending on N and base alignment. Consecutive inner j for one thread moves A by4M bytes, not4B. Consecutive K tiles move B by32N bytes. Consecutive C q moves by4M bytes. Other warps access disjoint consecutive A row strips; B staging repeats columns for different y rows. Different by CTAs reread A; different bx CTAs reread B. Those are reuse opportunities, not cache hit counts.

## 6. Dataflow, locality, merging and concurrency

Shared B makes its128 loads serve all128 rows. A scalar is reused16 times in a thread. Four warps per CTA and independent CTA tiles supply potential memory concurrency; within a thread the16 accumulators form separate arithmetic chains but each depends on current A/B operands. Barriers bound K tile progress. At observed grid8x66, 528 CTAs exist and geometry corresponds to M1024,N1056 under this implementation; K and input content are not encoded by grid. No exact resident CTA count follows from source. Potential same-line pending overlap depends on timing, not just repeated A/B footprints.

## 7. Frozen input and trace binding

DTC frozen selection is `P42-36` from `DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json` at atlas base `3b28d3064`. Logical input digest `ffc8a89493c8a21151320d1cfdaccbfca2706eb1c395fcb58e94a1b01e6ea453`; bundle `3745de69edb9414642035192656ae7890477988814781a0150cb82ed2516e90b`. Recorded parameter encoding: `_i___data_medium_input_matrix1_txt___data_medium_input_matrix2t_txt___data_medium_input_matrix2t_txt__o_matrix3_txt`. This digest is the registered identity; it is not newly certified SHA256 of original input bytes.

Only small `kernelslist.g` and first20 header lines per listed trace were read. Ordered header evidence is in [trace_metadata.json](../../contributions/parboil/trace_metadata.json); the frozen file inventories and content hashes remain in the original freeze. 1 launches are listed:

| Unique trace kernel | Grid | Block | Launches |
|---|---|---|---|
| `_Z9mysgemmNTPKfiS0_iPfiiff` | `(8,66,1)` | `(16,8,1)` | 1 |

Frozen scope is `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`. No new certification of capture-time executable or original input bytes. Matching names and dimensions support an implementation correspondence, not proof of full application completion, exact arguments, data values, or native correctness. No source, binary, input, trace or accepted performance evidence was changed.

## 8. Source-provable architecture features

Regular dense reads, column-major lane-contiguous A/C, split B half-warp loads, a512B shared staging tile, register reuse, strided per-thread K progression, no source global atomic. This is distinct from an untiled naive matrix multiply. Default `TILE_TB_HEIGHT=8` rather than stale prose describing4 (`sgemm_kernel.cu:25-43`).

## 9. DTC-L1 / EP-L2 hypotheses requiring validation

DTC-L1: test whether cross-CTA A/B reuse reaches ordinary L1, whether pending accesses coalesce at the same128B line, and whether Tag/PIB pressure limits otherwise independent tile loads. Hash conflicts require actual address/bank mapping and issue timing. EP-L2: compare A sharing across by and B sharing across bx, output write traffic and cache retention between tiles. Candidate source reuse does not establish L2 residency or queue pressure. Same-name EP SGEMM must match tile constants, input SHA, ELF, launch geometry, ROI and trace version before pooling.

## 10. Evidence and limitations

`SOURCE_VERIFIED=true` for the fixed content and source behavior below; `INPUT_BOUND=registered_identity_only`; `BINARY_BOUND=false`; `TRACE_SCOPE_BOUND=registered_sequence_only`; `RUNTIME_MEASURED=false` in this audit; `UNRESOLVED=true` for historical content/ELF/full-application linkage. These are independent dimensions. No GPU, native benchmark, capture, simulator or performance experiment was executed. No cache hit, MSHR merge, occupancy, latency, reuse distance or throughput was inferred as measured.

Every source reference below uses fixed commit `dad09cb0487845edc7524ded814c6cde9f0ef6a1`; line ranges in the text refer to these exact files.

- [main.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sgemm/src/cuda/main.cu)
- [sgemm_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sgemm/src/cuda/sgemm_kernel.cu)
- [io.cc](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sgemm/src/cuda/io.cc)
- [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/parboil/benchmarks/sgemm/src/cuda/Makefile)

Historical capture binary and original input linkage are unresolved even though fixed source contents and launch geometry correspond.
