# Stage II-A Agent B: kernel hypotheses and matched existing observations

Status: PLANNING_AND_READONLY_CPU_VALIDATION_ONLY. No simulator, GPU workload, new trace, scientific registration, original-result rewrite, owner change, or paper edit.

Existing Stage-II rules consumed at `5ba029e60c2e7523b193043b345990c7ae52531c`; their earlier330/335 snapshot is retained as history. This report uses final331/336, as proved by [authority readback](PHASE_I_FINAL_AUTHORITY_READBACK.json).

Authority: Atlas V1R1 `47a097aad4406893a07f8d230e1e0a850609bf39`; phase-I final `361fa6fa0700825bb9cda43e25b9fd1f60e0b262`. The English LaTeX v0.23 manuscript remains the sole user-confirmed manuscript.

This report adds phase-specific discriminating questions to the existing Atlas instead of repeating its general algorithm descriptions. The 11 programs and 25 kernel identities were fixed by the user, not selected by speedup.

## Evidence boundaries

- **S / fixed candidate source**: exact source formulas and dependencies, identified through Atlas report commit, source file/line and SHA manifests. Candidate source is not capture-producer certification; the cross-version label is UNKNOWN_CAPTURE_SOURCE_BINDING.
- **T / existing trace metadata**: frozen full input digest, registered kernelslist, names/order/grid/header and recorded HtoD sizes. No new body replay, original numeric-input certification, or producer ELF binding.
- **R / existing runtime measurement**: strict original CH/DH cycles and 2026-10-29 counter projection, with all 44 selected counter RESULT SHA values checked against final original slots. Named IR/R2 alternatives are disclosed separately and never substituted.
- **H / hypothesis**: potential reuse/concurrency and candidate bottlenecks. Static address overlap does not establish actual L1 hit, MSHR merge, live-miss overlap, latency or causality.

Final background REPORT hardware_counters is NOT_COLLECTED. This report explicitly uses a separate, older identity-matched L projection; it does not turn final REPORT missing values into zero. Per-kernel cycles, queue occupancy and request latency are unavailable in that projection. Every phase row has null for those unavailable measurements.

## Matched original whole-input measurements

CH F128/F256 have not run. Every CH-relative F effect and CH/DH F comparison remains missing. Original331/350 and named336/350 are distinct populations. The following is a selected evidence table, not a suite GM. DH speedup=P0/F (higher is better).

| Program | CH P0 cycles | DH P0 | DH F128 | DH F256 | DH P0/F128 | DH P0/F256 |
|---|---:|---:|---:|---:|---:|---:|
| convolutionSeparable | 825151 | 800572 | 674364 | 562886 | 1.187151 | 1.422263 |
| scan | 6710840 | 6648993 | 5748280 | 5179817 | 1.156693 | 1.283635 |
| hybridsort | 18575969 | 18563916 | MISSING | 16370955 | MISSING | 1.133954 |
| 2DCONV | 1548909 | 462740 | 437573 | 429253 | 1.057515 | 1.078012 |
| ATAX | 28428842 | 31880220 | 31894637 | 31321955 | 0.999548 | 1.017823 |
| MVT | 26581175 | 34687540 | 35332620 | 35093446 | 0.981743 | 0.988434 |
| BICG | 26298698 | 28685812 | 29210480 | 28883488 | 0.982038 | 0.993156 |
| vectorAdd | 220803 | 217305 | 213053 | 236217 | 1.019957 | 0.919938 |
| GEMM | 1395216 | 826089 | 826089 | 826089 | 1.000000 | 1.000000 |
| 3MM | 4191465 | 2402871 | 2402871 | 2402871 | 1.000000 | 1.000000 |
| particlefilter_naive | 511136 | 384601 | 384601 | 384601 | 1.000000 | 1.000000 |

