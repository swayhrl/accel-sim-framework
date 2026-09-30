# R17 graph-search capability matrix

Date: 2026-09-30. Preparation only; no execution authorization.

Authorities:
- cuVS stable source: `v26.08.01@25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`
- Jasper: `saltsystemslab/Jasper@7ec9125049d6ca08170e47f4027a10c7e37d18bc`
- SONG: `sunbelbd/song@9cb1f486fd72828128d65bc2b107d2c5c6799bf0`

| Existing capability | Source result | R17 consequence |
|---|---|---|
| CAGRA AUTO | Non-persistent AUTO uses SINGLE_CTA only when itopk<=512 and max_queries>=2*numSM; otherwise MULTI_CTA. | Q1 already selects the low-query path. |
| CAGRA MULTI_CTA | `num_cta_per_query=max(requested search_width, ceil(global_itopk_size/32))`. | itopk/search_width are mandatory strong software controls. |
| SINGLE_CTA | Block size is increased automatically for small query counts. | Forced SINGLE_CTA is not a deliberately weak baseline. |
| Persistent CAGRA | Persistent supports SINGLE_CTA only and is designed for concurrent small requests. | Treat as launch/concurrency control, not replacement for Q1 MULTI_CTA. |
| Dynamic batching | Stable cuVS combines concurrent small requests into larger upstream searches with queues, streams and timeout. | Mandatory serving baseline; not intrinsic isolated-Q1 acceleration. |
| Allocator hygiene | Official examples use workspace/memory pools; Python can accept caller-provided outputs. | Preallocate outputs and pool workspace before interpreting Q1. |
| Per-call plan | Public CAGRA search constructs a search plan per call. | Separate API/plan/workspace cost from GPU traversal. |

Direct neighbors:
- CAGRA already covers the generic idea “give a low-batch query more CTAs.”
- SONG stages candidate locating, distance calculation and queue/state update inside a dependent traversal loop.
- Jasper's inspected beam-search kernel launches one CTA per query and iterates frontier -> neighbors -> distance -> sort/dedup/clip -> next frontier.

Already covered claims: low-batch underutilization, multi-CTA per query, wider beam/search work, staged traversal work, persistent launch suppression, and dynamic batching.

Surviving question: after recall-qualified CAGRA MULTI_CTA, bounded itopk/search-width tuning, resident graph/data, preallocated outputs and pooled workspace, does isolated Q1 still retain a material GPU-local residual associated with iterative online discovery/state feedback, or is it explained by distance work and runtime management?

State: `R17_GRAPH_SEARCH_SURVIVES_SOURCE_SCREEN_NARROWED`.
