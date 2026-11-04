# lud - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

In-place FP32 blocked LU without pivoting, tileB16. Matrix lower triangle stores L (implicit unit diagonal); upper triangle stores U. CPU generates/reads matrix and optionally retains a duplicate for `lud_verify`; GPU diagonal factorization -> perimeter triangular solves -> internal Schur update. Selected generation is Toeplitz Aij=10*exp(-0.001*abs(i-j)) (`common/common.c:210-240`); the unused random-generator helper is not this selected input. The verifier reconstructs L*U and prints differences above0.0001 (`common/common.c:140-186`); its presence alone is not a pass/fail exit-status certificate. The whole matrix is copied back before CPU verification (`cuda/lud.cu:98-153`). Selected generatedN256 is separate from2.0-ftN64 variants.

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lud), suite Rodinia 3.1. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/lud` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/3.1/cuda/lud/` at this fixed commit. Historical capture-to-source/executable binding is separate.

`cuda/Makefile:17-22,37-50` uses NVCC `-O3 -use_fast_math`, `GPU_TIMER` and overridable GENCODE. `BLOCK_SIZE` resolves RD_WG_SIZE macros or fallback16 (`lud_kernel.cu:4-12`); trace confirms16. Host filename is `lud.cu` despite stale CCFILES references atMakefile35; actual object pattern%.cu and objects list determine recipe. Native `-v` is a CPU verifier path, not a newly executed verdict.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [cuda/lud.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lud/cuda/lud.cu) | `37f2b937b86a37f953d7111957818e9aa2023251` | `ef26e175c582210a7b55bba1ed9ea45cce4c8ba2ede17e89b0f4bac9aa7b6757` |
| [cuda/lud_kernel.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lud/cuda/lud_kernel.cu) | `801367aae3018a13a088d7fe0c1125161b164cba` | `fe3d0a5f06c82947f54cbf6fd9a75342b61263808a1587ead929fc3f8763fdc0` |
| [cuda/Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lud/cuda/Makefile) | `7d451ce686c22645d5cc87beae9a16b01f3a1874` | `22e98174ccdd96f0fcff17bdde2384c28b5de8868f1e985790cb3a7bbf5dad41` |
| [common/common.c](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/lud/common/common.c) | `c7c95996c5ddc2169c072d32f41e67b7a348c7b2` | `8a6cca89c03be97a690a5fc0a657810dabd451e86c34bf97857785a36eb28e5c` |

## 3. Host calls and kernel order

For offset o=0,16,...,224: diagonal<<<1,16>>>; perimeter<<<(N-o)/16-1,32>>>; internal<<<(k,k),(16,16)>>> with k=(N-o)/16-1. Then final diagonal at240 (`lud_kernel.cu:193-205`). Sequence has16 diagonal,15 perimeter and15 internal launches=46. The k grids descend15..1; ordinary stream order supplies global dependency barriers. CPU launches one cuda routine, copies one262144B matrix in/out, optional verifier follows.

## 4. Detailed kernel implementation

Diagonal `:15-55`:16 threads load one column each of16x16 shared shadow, barrier, serial i=0..14 with active-thread conditions and two barriers per pivot; writes rows1..15 back. Perimeter `:57-165`:32 threads split16 row-solve and16 column-solve roles, cooperatively load diagonal tile halves, their own row/column tile into3 shared16x16 arrays, synchronize, perform dependent triangular loops, synchronize, write solved tiles. Internal `:167-190`:16x16CTA cooperatively loads peri_row/peri_col shared tiles, barrier, each thread sums16 products and subtracts from its own global trailing element. No atomic/texture operations. The `.old` source is not part of selected build.

## 5. Thread and address formulas

Matrix address M(r,c)=BM+4*(r*N+c), N256 row stride1024B. Diagonal load loop i=`M(o+i,o+tx)`: lane+4B among16 lanes, loop+1024B, contiguous64B halfwarp (2sectors;1line when64B-aligned). Perimeter each role similarly handles16 consecutive columns; halfwarps may access distinct tiles/rows so one cannot treat the32-thread CTA as one contiguous128B stream. Repeated diagonal loads across k perimeter CTAs read identical16x16=1024B tile; row and column perimeter tiles are different objects.

