# Codex Goal — Lane F / node109
## AWMA R17 resident graph-search low-concurrency boundary V1

Date: 2026-09-30

One continuous solve-and-continue Goal. It intentionally merges preparation, qualification, Native screening, one bounded strong-software/mode challenge, profiling if needed, and sealed holdout. Do not stop between these stages for routine review.

Execution branch:
`hrl/awma-r17-graph-search-native-109-v1`

Starting authority:
`5ff0287ce45c3909d53ac44975f6fa488664b085`

Read `START_HERE.md` and the Round17 problem card first.

---

# 0. Question

Answer:

> On one GPU with graph and vectors resident, after using a mature CAGRA implementation and its existing low-query execution modes, does a low-concurrency ANN query still expose a material execution residual associated with iterative online traversal/state maintenance, or are the observed costs already explained by existing software choice, host/runtime overhead, or mandatory distance computation?

This is not a cache-design Goal and not a RAG end-to-end benchmark.

---

# 1. F0 — runtime/source/input qualification, CPU first

## 1.1 Runtime

First inspect node109 for an already compatible cuVS environment.

Preferred reproducible runtime:
`cuvs-cu12==26.8.1`.

Source identity for that release:
`NVIDIA/cuvs v26.08.01 @ 25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`.

If not already installed, create an isolated environment under the R17 campaign root. Do not modify accepted AWMA environments.

Record:
- Python
- cuVS version
- CUDA runtime/package versions
- driver/GPU/SM
- CuPy/RMM/RAFT-facing versions visible to Python
- exact wheel hashes if downloaded
- source tag/commit.

Current main `d3df668...` may be read for capability changes, but do not mix main source with 26.8.1 runtime behavior.

If 26.8.1 cannot run on RTX4080 after bounded environment repair, STOP:
`R17_CUVS_RUNTIME_NOT_QUALIFIED`.

## 1.2 Dataset

Primary scientific input:
cuVS built-in `glove-100-angular`.

Use the official cuVS benchmark dataset tooling / descriptor and its ground truth.

Why this input:
- about 1.1M learned word embeddings
- dimension 100
- 10K queries
- public ANN benchmark ground truth
- small enough that the full resident dataset and graph are practical on 16 GiB.

Do not call it a natural RAG request trace. It is a learned-embedding ANN workload.

Durable data lives on node164; node109 may keep an active replica/cache.

Freeze:
- exact dataset source/URL or helper version
- file hashes
- dtype
- normalization state
- metric
- ground-truth identity.

Use query IDs:
- discovery: 0..255
- sealed holdout: 256..511

Do not inspect holdout performance during tuning.

If GloVe authority/download cannot be recovered, a tiny SIFT canary is allowed only to debug the environment. It cannot become the scientific input. If GloVe remains unavailable, STOP:
`R17_GRAPH_INPUT_NOT_QUALIFIED`.

---

# 2. F1 — frozen CAGRA index

All CUDA work from this point requires:
`/data/c16/locks/c16_gpu_campaign.lock`.

Build exactly one uncompressed device-resident CAGRA index.

Frozen build parameters:
- metric matching the official angular/cosine ground truth;
- `graph_degree=64`;
- `intermediate_graph_degree=128`;
- stable-release default build algorithm unless the runtime explicitly reports a different default; bind the actual value;
- no compression;
- no filtering;
- no dynamic updates.

Use FP32 dataset representation for this first screen unless the official prepared input is another dtype. Do not convert to FP16 just for performance.

Record build time and peak memory separately. They are not part of query latency.

Serialize/publish the index if supported so later stages do not rebuild it. If serialization is unavailable, deterministic rebuild is acceptable but record the graph hash / deterministic identity if obtainable.

Sanity:
- k=10;
- verify ground-truth shape;
- validate finite results and indices;
- establish baseline recall.

If the default index cannot reach recall@10 >=0.95 with a reasonable search parameter from the bounded grid below, classify quality failure rather than weakening the target after seeing performance:
`R17_RECALL_GATE_NOT_QUALIFIED`.

---

# 3. F2 — source-plan and fixed-config census

Before tuning, freeze one diagnostic search configuration:

