# gaussian - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

FP32 Gaussian elimination without pivoting. A is row-major NxN, b is lengthN and m stores elimination multipliers. For pivot t, m[r,t]=A[r,t]/A[t,t], then A[r,c]-=m[r,t]*A[t,c] and b[r]-=m[r,t]*b[t]. GPU performs forward elimination; CPU performs triangular back substitution (`gaussian.cu:289-318,390-403`). Generated `-s64` constructs symmetric Toeplitz Aij=10*exp(-0.01*abs(i-j)) and bi=1 (`:65-89,132-144`). Other file/generated sizes are distinct data identities.

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/gaussian), suite Rodinia 3.1. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/gaussian` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/3.1/cuda/gaussian/` at this fixed commit. Historical capture-to-source/executable binding is separate.

`Makefile:10-13` passes `-DRD_WG_SIZE_0=128 -DRD_WG_SIZE_1=16`; this overrides source fallback512/4 in `gaussian.cu:22-40`. Thus the checked recipe and trace agree on128-thread Fan1 and16x16 Fan2. NVCC/GENCODE from common config supports compute70 among alternatives. No extra optimization flag is set here. The historical executable, compiler environment and actual binary bytes remain unbound.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [gaussian.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/gaussian/gaussian.cu) | `0f3b2154649e3b6bcf6053f92f5ff678bde77664` | `8b383f5c5149cb70c84720cac80f9115fe2cfd06907e321e589250fc21a5a5a4` |
| [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/gaussian/Makefile) | `87d3b64fb39d76ff915b5cebe1a880edcdd1e66b` | `0eb4fd138f98db36b95c6d7b3c8faabe9298c6ea1ebe071a2910332ef4df6442` |

## 3. Host calls and kernel order

CPU parses/generated matrix, zeroes m, copies m,A,b to device (`:128-165,274-278,332-341`). Sets fixed grid/block once from full N (`:343-359`), then for t=0..N-2 runs Fan1 -> thread synchronization -> Fan2 -> thread synchronization (`:364-369`). Copies m,A,b back then CPU BackSub and printing. At64 there are63 pivot steps and126 launches,2 unique definitions. Grid remains1 for Fan1 and4x4 for Fan2 even though bounds shrink; launches do not cover fewer CTAs merely because late threads return.

## 4. Detailed kernel implementation

Fan1 `:289-296` maps one thread to row r=128bx+tx+t+1, guards r<N, loads column t and pivot, writes m[r,t]. No shared memory/barrier/atomic. Fan2 `:303-318` maps xidx=16bx+tx to row and yidx=16by+ty to column; r=xidx+t+1,c=yidx+t. Bounds xidx<N-1-t,yidx<N-t; each live thread updates one A element, and only yidx0 updates b. Pivot row and multipliers are read repeatedly. Kernel boundaries enforce all multiplier writes before updates and all updates before the next pivot.

## 5. Thread and address formulas

With4B elements, Fan1 accesses m,A at B+4*(N*r+t): neighboring lanes delta4N=256B forN64. A full32 live-lane column instruction touches32 different128B lines/32 sectors (128B useful,1024B sector footprint), while all read pivot A[t,t] at same address. Next pivot changes row and column offsets, and reuses remaining matrix.

CUDA warp linearization for Fan2 is tx fastest: warp covers **16 rows and2 columns**, not32 adjacent columns. l->tx=l%16,ty=ty0+floor(l/16). `A` address=`BA+4*((t+1+16bx+tx)*N+t+16by+ty)`. Each halfwarp lane delta256B; the second half repeats the16 rows at column+1. With all32 lanes live and each pair within the same line/sector:16 lines/16sectors. If paired columns cross a boundary, counts can rise to32; exact start t and by determine it. m address is `Bm+4*(r*N+t)`, same between two column halfwarps:16 unique scalar addresses. Pivot-row loads have only2 unique addresses per warp, broadcast by16 lanes each. b branch has16 active x-lanes only when yidx0. CTA has8 warps: successive warp y pairs reuse m[r,t] and touch neighboring columns in each of16 rows; adjacent x-CTAs partition rows, adjacent y-CTAs reread the same multipliers and pivot row. No per-thread inner GPU loop; the time-changing pivot is a host loop.

## 6. Dataflow, locality, coalescing and concurrency

Independent A/m/pivot/b loads exist per update, followed by multiply-subtract and in-place stores. Fine-grained bounds reduce active lanes and parallel rows/columns as t grows; CPU barriers serialize the two kernels and pivots. The same small16KiB A plus16KiB m and256B b are reused over126 launches, but capacity fit alone does not imply hits across launches. Pivot broadcasts and strided column requests impose very different tag/sector demands; late steps cannot manufacture more useful CTAs through a larger cache.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-14`: `IDENTITY_FROZEN`; parameters `["_s_64"]`.
- Selected input digest `16f4c42373e4961eac6b16178237f1de2bbdf21d5e08bf669c4b6102bab2c6b3` is the registered identity, not automatically original-file SHA.
- Bundle `e777c8282c3720156144121bae4e8f794c189dcb837f247c03c1b98cb558ce35`.
- Trace entry `/root/workspace/assets/traces/bundles/e777c8282c3720156144121bae4e8f794c189dcb837f247c03c1b98cb558ce35/tree/kernelslist.g`.
- Existing scope `SOURCE_CONSISTENT_FULL_FORWARD_SUBSTITUTION`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: MEDIAN_SIZE_SOURCE_VERIFIED: E1 explicitly did not promote a primary Gaussian command. All five inputs are3.1 same Fan1/Fan2 ForwardSub algorithm; -f/-s only supply matrix/RHS. Trace copies establish N=4,16,64,208,256 and each has2*(N-1) alternating kernels. Median N64, deterministic source-generated matrix; no pivot/precision/algorithm flag changes. Not asserting matrix contents equivalent across sizes.

Header inventory: 126 kernel entries, 129 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z4Fan1PfS_ii` | `(1,1,1)` | `(128,1,1)` | 63 |
| `_Z4Fan2PfS_S_iii` | `(4,4,1)` | `(16,16,1)` | 63 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

SOURCE_VERIFIED: no pivoting/atomic/shared staging; forward GPU and backward CPU boundary;2 unique kernels,126 launches; source-build/trace blocks128 and16x16 match; strided row mapping in Fan2; shrinking active work with fixed grids. Freeze selects medianN64 independently of measured outcomes.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1: column loads may occupy many tags/physical lines for little useful sector data, whereas repeated pivot/multiplier addresses offer pending merges; test tag coverage and physical retention separately from low active parallelism. EP-L2: in-place A updates and pivot-step reuse suggest write/read residency and line conflicts, conditional on actual index mapping, write policy and scheduling. Existing runtime counters must establish resource blocking/latency; source fit/repetition does not establish MSHR occupancy or DRAM amplification.

## 10. Evidence and limits

Dimensions and deterministic generation contract are source/trace bound, but actual capture ELF and matrix bytes are not newly certified. Full63 pairs are a forward-substitution scope match, not certification of CPU BackSub output. Possible zero/poor pivots are an algorithmic limitation, not measured here. No new execution occurred.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
