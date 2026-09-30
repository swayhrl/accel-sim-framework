# R17 minimal Native contract V2 — review draft

Date: 2026-09-30.

Preparation only. This is not an accepted execution contract and does not authorize CUDA, profiler, simulator, holdout opening, or hardware work.

## Question

After a real learned-embedding graph and vectors are resident on one GPU, and after mature CAGRA low-query software is used, does isolated Q1 retain a material GPU-local residual associated with iterative online discovery/state feedback?

Legal negative explanations include existing MULTI_CTA/search-effort choices, host/API/plan/workspace management, necessary distance computation, or a change in ANN search work.

## Preconditions

Before scientific timing:
- qualified GloVe-100 local bytes and hashes;
- exact v26.08.01 runtime receipt on node109;
- one frozen resident uncompressed FP32 index;
- proposed graph_degree=64 and intermediate_graph_degree=128;
- k=10 and proposed recall@10 >=0.95;
- build/upload excluded from request timing.

Proposed query split for review:
- discovery IDs 0..255;
- sealed holdout 256..511.

Holdout must not influence software selection.

## Minimal software screen

For Q1, first record that AUTO resolves to MULTI_CTA. If AUTO and forced MULTI_CTA are the same plan, do not time them as two independent formal arms.

Proposed nonredundant discovery grid:
- itopk 64,128,256;
- search_width=1.

These map to at least 2,4,8 CTAs/query. Optionally add one width point that truly exceeds the implicit CTA count, such as itopk64/width4. Do not retain width=2 at all three itopk values as a nominally independent parallelism sweep.

One forced SINGLE_CTA arm may be a mode control. Persistent SINGLE_CTA is only an optional request/launch control. Dynamic batching belongs to a separate concurrent-serving comparison, not isolated-Q1 intrinsic latency.

## Timing boundary

Future selected arms must record:
- caller-visible request time;
- GPU-event search time where valid;
- plan/workspace/allocation accounting;
- recall and actual query count;
- resolved algorithm and search parameters.

Outputs must be preallocated before formal timing. Workspace behavior must be pooled or explicitly receipted.

Do not use index build/load time, first upload, throughput-hidden scheduling latency, or Q32_time/32 as Q1 latency.

If host/plan/wrapper effects are material, a bounded preallocated C/C++ path or equivalent stable benchmark path must be tested before any architecture-local conclusion.

## Admission

Profiling is considered only after real input, recall, strong software and runtime-accounting gates all pass, and only with user approval.

Candidate future labels:
- `R17_EXISTING_CAGRA_SOFTWARE_SUFFICIENT`
- `R17_HOST_PLAN_OR_WRAPPER_DOMINANT`
- `R17_DISTANCE_WORK_DOMINANT`
- `R17_LOW_CONCURRENCY_GPU_RESIDUAL_PRESENT`
- `R17_RESULT_MIXED_NEEDS_REVIEW`

Current state:
`R17_NATIVE_CONTRACT_REVIEW_DRAFT_READY_LOCAL_RECEIPTS_PENDING`.
