# R17 graph-search capability matrix

Date: 2026-09-30. Preparation only; no execution authorization.

Authorities:
- cuVS stable: `v26.08.01@25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`
- cuVS current-source comparison: `d3df668c77da45bce9f7ff80b6adc62f91d4ba01`
- Jasper: `saltsystemslab/Jasper@7ec9125049d6ca08170e47f4027a10c7e37d18bc`
- SONG: `sunbelbd/song@9cb1f486fd72828128d65bc2b107d2c5c6799bf0`

| Capability | Verified source behavior | R17 consequence |
|---|---|---|
| CAGRA AUTO | For non-persistent search, SINGLE_CTA requires itopk<=512 and max_queries>=2*numSM; otherwise MULTI_CTA. | Q1 AUTO is already the mature low-query path. |
| MULTI_CTA | `num_cta_per_query=max(search_width,ceil(itopk/32))`. | itopk is itself an intra-query CTA knob; width=1 vs 2 is redundant at itopk 64/128/256. |
| SINGLE_CTA | Block sizing is adjusted for small query counts. | Legitimate mode control, not primary Q1 baseline. |
| Persistent | SINGLE_CTA only. | Launch/request control; no persistent MULTI_CTA equivalent in this authority. |
| Dynamic batching | Aggregates concurrent requests with queues, streams and timeout. | Serving/concurrency control, not intrinsic isolated-Q1 acceleration. |
| Workspace/output hygiene | Official examples use workspace pooling; benchmark preallocates result buffers. | Allocation/runtime effects must be removed or accounted for. |
| Per-call plan | Public CAGRA search constructs a search plan per call. | Plan/API time must be separated from traversal before architecture claims. |
| Official tuning surface | cuVS-bench sweeps itopk 32..512 and search_width 1..64. | Legitimate knobs, but no need for an exhaustive R17 sweep. |
| Benchmark timing | Wall time plus optional GPU-event timing; throughput mode may pipeline. | Qualification is useful, but Q1 needs caller-visible/runtime accounting. |

Direct neighbors:
- CAGRA already covers “give a low-batch query more CTAs.”
- SONG separates candidate location, distance calculation and state update inside dependent traversal.
- Inspected Jasper beam search iterates frontier -> neighbors -> distance -> sort/dedup/clip -> next frontier.

Generic claims already covered: low-batch underutilization, multi-CTA/query, wider search effort, persistent launch suppression, and concurrent request aggregation.

Surviving question: after recall-qualified MULTI_CTA, a nonredundant bounded itopk/width challenge, resident graph/data and runtime accounting, does isolated Q1 retain a material GPU-local iterative-discovery/state-feedback residual, or is the result explained by distance work and software/runtime management?

State: `R17_GRAPH_SEARCH_SURVIVES_SOURCE_SCREEN_CONTRACT_SIMPLIFIED`.