Internal thread tx,ty at tile(rx=o+16*(by+1),cx=o+16*(bx+1)) reads `M(o+ty,cx+tx)` and `M(rx+ty,o+tx)`; output=`M(rx+ty,cx+tx)`. Warp has two16-lane rows: two64B spans, generally2 distinct128B lines and4sectors at this selected alignment. Shared inner product=`peri_col[ty][i]*peri_row[i][tx]`; as tx varies column operand is broadcast, row operand contiguous. Same thread's loop i increments shared references by4B in column tile and64B in row tile; no repeated global inner-product loads are mandated. Neighboring internal CTAs along x reread identical peri_col tile, along y identical peri_row tile. Later host offsets revisit/update surviving trailing tiles. Boundary scalar store footprints count active lanes and row alignment, not256B useful transfer simply because block256 exists.

## 6. Dataflow, locality, coalescing and concurrency

High shared reuse within internal CTAs and explicit stage producer/consumer dependencies. At first trailing update225 CTAs can run; last has1, diagonal always1 and16 active lanes. Perimeter grid shrinks15..1. This concurrency change is algorithmic. Internal loads of2 tiles are independent; outputs wait on shared barrier and16-term accumulation; diagonal/perimeter triangular solves impose sequential critical paths. Cross-CTA perimeter-tile reuse is potential cache reuse only. Source allocations/fit do not define occupancy or pending lifetime.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-23`: `IDENTITY_FROZEN`; parameters `["_s_256__v"]`.
- Selected input digest `b33381cf25d443599aea5253936c13914acb0a2e7c22478496025c5234aef1f8` is the registered identity, not automatically original-file SHA.
- Bundle `07e439dd141d4465b96a46e9ca7031d557b99743eaba5e8c6584e0543f15a7df`.
- Trace entry `/root/workspace/assets/traces/bundles/07e439dd141d4465b96a46e9ca7031d557b99743eaba5e8c6584e0543f15a7df/tree/kernelslist.g`.
- Existing scope `SOURCE_CONSISTENT_FULL_BLOCKED_LU`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: PRIOR_REFERENCE_SELECTED: Historical pre-current-performance E1 primary is Rodinia3.1 generated -s256 -v. Prefer this identified reference, not pooled median across2.0-ft/3.1 implementations. Trace262144-byte matrix and16 diagonal+15perimeter+15internal kernels match full256 block16 LU. Retain512 and both2.0-ft64 captures as distinct alternatives.

Header inventory: 46 kernel entries, 47 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z12lud_diagonalPfii` | `(1,1,1)` | `(16,1,1)` | 16 |
| `_Z13lud_perimeterPfii` | `(15,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(15,15,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(14,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(14,14,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(13,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(13,13,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(12,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(12,12,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(11,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(11,11,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(10,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(10,10,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(9,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(9,9,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(8,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(8,8,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(7,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(7,7,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(6,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(6,6,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(5,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(5,5,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(4,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(4,4,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(3,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(3,3,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(2,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(2,2,1)` | `(16,16,1)` | 1 |
| `_Z13lud_perimeterPfii` | `(1,1,1)` | `(32,1,1)` | 1 |
| `_Z12lud_internalPfii` | `(1,1,1)` | `(16,16,1)` | 1 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

SOURCE_VERIFIED:46 launches/3 definitions, all selected grids source-consistent; in-place reads/writes; CTA shared tiling and synchronous LU phases; cross-CTA row/column reuse; small-grid diagonal phases. SOURCE/INPUT/TRACE structure does not substitute for actual CPU `-v` success.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1: internal stage may share pending row/column tile lines while diagonal stage lacks parallelism; separate physical-line retention of reused perimeter tiles from searchable-tag demand and PIB waiters. EP-L2: repeated reads and dirty writes of overlapping matrix stages may favor residency/write buffering, but replacement/hash conflicts need measured address mapping and timing. No direct inference of speedup, MSHR merges or L2 queue occupancy from tiling.

## 10. Evidence and limits

`-s256 -v` fixes generated-input contract, not the exact historical library/build or accepted native result. Matrix generation and verifier source are inventoried, existing trace46 scope is structurally complete forB16,N256. Source/ELF and numerical correctness remain separate. No2.0-ft trace is merged; no new run performed.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