hybridsort original F128 is an archived negative. Any IR acceptance is a separate named role; it does not fill this table. ATAX/BICG/MVT P0 are previously matched, authorized no-new-start references. There are no CM/DM Stage-I L2-F runs in this current matrix; old CM/DM Hash data and EP/PQ/PS results must remain separately named with their own model receipts.

## Per-kernel discriminating matrix

The complete [machine-readable matrix](KERNEL_HYPOTHESIS_MATRIX.json) binds source report SHA, fixed source line, phase ID, exact capture occurrence ordinals, and runtime gaps. Occurrence ordinals are source/header-map interpretation, not measured time intervals. Counts repeated in source rows must not be summed as independent program launch totals.

| Program / kernel | Address and geometry (S) | Dependency / supply (S, T) | Hypothesis and decisive observation (H) |
|---|---|---|---|
| convolutionSeparable / _Z21convolutionRowsKernelPfS_iii | Rows x=128bx-16+tx+16i,y=4by+ty; block16x4; two64B half-warps per warp; CTA128x4 output,640float interior load/512float output. | 18432 CTAs; shared2560B and CTA barrier; main/halo input loads precede shared17-tap reduction. | F benefit may occur in input tile admission/return service rather than tap arithmetic; horizontal CTA halo overlap is only potential cross-CTA reuse. Need: Rows-only cycles and accepted/global/texture/constant requests; outstanding/mrq occupancy and end-to-end request lifetime. |
| convolutionSeparable / _Z24convolutionColumnsKernelPfS_iii | Columns x=16bx+tx,y=64by-8+ty+8i; block16x8; lane15->16 crosses rows; not a W-strided full warp. Shared pitch81; CTA16x64 output. | 9216 CTAs; shared5184B; preceding row kernel produces B; spatial CTA halo overlap16rows. | Compare vertical and horizontal staging, without attributing whole-program1.422x to either phase. Need: Columns-only service/queue occupancy, B write/read traffic, phase boundaries and total-vs-delta counter semantics. |
| scan / _Z19scanExclusiveSharedP5uint4S0_j | uint4 Src/Dst+16*(256b+t);1024elements/CTA. Vector opcode vs scalarized components unbound. | 6656 CTAs/launch, shared2048B; register/warp/block scan dependency. 17 first-pass launches in selected sweep. | Bulk first-pass admission may dominate benefit; shared scan dependencies can limit extra outstanding requests. Need: Per-launch cycles grouped by arrayLength, vector memory opcodes, read/write sectors, issue/return occupancy. |
| scan / _Z20scanExclusiveShared2PjS_S_jj | Chunk-last Src/Dst+4*(1023+1024p),4096B lane stride; buffer4p contiguous. | 26 CTAs per middle launch;8 occurrences; global phase dependency and shared scan. | Sparse gather has large static tag footprint but small grid; cannot infer that it dominates the33-launch total. Need: 8 matched middle-kernel cycle deltas, per-request sectors and MSHR merge admission/fail events. |
| scan / _Z13uniformUpdateP5uint4Pj | uint4 D+16*(256b+t); only thread0 loads B+4b then shared broadcast. | 6656 CTAs, shared4B+barrier;8 occurrences; chunk totals required before update. | Offset sharing and Dst read-modify-write may react differently to shared-credit/window change. Need: Uniform-only cycles, B requests, Dst reads/writes, completion queues and per-phase occupancy. |
| hybridsort / histogram1024Kernel | Data4*(96b+t+6144q);64x96 threads. Shared3x1024 bins; perCTA1024 global atomicAdd outputs. | Source65536 global atomicAdd/sort is static, not contention count; threadTag retry depends on values. | Atomics/shared retry can constrain benefit independently of ordinary-load L2 pressure. Need: Atomic-vs-ordinary request path, atomics issued/serialized, per-phase cycles; texture/constant separated. |
| hybridsort / bucketcount | Input/encoded-rank4*(32b+t+32768q),1024x32threads; texture pivot search starts511. | Shared1024 counters and volatile retry;128 iterations/thread; output rank<<10\|bucket. | Pivot reuse/serial routing and ordinary rank writes need separate timing classification. Need: Texture read sectors, retry iterations if observable, ordinary loads/stores and phase cycles. |
| hybridsort / bucketprefixoffset | Prefix4*(1024b+bucket), lane4B but same-thread slab-step4096B. | 8x128threads, one thread/bucket serially scans1024 slabs; waits for counts and CPU boundary later. | Prefix has limited grid and long serial work; more downstream capacity may offer limited overlap. Need: Prefix-only cycles, actual activeCTA/SM, outstanding reads and latency distribution. |
| hybridsort / bucketsort | Scatter=4*(l_offsets[bucket]+prefix[b*1024+bucket]+rank); no constant lane stride. | 1024x32threads; shares pivot/totals; stores depend on rank/prefix. | Irregular store destinations could respond to credits differently from read-side merges. Need: Store sectors/write-allocate/DRAM writes, real destination sector union, queues and phase cycles. |
| hybridsort / mergeSortFirst | float4 texture and store16tid; four values sorted in registers. | 4098x256threads per occurrence; fixed compare network, no shared merge tile. | Regular initial stage is useful control against later strided merge passes. Need: Texture/global path counts and first-stage cycles, actual emitted record load width. |
| hybridsort / mergeSortPass | Pass lanes initially16*nrElems apart, perthread conditional advance16B; output sequential perthread. nrElems>=8 may span32 distinct lines/warp. | 11 passes/sort; grids2585,1295,650,325,163,84,45,25,15,10,8; finalblock128 else208. Divergence, small late grid and buffer dependency. | Benefit may concentrate in early strided/high-supply passes or late pass latency; no per-pass evidence yet decides. Need: Perpass cycles+run size/geometry, texture/request path, issued sectors, queue wait/service and active warps. |
| hybridsort / mergepack | Pack reads4*(4*constStartAddr[d]+nullElems[d]+idx), writes4*(finalStartAddr[d]+idx). | Grid17x1024/block256; waits last merge, strips padding; lane4B within division. | Final regular stream is another control; padding can change alignment across division boundary. Need: Pack-only read/write sectors, cycles and division-boundary active mask. |
| 2DCONV / _Z20Convolution2D_kernelPfS_ | A4*((i+di)*4096+j0+lane+dj),9taps; output4*(i*4096+j). Block32x8,grid128x512. | 65536 CTAs; no shared/barrier/atomic; neighbor warp/CTA inputs overlap. | Static9-tap reuse can explain opportunity, not hit/merge; current F response must be checked against runtime request timing. Need: One-kernel cycle/traffic linkage exists; add actual tag/MSHR/PIB and service-lifetime attribution if approved. |
| ATAX / _Z12atax_kernel1PfS_S_ | A4*(q*4096+t): lane16384B,loop4B; x4t uniform; tmp4q output. | 16 CTAs/128 warps; recurrence4096; independent load addresses do not prove outstanding overlap. | Poor fixed-t lane coalescing coexists with intra-thread row-line reuse; tag retention and limited CTA supply are competing constraints. Need: Phase1 actual L1/L2 sectors, tag failures, live misses, PIB/return stalls and perkernel cycles. |
| ATAX / _Z12atax_kernel2PfS_S_ | A4*(t*4096+q): lane4B,loop16384B; tmp4t uniform; y4q output. | 16 CTAs; true tmp producer-consumer edge plus default-stream/synchronize boundary. | Coalesced phase2 and tmp sharing need separate attribution from phase1; initialization/producer provenance remains capture-unbound. Need: Phase2 delta counters, tmp request overlap, emitted accumulator load/store pattern. |
| MVT / _Z11mvt_kernel1PfS_S_ | A4*(q*4096+t):lane16384B,loop4B; y1 uniform; x1 output. | 16 CTAs; serial4096 accumulation; first phase no software shared tiling. | Test phase1 row-line retention against limited work supply; no whole-suite diagnosis from geometry alone. Need: Perkernel live-miss/request lifetime, tag failures, queues and activeCTA/SM. |
| MVT / _Z11mvt_kernel2PfS_S_ | A4*(t*4096+q):lane4B,loop16384B; y2 uniform; x2 output. | 16 CTAs; algebraically independent of x1 yet default-stream serialized. | Order/carryover of64MiB A may affect cache state but is not measured persistence. Need: Separate phase2 cycles and sector/hit/miss deltas; source-to-emitted accumulator traffic. |
| BICG / _Z12bicg_kernel1PfS_S_ | s=A^T*r: A4*(t*4096+q),lane4B;loop16384B. | 16 CTAs;4096 recurrence; explicit zero s; coalesced phase first. | Reverse order from ATAX/MVT is a natural phase-order control, not a causal intervention. Need: Phase1 cycles, return service/PIB, actual vector merging and carried cache state. |
| BICG / _Z12bicg_kernel2PfS_S_ | q=A*p: A4*(q*4096+t),lane16384B;loop4B. | 16 CTAs; explicit zero q; synchronized after coalesced first product; no solver iterations. | Late scattered row accesses may expose tag/reuse constraints; previous Tag/PIB work does not prove current bottleneck. Need: Phase2 tag allocation vs MSHR merge/capacity vs downstream credit blocking, with exact model identity. |
| vectorAdd / _Z6VecAddPKfS0_Pfi | A/B/C4i, i=256b+t;lane4B;N6000000,grid23438/block256,4inactive final warps. | Two independent input reads then add/store; no intended cross-CTA reuse, shared/atomic/barrier. | F256 negative with unchanged read traffic and fewer failures disproves a simple fewer-stalls=>faster narrative; altered service/order remains hypothesis. Need: Per-request wait/service distribution, write/return pressure, SM issue and endpoint drain; latency unavailable in old projection. |
| GEMM / _Z11gemm_kernelPfS_S_ | A4*(i*512+k) broadcast;B4*(k*512+j0+lane) contiguous;C4*(i*512+j),loop512. | 1024 CTAs/8192warps,8CTAwarps reuse B source lines;512 output recurrence. | Exact zero F response and projected0 DRAM reads fit weak DRAMwindow pressure; neither proves compute-bound nor cache-hit cause. Need: Existing printed0 counters require scope/initial cache checks; source shared reuse is absent; counters for tag/completion/issue remain needed. |
| 3MM / _Z11mm3_kernel1PfS_S_ | E=A*B: A broadcast/B contiguous,512 loop;one E output/thread. | 1024 CTAs;512 accumulation; E later consumed byG. | Zero response is a downstream control, not proof of absence of DTC benefit. Recovered candidate E lacks explicit zero; preserve capture correctness gap. Need: Phase1 cycles and counter deltas; prelaunch cache state/memcpy handling and emitted accumulator semantics. |
| 3MM / _Z11mm3_kernel2PfS_S_ | F=C*D: same access geometry, different bases. | 1024 CTAs;independent ofE but host synchronizes; F later consumed byG. | Same shape can map differently; do not pool perphase traffic or assume same cache residency. Need: Phase2 cycles, address-map-sensitive request path and exact initialization/source binding. |
| 3MM / _Z11mm3_kernel3PfS_S_ | G=E*F: same geometry, now true producer-consumer intermediates. | 1024 CTAs;awaitsE/F;7MiB full source object footprint not a residence proof. | E/F retained data may matter independently of DRAM scheduling; actual hit/merge evidence is absent. Need: Phase3 hit/miss/merge deltas and intermediate lifetimes, baseline cache state and strict correctness lineage. |
| particlefilter_naive / kernel | Double CDF8x broadcast across active lanes;linear scan untilCDF[x]>=u[i];coordinate gathers8*j_l;outputs8i contiguous. | 8 CTAs/block128,9 frames with CPU roundtrips; CPU generates video/likelihood/CDF. P1000 CDF<=8000B,not1000lines. | Repeated scan prefix offers reuse conditional on request overlap; zero F response and2read atoms do not establish actual MSHR merge. Need: Perkernel request path and CDF same-line overlap, divergent search lengths, tag/PIB waits and CPU/GPU boundary retained. |

