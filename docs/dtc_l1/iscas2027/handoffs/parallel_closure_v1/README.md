# DTC-L1：论文与最小补证并行收口 V1

2026-10-16。User-approved direction: express the broader architectural significance, investigate contemporary relevance, and advance writing and necessary evidence concurrently. Status: execution specifications prepared; no node task is asserted started. This branch adds documents only. Old coordination remains d0f8e72b370271b7432c3785c0687e79ca3e0f4b; FAST64/Lane-E/accepted TC80, SG0 and closed SG3/logical80 are not reopened.

## Scientific center

How should finite on-chip storage and service resources support both searchable locality and incomplete memory operations? DTC separates the lifetimes of lookup mappings, retained physical data, and instruction metadata. Renaming permits tag replacement; retained data supports metadata-only waiting; IO/OO supply different complete/reclaim rules. This framing does not invent a new mechanism or assume all modern GPUs have an eight-entry PIB.

Empirical goal: determine when this organization is preferable to enlarging searchable capacity or conventional waiting/miss state, including its finite service cost. Historical 64-SM speedups remain original-model results. Native RTX4080 observations constrain baseline behavior, not hypothetical hardware DTC speedup or undisclosed structure sizes.

## Workload decision

Keep all twelve accepted workloads: ATAX, BICG, GESUMMV, GEMM, 2DConvolution, Btree, DWT2D, Gaussian, Hotspot1, LUD, NN, MRI-Q. Keep regressions and slow cases. The fixed manifest contains 629 ordered trace members; Gaussian 510 and LUD 94 account for 604, about 96.0%. That is not 629 independent applications. NN is nearest neighbor, not a neural network. PolyBench GEMM/2DConvolution are not automatically current Tensor-Core/DNN implementations.

First audit captured input sizes, opcode/cache paths, CTA coverage, steady interval, L1 exposure and actual L2/DRAM work. NO_ARGS and numeric filenames do not establish sizes. RTX4080's 64MiB modeled L2 and adaptive L1/shared partitioning can put old inputs in a different residency regime; do not infer a modern bottleneck from the old program name. A resized input is a new named lineage, not a replacement of the frozen one.

At most TWO added families:
1. SpMV, preferring an already available Parboil implementation/input. Test sparse indirect access, not an assumed positive case.
2. A native-framework LayerNorm operator on the installed stack. Test an actual modern read/reduction/write implementation; no full LLM, weights download, or artificial slow rewrite to enter the DTC path.
One primary input per family; at most one contrasting size used as sensitivity. Fix source, shapes, kernels and eligibility before looking at DTC results. Negative/neutral results remain. Unsupported opcodes, trace semantics or a mostly bypassing path are explicit scope findings, not reasons to search many replacements until a winner appears.

Four bounded diagnostic families: coalesced independent loads; concentrated/distributed addresses; shared consumers and response skew; hit/low-MLP controls. Initially at most three conditions each (twelve native conditions total). Simulator-controlled response schedules are unit tests, not native memory behavior. Hardware cache set indices are not assumed known.

## Evidence priorities

A (mandatory): effective service specification, legality and opt-in necessary correction. Lookup delay/initiation interval, 32B refill, 128B readiness, waiter updates, collection and writeback are separate units. Per-call code limits must be translated into per-core-cycle service. No zero-cost update assumptions merely because a function completes in one call.
B (mandatory): paired performance against conventional capacity and a single predeclared resource-enhanced baseline. Waiting-depth-only diagnosis and cost-bounded traditional design are distinct. Traditional PIB/MSHR growth is not free.
C (mandatory mechanism): one legal IO/OO matched-depth pair on at most four existing diagnostic workloads. Measure fully admitted ready-to-complete time, map-loss-to-free time and occupancy integrals; do not rename legacy frontend-ready counters as a stricter metric.
D (mandatory relevance check): RTX4080 baseline-only diagnosis first, then DTC comparison after A. No DTC-specific 8-entry/32-MSHR clamps on the modern baseline. Read config parser, per-kernel adaptive changes and actual executed paths, not only the literal m/s/f field. Do not switch policy letters through invalid write-policy combinations.
E (bounded extension): the two families above; own result table, not automatic pooled GM14 or repeated shapes counted as separate programs.
F (conditional): RTX3070 at most three representative conditions after primary closure and only if time permits. Not two full platform matrices.