- `itopk_size=64`
- `search_width=1`
- team_size/thread_block/hashmap = AUTO/default
- max_iterations = AUTO/default
- random-seed settings unchanged
- k=10.

Run on discovery queries at controlled batch sizes:
- Q1
- Q32
- Q256 control.

For each, evaluate:
- AUTO
- forced MULTI_CTA
- forced SINGLE_CTA

Do not duplicate a full timing arm when source/runtime evidence proves AUTO resolved to exactly the same plan and behavior as one forced arm; keep a short identity receipt instead.

Persistent search:
- only SINGLE_CTA is legal.
- treat it only as a launch/host-overhead control.
- if the Python API's allocations make persistent evaluation invalid or fragile, do not force it through Python. Use the one allowed preallocated C/C++/C-API harness fallback if practical.
- if no clean persistent measurement is possible, mark `PERSISTENT_CONTROL_NOT_QUALIFIED`; that alone does not fail the main experiment.

Report recall for every distinct execution arm. Different recall/work is not a pure performance comparison.

---

# 4. F3 — bounded strong low-concurrency software challenge

The primary workload is Q1.

Use discovery queries only.

For MULTI_CTA, evaluate this preregistered small grid:

- itopk_size: 64, 128, 256
- requested search_width: 1, 2
- all other search parameters unchanged/default.

This is six configurations, not an open-ended tuner.

For each:
- recall@10;
- complete query-ready -> results-ready host time;
- GPU event search time if valid;
- actual batch=1;
- source-derived expected `num_cta_per_query` from the accepted CAGRA rule where applicable;
- output equality is not required across approximate configurations; quality is controlled by recall.

Choose the fastest Q1 configuration satisfying recall@10 >=0.95.
Call it `Q1_STRONG`.

Do not tune on holdout.

Also keep:
- `Q1_AUTO_DEFAULT`
- the best legal SINGLE_CTA nonpersistent control if it meets recall
- persistent SINGLE_CTA only if cleanly qualified.

If the mature grid removes the apparent low-query penalty or leaves no concrete residual, terminate after the timing/quality closure:
`R17_CAGRA_EXISTING_SOFTWARE_SUFFICIENT`.

---

# 5. F4 — formal timing boundary

Use discovery queries 0..255.

For the selected distinct arms, formal timing uses:
- 3 paired groups
- 2 warmups/arm/group
- 5 formal repeats/arm/group
- alternate arm order across groups
- save every sample.

A formal repeat for Q1 processes the complete frozen 256-query set as 256 individual searches.
A formal repeat for Q32 processes the same set as eight 32-query batches.
Q256 is a throughput/control point, not the target latency claim.

Report:
- complete host wall time
- GPU completion time where correctly measurable
- per-query latency distribution for Q1
- batch completion time for Q32/Q256
- throughput
- recall
- query/result allocations and any reusable workspace behavior.

Do **not** use `Q32_time/32` as a single-query latency bound.

## Wrapper gate

Python is acceptable for qualification/tuning.

For the scientific Q1 conclusion, if host/wrapper/allocation work is >=10% of complete Q1 time or NSYS shows it dominates:
- build/use one minimal preallocated C or C++ harness against the same pinned cuVS runtime/source behavior;
- re-run only the selected Q1 arms.

If a strong preallocated harness cannot be qualified and wrapper cost remains material:
`R17_HOST_OR_WRAPPER_DOMINANT`.
Do not claim GPU traversal architecture headroom.

---

# 6. F5 — bounded localization only if a residual survives

Trigger only if:
- recall gate passes;
- Q1 strong software/mode screen still leaves a scientifically interesting low-concurrency behavior;
- host/wrapper is not the explanation.

Take at most:
- one NSYS capture covering Q1_STRONG and one Q32 matched batch in clearly separated NVTX ranges;
- two NCU exact traversal-kernel targets, one Q1 and one Q32, only if exact kernel identity can be bound from the timeline.

Before NCU, query actual SM89-supported metrics.