## Existing counter associations and counterexamples

| Program | P0→F256 cycles speedup | DRAM read atoms P0→F256 | L2 reservation failures P0→F256 | Last printed avg_mrq P0→F256 |
|---|---:|---:|---:|---:|
| convolutionSeparable | 1.422263 | 2359408 → 2359296 | 17783805 → 12199317 | 321 → 905 |
| scan | 1.283635 | 21712700 → 21712484 | 67640158 → 65039619 | 184 → 628 |
| hybridsort | 1.133954 | 10205304 → 10204995 | 170798482 → 108686015 | 479 → 1423 |
| 2DCONV | 1.078012 | 2097152 → 2097152 | 2546098 → 1325585 | MISSING → MISSING |
| ATAX | 1.017823 | 19387556 → 18958508 | 158818027 → 153895441 | 745 → 1873 |
| MVT | 0.988434 | 20574896 → 20779732 | 161531923 → 157377128 | 738 → 1798 |
| BICG | 0.993156 | 17688864 → 17459384 | 158410296 → 159914089 | 791 → 2074 |
| vectorAdd | 0.919938 | 1500000 → 1500000 | 5068832 → 2472990 | MISSING → MISSING |
| GEMM | 1.000000 | 0 → 0 | 0 → 0 | MISSING → MISSING |
| 3MM | 1.000000 | 0 → 0 | 0 → 0 | MISSING → MISSING |
| particlefilter_naive | 1.000000 | 2 → 2 | 0 → 0 | 11 → 11 |

