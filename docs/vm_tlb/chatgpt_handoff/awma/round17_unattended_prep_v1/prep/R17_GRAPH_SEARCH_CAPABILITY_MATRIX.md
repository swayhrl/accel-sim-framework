# R17 graph-search capability matrix

Date: 2026-09-30. Source audit only; no execution authorization.

Authorities:
- cuVS stable: `v26.08.01@25b1be43a8c127e5ab6d2f29f20c62dbfd3351ab`
- cuVS current comparison: `d3df668c77da45bce9f7ff80b6adc62f91d4ba01`
- Jasper: `saltsystemslab/Jasper@7ec9125049d6ca08170e47f4027a10c7e37d18bc`
- SONG: `sunbelbd/song@9cb1f486fd72828128d65bc2b107d2c5c6799bf0`
- FlowANN: OSDI 2026; artifact `SJTU-IPADS/GPU-Graph-ANN@e0a0436fcb2b6c090ba4379d280c6d957215110c`

| Capability | Verified behavior | R17 consequence |
|---|---|---|
| CAGRA AUTO | Non-persistent SINGLE_CTA requires itopk<=512 and max_queries>=2*numSM; otherwise MULTI_CTA. | Q1 AUTO already uses mature low-query MULTI_CTA. |
| CAGRA MULTI_CTA | `num_cta_per_query=max(search_width,ceil(itopk/32))`. | Generic more-CTAs/query claim is covered; width1/2 is redundant for itopk64/128/256. |
| cuVS persistent | Persistent is SINGLE_CTA-only in the pinned authority. | Launch/request control, not persistent MULTI_CTA. |
| cuVS dynamic batching | Aggregates concurrent small requests. | Serving control, not isolated-Q1 intrinsic latency. |
| Runtime hygiene | Public search has per-call plan work; benchmark/examples support pooling/preallocation paths. | Runtime/plan/allocation must be separated before GPU-local claims. |
| SONG/Jasper | Explicit iterative candidate/frontier, distance and state-update organization. | Strong execution neighbors. |
| FlowANN dependency model | Strict step dependency is decomposed into discovery and later expansion; discoveries may be deferred. | Directly covers R17 central causal insight. |
| FlowANN search-work check | ~96% tested points add no steps; a few add ~0.7--2.1% at same accuracy. | Deferral is not justified by silently doing much less work. |
| FlowANN workload boundary | Main evaluation batch16--2048; target is billion-scale CPU/GPU tiered graph. | Does not supply resident-Q1 Native result. |
| FlowANN upper-bound study | Full-GPU CAGRA is upper bound; FlowANN with 50% edges gets 67.9%/85.4% at batch64/2048. | Offload path is not evidence of beating resident CAGRA. |
| FlowANN artifact Q1 capability | Benchmark accepts batch1 but allocates per-batch device matrices. | Source capability, not clean Q1 latency authority. |

Closed generic claims now include low-batch underutilization, multi-CTA/query, persistent launch suppression, concurrent request aggregation, recognizing iterative graph dependency, separating discovery from expansion, and using discovery-expansion slack to defer work.

Remaining factual gap: a fully resident isolated-Q1 cost decomposition on the target platform. This is characterization, not sufficient active novelty after FlowANN.

State: `R17_GRAPH_DEPENDENCY_CORE_INSIGHT_DIRECTLY_COVERED_BY_FLOWANN`.
