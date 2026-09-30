# Round17 closeout after FlowANN direct-neighbor audit

Date: 2026-09-30.

Status: `R17_GRAPH_DEPENDENCY_CORE_INSIGHT_DIRECTLY_COVERED_BY_FLOWANN`.

Project interpretation: `R17_ACTIVE_PROBLEM_DISCOVERY_CLOSED_NOVELTY_OVERLAP`.

This is a literature/source closeout, not a Native performance negative.

## Decisive direct neighbor

FlowANN: Haoru Zhao et al., *Disentangling Graph Dependencies for Efficient Billion-Scale GPU Vector Search*, OSDI 2026.

Primary paper: https://www.usenix.org/conference/osdi26/presentation/zhao

Public artifact: `SJTU-IPADS/GPU-Graph-ANN@e0a0436fcb2b6c090ba4379d280c6d957215110c`.

FlowANN directly identifies the strict step-level dependency of best-first graph search, then separates node discovery from later node expansion. It reports that 95.6% of search steps have an average discovery-expansion window greater than five steps, with roughly 6--14 us per step depending on batch. It uses this slack to defer discoveries and overlap edge fetching with computation.

This is the same causal structure that made R17 potentially novel; it is not merely another multi-CTA baseline. FlowANN also checks search-work consequences: about 96% of evaluated cases need no extra search steps under deferred discovery, while the remaining reported cases add only about 0.7--2.1% at the same accuracy target.

## Important non-equivalence

FlowANN targets billion-scale graph capacity and CPU/GPU edge fetching. Its main evaluation uses batch sizes 16--2048, not isolated resident Q1.

In its small-dataset upper-bound study, CAGRA keeps the full graph on GPU. FlowANN keeps 50% of edges and reaches 67.9% and 85.4% of CAGRA throughput at batch 64 and 2048. Thus FlowANN does not show that offloaded execution beats resident CAGRA.

The public artifact benchmark can accept batch size 1, but the inspected benchmark allocates per-batch query/result device matrices in its loop; that is not a clean preallocated Q1 latency authority.

Therefore fully resident Q1 cost decomposition remains an unmeasured characterization question, but it no longer qualifies by itself as an active AWMA novelty candidate.

## Reopen rule

Reopen only if an independent Native observation exposes a distinct material resident-GPU residual not already explained or targeted by CAGRA multi-CTA/search-width execution, FlowANN-style discovery/expansion deferral, host/plan/workspace overhead, necessary distance computation, or changed ANN search work/quality.

The GloVe authority and Native draft remain dormant characterization assets.

Boundary: CUDA=0; NSYS/NCU=0; 174/Accel-Sim=0; NVBit/SASS=0; no payload download; no accepted contract change; no hardware design.