- **Positive controls**: convolutionSeparable, scan and 2DCONV improve, while DRAM read atom counts remain unchanged or nearly unchanged. This is consistent with changed service/concurrency rather than substantially reduced DRAM work; it does not identify the kernel or isolate FR-FCFS from shared credits. hybridsort F256 is a supplementary positive without original F128 parity.
- **Negative control**: vectorAdd F256 is slower although its DRAM reads are unchanged and L2 reservation-failure and gpu_stall_dramfull totals decline. A smaller failure total alone cannot establish shorter critical-path delay. F128 gives a modest gain, so "all queue expansion hurts streaming" is also unsupported.
- **Zero-response controls**: GEMM and3MM have exactly equal DH P0/F128/F256 cycles; their existing projection records0 DRAM reads and0 L2 reservation failures. particlefilter_naive has exactly equal cycles and2 DRAM read atoms. These are recorded numeric observations, not missing-as-zero imputation; they do not establish a complete causal classification or capture correctness. Initial HtoD/cache handling and non-DRAM bottlenecks remain relevant.
- **Mixed controls**: ATAX F256 improves slightly but F128 does not; MVT and BICG remain slower for both F variants. Their16-CTA phases have contrasting lane-vs-loop strides and serialized phase order. No per-kernel measured attribution exists yet.
- Printed avg_mrq increases while convolution/scan get faster. It is a last printed aggregate, conditionally emitted and integer-divided, not a measured isolated L2→DRAM queue latency. Do not add means, divide unrelated counts by it, or infer performance from it.
- L2 accepted reads count accepted sectors, not source loads. MSHR_HIT is a supplementary SECTOR_MISS bucket and WRITE_ALLOCATED supplements MISS; neither may be double-counted. DRAM n_rd counts read commands/atoms, not time. Retry/failure and stall totals can count across units/events; do not treat them as disjoint wall-cycle fractions.
- All reused counter projections are SINGLE_STREAM_DECLARED_TRACE_TOTAL. Source print_stats is stream-filtered; an arbitrary final printed bucket is not an all-stream total. Missing L2_specific_MSHR_reasons remains null for all consumed observations.