First application pilot is fixed: BICG, Btree, 2DConvolution, Hotspot1, chosen from known distinct responses and practical runtime. This is not an independent holdout. GESUMMV and all twelve cases remain in the full cohort. Pilot qualification permits rolling already-registered independent rows; do not impose a batch barrier. A changed service model does not allow legacy rows to masquerade as new data. Reuse exact identity, validate terminal attempts rather than rerun, and share compatible baselines.

Keep both comparison roles: matched128B structural controls, and a reasonable sector-based contemporary reference. Same data capacity is not same total area. Do not force a modern baseline to whole-line behavior merely to claim fairness.

## Parallel ownership

- [174 Goal](GOAL_174.md): finite service, directed tests, reuse ledger, contemporary baseline pilot and qualified paired simulation.
- [109 Goal](GOAL_109.md): CPU asset preparation, exclusive native diagnostics and at most two new workload families/trace delivery.
- ChatGPT: rewrite the paper and consume verified evidence; English v0.4 has been prepared separately. Source/destination data and unresolved results stay explicit. Hardware reports and final authors are user inputs.

Inspect active node jobs and locks; never infer idleness from historical handoffs. No cross-project resets or restarts. AWMA/C16 platform qualifications are not DTC qualifications. Existing translation features must be dormant or explicitly scoped in DTC tests; do not retune their frozen branches.

## Time and resource policy

Official deadline read on 2026-10-16: Oct22 23:59 UTC-05:00, i.e. Oct23 12:59 Beijing. Working budgets, not guaranteed completion estimates: first 0-6h inventory/service/asset receipts; 6-24h bounded correctness and native pilot; 24-48h first paired evidence and resource baseline selection. Launch qualified slow critical rows early while rolling short rows. Base concurrency on current CPU/RSS/swap/IO and other jobs, not a fixed obligation to fill 24 workers. Real write capacity matters; no arbitrary large free-disk floor.

By Oct20 Beijing evening stop adding workload families and mechanisms; Oct21 fix the supported main-table scope; Oct22 prioritize validation, explicit corrections, paper figures, authors and submission checks. If core evidence is not closed, do not convert a placeholder to a favorable historical number.

Stop only for scientific contract/identity/claim/support-domain changes, irrecoverable payload loss or failed correctness closure. Ordinary parser/build/launcher/provenance repairs continue. Stop irrelevant extra sweeps when the question is answered even negatively. No SG3 queue/DRAM/ICNT replay, no logical80, texture/Tag-bypass expansion, new throttling mechanism, full-GPU RTL or new toolchain migration.

## Source anchors

- Fixed payload: Framework 18a68dcccd795f1b6cda75504e9450d00c9cee02, docs/dtc_l1/fast64/generated/FAST64_PAYLOAD_MANIFEST.tsv.
- Legacy Core: 95ccdb7a056f2d53f740d90869785cac6d4ee0f5, with registered 2D exception 6582b9d171330d88b17e8d5294c97704229e3823; never erase this distinction.
- RTX4080 asset: Framework 8d1f14a32f5538660d74da86ccb03a2c504c5735, configs/rtx4080_ada/SM89_RTX4080_AWMA_V1/gpgpusim.config. Qualification scope: AWMA memory translation, not new DTC acceptance.
- Thesis chapters2.4/4 motivate the concurrency/contention and metadata-waiting relations; their 79% blocked-access breakdown and4.7% OO/IO area belong to the original platform.
- https://epapers2.org/iscas2027/ESR/authorinfo1.php
- https://rodinia.cs.virginia.edu/k-nearest_neighbors.html
- https://docs.nvidia.com/cuda/archive/13.1.1/cuda-programming-guide/04-special-topics/async-copies.html