Evidence classes:
A. utilization/issue:
- active/eligible warps
- occupancy
- selected/not-selected context
B. memory/dependency:
- long-scoreboard-like
- LG/LSU throttle
- L1/TEX/L2/DRAM traffic if supported
C. compute:
- math-pipe / executed instruction evidence
D. launch/runtime:
- host gaps, kernel count, allocation/sync

Unsupported counters stay unavailable.

Do not infer:
- long scoreboard == graph pointer dependency
- DRAM bytes == cache mechanism headroom
- low occupancy == hardware opportunity.

No SASS/NVBit trace.

---

# 7. F6 — interpretation and sealed holdout

Potential classifications after discovery:

### Existing software sufficient
`R17_CAGRA_EXISTING_SOFTWARE_SUFFICIENT`

Use when mode/search-width/itopk choices close the observed issue or no material unexplained Q1 residual remains.

### Host/runtime dominated
`R17_HOST_OR_WRAPPER_DOMINANT`

Use when complete Q1 cost is materially controlled by Python/allocation/dispatch and a stronger preallocated path cannot demonstrate a GPU-local residual.

### Mandatory distance/compute dominant
`R17_DISTANCE_COMPUTE_DOMINANT`

Use only with profiling/source evidence that the strong Q1 path is primarily limited by necessary distance/math work rather than a localizable traversal/state issue.

### Low-concurrency execution residual
Candidate label:
`R17_LOW_CONCURRENCY_TRAVERSAL_RESIDUAL_PRESENT`

This requires all:
- real input + recall>=0.95
- Q1 strong mature software/mode baseline
- host/wrapper not primary
- a consistent GPU-local residual across discovery queries
- source/profiler evidence compatible with limited intra-query progress/online traversal or state maintenance
- not merely a different amount of search work
- no claim of a specific hardware fix.

If this candidate label is reached, open sealed holdout queries 256..511 and re-run only:
- Q1_STRONG
- one preselected comparator that motivated the residual
- the same quality/accounting.

No retuning after holdout.

If holdout does not reproduce the direction, final:
`R17_RESULT_MIXED_NEEDS_REVIEW`.

If it does, final:
`R17_LOW_CONCURRENCY_TRAVERSAL_RESIDUAL_READY_FOR_REVIEW`.

This still does not authorize architecture or 174.

### Evidence insufficient
`R17_RESULT_MIXED_NEEDS_REVIEW`

Use for inconsistent quality/performance/counter evidence that does not fit the labels above.

---

# 8. What is explicitly forbidden

Do not:
- use a synthetic random-vector dataset as scientific evidence
- call GloVe a RAG service trace
- lower recall to claim speedup
- dynamically insert/delete graph nodes
- add filtering predicates
- use CPU/NVMe/offload/multi-GPU
- run a second dataset/model
- run exhaustive parameter sweeps
- start Jasper performance porting unless CAGRA cannot qualify at all and the reason is specifically an implementation capability gap; even then stop for review rather than silently switching systems
- design a cache/prefetcher/graph accelerator
- capture new NVBit/SASS trace
- run Accel-Sim / node174
- reopen Round16 lines.

---

# 9. Deliverables

Review pack:
`docs/vm_tlb/review_packs/AWMA_R17_GRAPH_SEARCH_109_V1/`

At minimum:
- README.md
- SOURCE_RUNTIME_RECEIPT.json
- DATASET_RECEIPT.json
- QUERY_SPLIT.tsv
- INDEX_RECEIPT.json
- QUALITY_CALIBRATION.tsv
- PLAN_IDENTITY.tsv
- DISCOVERY_TIMING.tsv
- STRONG_Q1_SELECTION.md
- WRAPPER_ACCOUNTING.md
- PROFILE_SUMMARY.tsv if triggered
- HOLDOUT_TIMING.tsv if triggered
- FINAL_DECISION.md
- RUN_RECEIPTS.json
- RAW_DATA_INDEX.tsv
- SHA256SUMS

Large dataset/index/raw goes to node164.

---

# 10. Closure

Release GPU lock after every bounded campaign and at final closure.
No busy waiting.

Commit exact harness/tools/review pack.
Push and fetch-back verify exact branch SHA/tree.
Clean worktree.
STOP.

Do not auto-start any next experiment after the final classification.