## Capture and source contradictions retained

- convolutionSeparable: inspected SDK4.2 candidate host predicts384×192 and warmup behavior, while frozen metadata records3072² and one rows/columns pair. The source kernel math can guide a hypothesis; exact host/ROI identity remains unresolved.
- scan: inspected candidate host N26624 differs256× from trace N6815744. The33-launch nine-short/eight-triple recipe and header geometry agree, but the exact capture driver remains unresolved.
- ATAX uses the full selected eededb… trace. dd8955… is an existing body-prefix trim and remains excluded; this analysis does not reselect by speedup or CTA count.
- Fixed recovered PolyBench source differs from separate M5/sgrauerg source/build variants. Do not import M5 corrected-source correctness. ATAX candidate output initialization and3MM candidate E/F/G initialization gaps cannot be silently repaired in source attribution.
- particlefilter_naive GPU work is resampling only; image likelihood, weights and CDF are CPU work. The captured producer ELF, original random bytes and numerical correctness remain separate from strict simulator completion.

## Five observation tasks, in priority order

1. **Read-only existing log phase ledger**: map kernel launch ID/order, stream, perkernel/nonoverlap cycle markers and cumulative counter reset points to the25 phase rows. Produce exact deltas only where monotonic same-scope snapshots bracket each launch; otherwise mark missing. This is the first discriminating step for conv/scan/hybridsort. No simulation is needed.
2. **Read-only counter semantics and baseline cache-state audit**: verify Core9eed print/reset/aggregation, HtoD handling, L2 accepted/merge buckets, DRAM atoms and end-of-kernel drain; inspect exact raw proof references for0-read controls. Avoid summing cumulative snapshots. No simulation is needed.
3. **Read-only bounded emitted-trace inspection**: after explicit workload-bound read budget, inspect retained SASS opcode/header/body snippets for vector widths, texture/constant/global distinction and accumulator RMW; this can disprove source lowering assumptions but cannot certify full-body coverage or dynamic cache behavior. No new capture or execution is needed.
4. **Later separately approved observation build**: if existing logs do not discriminate, add perkernel queue occupancy area/max, admission→L2→DRAM-queue→issue→return→consumer timestamps and failure reason counts, including credit availability. CPU-only test counter accounting first, then seek explicit new model/binary/observation-run authorization. None is implemented here.
5. **Later approved same-identity CH matching**: run predeclared CH F128/F256 cohorts after new scientific/resource execution authority. Compare same original complete inputs and common F128/F256 population; retain negative/missing entries. Only after this and source review consider finite M8×F interactions using real simulation, never multiplied single-factor speedups.

## Reproducibility and boundaries

[PROGRAM_EVIDENCE.json](PROGRAM_EVIDENCE.json) records exact input digest, original RESULT path/SHA/UUID, Core/FW/binary/options and separate named alternatives. [TRACE_METADATA_FOCUS.json](TRACE_METADATA_FOCUS.json) retains already-published Atlas headers. [ATLAS_EXTRACT_MANIFEST.json](ATLAS_EXTRACT_MANIFEST.json) binds all extracted Atlas documents/source snapshots to47a097aa and byte SHA. [RUNTIME_EXTRACT.json](RUNTIME_EXTRACT.json) records source projections and Core source counter-semantics excerpts. This agent produced only independent analysis files.

CH and DH L1 structures are intentionally different designs; matched downstream settings do not prove equal L1 capacity, tag resource, queue/timing or physical area. FR-FCFS128/256 changes shared-credit capacity as well as scheduler window. No current result is an equal-area hardware claim. No future speedup, CH advantage, or causal perkernel result is fabricated.
