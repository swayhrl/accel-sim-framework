# R17 direct-neighbor check

Date: 2026-09-30.

## Existing execution neighbors

CAGRA already implements multi-CTA search for low-batch cases. Stable cuVS also contains persistent CAGRA and dynamic batching. For Q1, stable AUTO routes to MULTI_CTA. These close generic claims about low-batch underutilization, adding CTAs per query, persistent request handling and request aggregation.

SONG separates candidate location, distance calculation and search-state update inside a dependent graph-search loop. The inspected Jasper beam-search kernel advances frontier -> neighbors -> distance -> sort/dedup/clip -> next frontier.

## FlowANN — decisive nearest neighbor

FlowANN (OSDI 2026) is the closest direct neighbor found.

Authorities:
- https://www.usenix.org/conference/osdi26/presentation/zhao
- `SJTU-IPADS/GPU-Graph-ANN@e0a0436fcb2b6c090ba4379d280c6d957215110c`

FlowANN explicitly identifies strict step-level dependency in best-first graph search and replaces it with finer node-level dependency by splitting node discovery from later expansion. It exploits the discovery-expansion window to defer some discoveries and overlap edge fetching with computation.

Primary-paper evidence relevant to R17:
- 95.6% of search steps have mean discovery-expansion window >5 steps;
- one step is about 6--14 us depending on batch;
- about 96% of tested accuracy points add no search steps; a few add about 0.7--2.1%;
- main performance evaluation uses batch 16--2048;
- small-dataset upper-bound study keeps full graph on GPU for CAGRA; FlowANN with 50% of edges reaches 67.9%/85.4% of CAGRA at batch64/2048.

The artifact benchmark supports an explicit batch size including batch 1, but that source capability is not a paper Q1 result and the benchmark allocates per-batch device matrices in its loop.

## Decision

FlowANN does not answer the exact resident isolated-Q1 timing question. It does, however, directly cover the mechanism-level insight that made R17 potentially novel: conventional iterative discovery can be relaxed through discovery-expansion slack while preserving search quality.

State:
`R17_DIRECT_NEIGHBOR_SCREEN_CLOSES_ACTIVE_NOVELTY_CLAIM`.

Project state:
`R17_GRAPH_DEPENDENCY_CORE_INSIGHT_DIRECTLY_COVERED_BY_FLOWANN`.

The dormant Q1 contract remains useful for characterization only. No Native experiment was run.
