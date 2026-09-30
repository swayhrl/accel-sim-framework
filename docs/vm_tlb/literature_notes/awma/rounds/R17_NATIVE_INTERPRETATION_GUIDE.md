# R17 native interpretation guide

Date: 2026-09-30. This is advisory evidence for reviewing Lane F. It does not
change Lane F's preregistered arms, shape choices, thresholds, or profiling budget.

## First bind identity and work

For every compared result, keep together:

- cuVS release/commit and actual selected algorithm;
- graph/index hash, data/query split, dtype, metric, k and recall;
- search_width, internal top-k, graph degree, min/max iterations and team size;
- number of queries and whether the number is request concurrency or a throughput batch;
- graph/vector/query residency and workspace allocation/reuse;
- iterations and evaluated distance/node counts where observable.

Do not interpret a faster mode as execution improvement until quality and search work are
shown comparable. CAGRA MULTI_CTA normally visits more nodes per iteration; beam width and
internal top-k are not execution-only knobs.

## Interpretation table

| Classification | Observable pattern | What it means | Common false positive |
|---|---|---|---|
| software sufficient | AUTO selects MULTI_CTA for low max_queries; qualified explicit MULTI_CTA leaves less than the preregistered material residual; group results stable | Existing per-query parallel execution closes the question | Comparing only with SINGLE_CTA or a Python per-query loop |
| mandatory distance math | At fixed recall/work, time tracks evaluated vectors times dimension; distance work dominates the valid device interval; visited/queue phases and host gap are small | Remaining time is useful similarity computation | Calling all kernel time memory latency without work counts |
| host/runtime | Synchronized device interval is small while query-ready to result-ready wall time is larger; reusable workspace removes allocations; supported SINGLE_CTA persistent mainly removes launches | Fix wrapper, allocation, launch, or synchronization first | Treating persistent-versus-MULTI_CTA as one causal intervention |
| online traversal residual | Same-quality, similar-work low-query execution remains materially slower after legal MULTI_CTA; device timeline contains repeated frontier/visited/selection serialization not explained by distance math; batch-32 gains come from hiding this per-query critical path rather than only more independent work | A bounded GPU-local traversal organization question remains | More CTAs perform more search, lower recall, or use future-path knowledge |
| query-bubble residual | Queries in a batch finish at different iteration counts and completed slots wait for the slowest; a persistent independent-slot design would remove the wait | ALGAS is the direct software neighbor | Calling cross-query tail wait an intrinsic single-query dependency |
| edge-I/O dependency | Stalls are caused by host/storage edge fetch after discovery | FlowANN/FlashANNS/GORIO are the direct neighbors | Generalizing offload results to a fully resident graph |
| unknown | Required counters are unavailable, persistent hides iteration observation, or quality/work do not match | Preserve uncertainty and stop mechanism claims | Inferring causality from occupancy or a stall percentage alone |

## Minimal non-invasive observables

Use only observables already legal in Lane F:

1. Complete wall time from resident query-ready to results-ready.
2. Synchronized GPU interval for the same request.
3. Actual search mode and source-backed AUTO decision.
4. Recall and result quality on the frozen query split.
5. Search iterations and distance/node evaluations when the mode exposes them.
6. Kernel/launch count and workspace allocation outside versus inside the request boundary.
7. A bounded timeline only if timing leaves an unexplained residual.

These observables distinguish the four requested cases without SASS/NVBit or future-path
tracing.

## Mode-specific cautions

### CAGRA

- Stable and current source route AUTO to MULTI_CTA when low max_queries cannot occupy the
  GPU or internal top-k exceeds 512.
- MULTI_CTA uses a standard device-memory hash and private CTA candidate lists; it is not
  the same state organization as SINGLE_CTA.
- Persistent mode is SINGLE_CTA-only. It is a host/launch diagnostic, not the strong
  low-query per-query-parallel endpoint.
- The ordinary public search path does not expose a user-facing iteration array; an
  internal observer must not be assumed available in every wrapper or persistent path.

### Jasper

- Pinned Jasper maps one query to one block and fuses the iterative loop.
- It removes the visited hash and can compute duplicate distances. Work counts are needed
  before comparing its timing to CAGRA.
- Directional search and RaBitQ are algorithm/representation variants, not execution-only
  controls.

### ALGAS and FlowANN

- If the only problem is launch or batch-tail waiting, cite ALGAS and classify the result
  as software organization.
- If the only problem is offloaded-edge waiting, cite FlowANN and keep it outside the
  fully resident claim.
- Neither system permits an oracle that preloads the future resident traversal path.

## Decision flow

1. Verify residency, quality and selected mode.
2. Compare qualified AUTO and explicit legal low-query mode.
3. Check work counts before reading timing deltas.
4. Separate host wall time from synchronized device time.
5. Attribute the remaining device interval to distance math versus frontier/visited work.
6. If one category closes the result, stop there.
7. If evidence is mixed or an observer is unavailable, report UNKNOWN; do not redesign
   Lane F or promote a mechanism.

## Nearest-neighbor citations

- [CAGRA](https://arxiv.org/html/2308.15136v2)
- [cuVS CAGRA guide](https://docs.nvidia.com/cuvs/user-guide/api-guides/indexing-guide/cagra)
- [Jasper](https://arxiv.org/html/2601.07048)
- [ALGAS](https://yreddice.github.io/pdfs/algas.pdf)
- [FlowANN](https://www.usenix.org/conference/osdi26/presentation/zhao)
- [GPU graph-ANN empirical study](https://www.shimin-chen.com/papers/gpu-graph-anns-hardbdactive25.pdf)
