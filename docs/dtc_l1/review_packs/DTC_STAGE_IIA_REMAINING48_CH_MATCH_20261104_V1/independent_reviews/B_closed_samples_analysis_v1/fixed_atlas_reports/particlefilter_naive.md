# particlefilter_naive - source and behavior audit

This report is a read-only source/metadata audit. No GPU, native, capture or simulator execution was performed.

## 1. Program and algorithm

Sequential Monte Carlo tracking of a synthetic moving disk. CPU constructs an `int` video in frame-interleaved layout `I[x*Y*F+y*F+k]`, radius5 disk offsets, random motion, likelihood, normalized weights, location estimate and CDF. Only resampling is offloaded. CPU `calcLikelihoodSum` computes sum over disk samples `((I-100)^2-(I-228)^2)/50` (`ex_particle_CUDA_naive_seq.cu:367-372`). Therefore random video accesses in this implementation are **CPU accesses**, not evidence of GPU irregular image reads. The CPU loop is k=1..F-1 (`:473-552`).

## 2. Actual source authority and build

Authority: [accel-sim/gpu-app-collection@dad09cb0487845edc7524ded814c6cde9f0ef6a1](https://github.com/accel-sim/gpu-app-collection/tree/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/particlefilter), suite Rodinia 3.1. Local recovered root `/root/workspace/offline-sim-v1/cache/apps/gpu-app-collection/src/cuda/rodinia/3.1/cuda/particlefilter` has no Git metadata; exact file bytes match fixed upstream Git blobs as recorded in [SOURCE_BLOB_VERIFICATION.json](../../SOURCE_BLOB_VERIFICATION.json). Path:line citations below are relative to `src/cuda/rodinia/3.1/cuda/particlefilter/` at this fixed commit. Historical capture-to-source/executable binding is separate.

`Makefile:5,11-15` compiles the naive and float sources separately with NVCC, `-g -lm -O3 -use_fast_math` and externally overridable `GENCODE_*` targets. `threads_per_block=128` is source line32. Despite the name of the companion target, this selected kernel operates on **double**, not float. The common make configuration defines compute35 through75 including70; the retained trace header says binary version70. Actual toolkit version, effective environment/flags, ELF/PTX/SASS hash, and capture executable remain unbound.

Read source identity inventory (source blobs/SHA256 are not binary hashes):

| File | Git blob | SHA256 |
| --- | --- | --- |
| [ex_particle_CUDA_naive_seq.cu](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/particlefilter/ex_particle_CUDA_naive_seq.cu) | `b3d14ce9899fc20282b7dc75142f05e180ded6c9` | `927a58af8122dced9e336d1850f5a749874b76b0c4bba1f5e0cf3ef596049680` |
| [Makefile](https://github.com/accel-sim/gpu-app-collection/blob/dad09cb0487845edc7524ded814c6cde9f0ef6a1/src/cuda/rodinia/3.1/cuda/particlefilter/Makefile) | `c7cccf04b4bb74797f96d3a2eef9b1981528231f` | `3c97a48b2c0b551f60ac45491da2b121cdfce34172152355c1b05ca528618f11` |

## 3. Host calls and kernel order

`main:612+` parses `-x -y -z -np`, allocates/seeds synthetic data and invokes `particleFilter`. For every frame k=1..9: CPU motion and likelihood (`:480-503`), exponential weight update/sum/normalization (`:508-520`), expectation (`:527-535`), cumulative sum and systematic-resampling thresholds (`:543-551`); six H2D copies of X,Y,xj,yj,CDF,u (`:557-562`); **one** `kernel<<<ceil(P/128),128>>>` (`:565-568`); device synchronization; two D2H copies (`:569-573`); CPU replaces X,Y by resampled coordinates and resets weights (`:581-585`). Total expected9 launches, one unique global definition. `findIndexSeq`/`findIndexBin` are device helpers present at58/74 but are not called by the launched body. They must not be counted as extra kernels or used to describe its search algorithm.

## 4. Detailed kernel implementation

`kernel:113-134`: i=128*blockIdx.x+threadIdx.x; inactive i>=P does nothing. Each active thread scans x=0..P-1 from the **beginning** until CDF[x]>=u[i], falls back to P-1, gathers X[index],Y[index], and writes xj[i],yj[i]. There is no shared allocation, CTA barrier, GPU atomic or reduction. Search exits diverge by threshold. The result coordinate index is data dependent; the CDF load index is the loop counter. The compiler may hoist/reuse u[i] or scalar values, so source references are not an instruction count.

## 5. Thread and address formulas

Let lane l have i=i0+l within a warp, each double8B. `u[i]`, xj/yj stores have addresses B+8(i0+l), lane delta8B, full aligned warp256B = **2 lines/8 sectors**. At a common active loop iteration x, every participating lane loads `CDF+x*8`: lane delta0, one double spans one32B sector unless misaligned across a boundary; x->x+1 delta8B. Adjacent16 CDF doubles share a128B line, four share32B sector. Different warps/CTAs restart the same prefix; theoretical repeated-address overlap is high. For gathers addresses are `BX+8*j_l`, `BY+8*j_l`; no constant lane delta. If weights form a valid monotone CDF and u increases with i, j_l is nondecreasing, but duplicates/gaps depend on data. Distinct-sector count is `|{floor((B+8*j_l)/32)}|` including any crossing byte; bounds1..32 sectors for aligned doubles, not an asserted random distribution. Every thread scans at most P doubles, so P=1000 gives a maximum8000B CDF footprint (63 aligned128B lines;250 sectors), not 1000 independent lines. CTA b covers i=128b..128b+127, four warps with adjacent output ranges; next CTA output stride1024B. No inter-thread inner-loop stride exists for the final gather.

## 6. Dataflow, locality, coalescing and concurrency

CPU supplies a new CDF and coordinate vectors every frame. Resampling outputs are consumed by CPU and become input to the next frame. Simultaneous static scan prefixes offer same-address and cross-warp/CTA reuse; independent thresholds and coordinates can expose multiple requests, but each thread's next comparison controls exit and final gather. Eight CTAs (last104 active threads) bound grid-level parallelism. No source basis establishes SM mapping, pending request lifetime, occupancy, merge count or hit rate. CPU/device round trips separate frames and affect cache residency; persistent CDF hits across them cannot be assumed.

## 7. Frozen input and trace binding

Freeze: `docs/dtc_l1/review_packs/DTC_PAPER42_HASH_REVIEW_20261027_V1/REPRESENTATIVE_FREEZE.json`, framework atlas base `3b28d3064`.

- Slot `P42-31`: `IDENTITY_FROZEN`; parameters `["_x_128__y_128__z_10__np_1000"]`.
- Selected input digest `3f85d1878aba9f04916ec52cc1162b37673f92a88be07c4db815240c9564755e` is the registered identity, not automatically original-file SHA.
- Bundle `edba399b6598403ce810930789172452c38219709a99d66f634dbe7df4284139`.
- Trace entry `/root/workspace/assets/traces/bundles/edba399b6598403ce810930789172452c38219709a99d66f634dbe7df4284139/tree/kernelslist.g`.
- Existing scope `REGISTERED_TRACE_COMPLETE_FULL_APPLICATION_UNCERTIFIED`.
- Existing freeze exact capture executable/original input linkage newly certified: **false**.

Selection rationale retained: Only ordinary trace identity for this program in the72-input matrix; no outcome-dependent replacement. Keep its recorded source/command/content identity. Exact capture-time executable/input-content and full-application provenance are not newly certified.

Header inventory: 9 kernel entries, 63 total kernelslist events. Only metadata headers were read, not instruction bodies. Every observed header reports binary version70.

| Kernel metadata | Grid | Block | Entries |
| --- | --- | --- | --- |
| `_Z6kernelPdS_S_S_S_S_i` | `(8,1,1)` | `(128,1,1)` | 9 |

Independent evidence dimensions:

| Dimension | State and limit |
| --- | --- |
| SOURCE_VERIFIED | Read files match fixed upstream blobs; selected host/body formulas audited. |
| INPUT_BOUND | Registered command/dimensions and bundle identity bound; capture-time data/generator state not newly certified. |
| BINARY_BOUND | UNRESOLVED: target70 is not ELF/PTX/SASS SHA linkage. |
| TRACE_SCOPE_BOUND | Names/counts/grids checked against source with per-program limits; full instruction-body/ROI/executable completeness not newly certified. |
| RUNTIME_MEASURED | No new measurement; no queue/latency/cache-hit inference promoted. |

## 8. Verifiable architectural features

SOURCE_VERIFIED: GPU-only resampling; linear shared-prefix CDF scan; FP64 coordinate vectors; one thread/particle; contiguous outputs; conditional gather;9 launches at selected F10; no GPU atomic/shared reduction. INPUT_BOUND applies to selected dimensions/trace identity, not random realized video/seed. The float companion moves likelihood and reductions to GPU and uses unsigned-byte video, so identical command strings do not establish source/data equivalence.

## 9. DTC-L1 / EP-L2 hypotheses awaiting validation

DTC-L1 hypothesis: scan prefixes may produce same-line pending requests and PIB waiters whose measured merge/retention behavior depends on request timing; compare searchable-tag pressure against physical-line occupancy separately. EP-L2 hypothesis: repeated CDF prefix loads plus sparse coordinate gathers may have very different sector traffic and downstream response lifetimes. Validate using existing identity-bound event evidence only; no causal speedup or DRAM multiplication follows from source repetition. Treat CPU likelihood as outside GPU cache hypotheses.

## 10. Evidence and limits

Exact seed and generated video/CDF bytes are not retained in the freeze. Main uses time-based seed initialization; runtime/library/fast-math effects and invalid numeric CDFs could change exits. One registered trace can match9 resampling launches without proving full numerical tracking correctness. No new execution or measurement occurred.

Static repeated references are not measured cache hits, MSHR merges, reuse distances or DRAM repeats. 128B-line/32B-sector counts describe ideal address unions under stated alignment/active-lane conditions. Source facts, structural inference and runtime measurement remain separate. [Header inventory](../../contributions/rodinia/trace_headers.json) and [source manifest](../../contributions/rodinia/source_manifest.json) preserve audit inputs.
