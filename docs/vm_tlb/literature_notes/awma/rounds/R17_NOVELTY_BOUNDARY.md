# R17 GPU graph-search novelty boundary

Date: 2026-09-30. Scope: CPU/source/web review only. CUDA=0, GPU-lock acquisitions=0,
node174=0. This note does not modify or reinterpret Lane F's preregistered experiment.

## Outcome

R17 is not an untouched sequential-discovery problem.

- SONG already split graph search into candidate locating, bulk distance, and data-structure
  maintenance to expose GPU distance parallelism.
- CAGRA explicitly assigns multiple CTAs to one low-batch query and tests single-query
  performance.
- Speed-ANN directly relaxes strict best-first ordering through multiple asynchronous CPU
  walkers.
- ALGAS directly targets small-batch latency with persistent independent query slots and
  also changes late search through beam extension.
- Most importantly, FlowANN explicitly identifies the step-level discovery dependency,
  replaces it with node-level discovery-to-expansion windows, and overlaps deferred edge
  fetches with useful work.

The defensible R17 boundary is therefore narrow:

> For a fully GPU-resident static graph, after cuVS AUTO/MULTI_CTA and legal workspace
> reuse, does fixed-quality low-query completion still contain a GPU-local online
> traversal residual that is not host launch, query-batch bubbles, optional graph I/O,
> extra search work, or mandatory distance calculation?

This remains an empirical boundary for Lane F, not a novelty or hardware claim.

## 1. Does prior work directly attack sequential discovery?

Yes, at several strengths.

FlowANN is the closest direct answer. Its OSDI 2026 paper names strict step-level
dependency as the root problem and splits it into node-level discovery and later expansion.
Its public artifact contains per-slot discovery-expansion window state, deferred copy
queues, and dynamic synchronization. The system is designed around a tiered graph with
CPU-resident edges and GDRCopy, so it does not prove the same intervention helps when all
edges are already resident on GPU. It does prove that dependency disentanglement itself is
known prior work.

Speed-ANN is the closest algorithmic answer. It lets asynchronous private CPU walkers
advance and synchronizes them lazily. This changes traversal order, redundant work, and
search dynamics, so it is not an execution-neutral oracle for CAGRA.

SONG is the closest early GPU answer. It decouples an iteration into three stages, but the
candidate and maintenance results still determine the next iteration. CAGRA adds
multi-CTA trajectories and more nodes per iteration; it increases available parallel work
rather than removing the feedback relation.

ALGAS is the closest low-batch systems answer. Its persistent slots remove batch-tail
waiting and repeated launch overhead. That addresses query bubbles across queries, not the
within-query rule that newly measured candidates determine later parents.

Primary sources:
[CAGRA](https://arxiv.org/html/2308.15136v2),
[FlowANN](https://www.usenix.org/conference/osdi26/presentation/zhao),
[Speed-ANN](https://arxiv.org/abs/2201.13007),
[SONG](https://www.cs.rit.edu/~wjz/papers/conference/2020-icde-song.pdf),
[ALGAS](https://yreddice.github.io/pdfs/algas.pdf).

## 2. Algorithm/recall changes versus execution organization

Execution-preserving or close to execution-preserving:

- CAGRA warp splitting and distance team size change hardware mapping, not the graph
  frontier semantics.
- Fusing a per-query search loop, preallocating workspace, and suppressing launches with
  a persistent kernel preserve search work if parameters and stopping rules are fixed.
- ALGAS independent persistent slots remove cross-query batch synchronization; this part
  is an execution change.
- Graph vertex reordering can preserve edges and search rules while changing addresses and
  locality.
- FlowANN's asynchronous edge-fetch schedule is intended to preserve answers, but its
  tiered layout/offload contract is not the same resident workload.

Changes that must be treated as algorithm/work/quality changes:

- CAGRA MULTI_CTA explores more parents/nodes per iteration; search_width, internal top-k,
  graph degree, and iteration limits alter work and recall.
- CAGRA's forgettable hash is lossy and periodically reset.
- Jasper removes a visited hash, permits duplicate neighbor distances, changes merge order,
  and optionally uses directional scoring or lossy RaBitQ.
- GANNS omits the visited-distance check and accepts redundant distance work.
- ALGAS beam extension expands several parents and skips intermediate sorts.
- BOA changes beam width and the surviving query set online.
- Speed-ANN changes best-first order and uses asynchronous private walkers.
- Quantization, graph pruning/layout construction, filtering, tiering/offload, and dynamic
  updates change the problem or index contract unless separately controlled.

The matrix R17_RELATED_WORK_MATRIX.tsv records these distinctions row by row.

## 3. Are CAGRA/Jasper already sufficient for low-query parallelism?

CAGRA is intentionally strong and is the mandatory endpoint, but sufficiency is not known
before Lane F runs.

The CAGRA paper maps one low-batch query to multiple CTAs and reports MULTI_CTA faster for
a single query. Stable cuVS v26.08.01 AUTO selects SINGLE_CTA only when internal top-k is at
most 512 and max_queries is at least twice the SM count; otherwise it selects MULTI_CTA.
Persistent mode forces SINGLE_CTA. Current cuVS main retains these relevant rules.

Independent evidence also prevents an automatic software-sufficient conclusion. The
HardBD/Active 2025 study reports that MULTI_CTA reduces small-batch loss but still does not
fully scale at batch 10. That study reports QPS and changes tuned parameters under recall
constraints; it does not isolate one resident query's mandatory versus removable latency.

Jasper is a strong per-query kernel but a weaker low-query occupancy counterexample. The
pinned source launches one block per query, fuses distance/sort/expansion, keeps state in
shared memory, and tiles distances. No multi-CTA/query or persistent request queue is
present at the pinned commit. Its RTX4080-Super appendix is valuable platform evidence, but
it reports recall-throughput curves rather than a q=1 resident latency decomposition.

Conclusion: Lane F must compare against qualified cuVS AUTO/MULTI_CTA first. Jasper is a
nearest-neighbor capability check, not a reason to replace the preregistered baseline or
declare low-query saturation.

Sources:
[GPU graph-ANN empirical study](https://www.shimin-chen.com/papers/gpu-graph-anns-hardbdactive25.pdf),
[Jasper paper](https://arxiv.org/html/2601.07048),
[Jasper source](https://github.com/saltsystemslab/Jasper).

## 4. Remaining-problem admission rule

A remaining R17 problem exists only if all of the following hold on the same real,
fixed-quality query set:

1. Graph, vectors, queries, output, and reusable workspace are already resident.
2. AUTO resolves as expected and explicit MULTI_CTA is a qualified comparison.
3. Search work is reported: iterations, evaluated nodes/distances, and quality.
4. Host wall time, synchronized GPU time, allocations, and launch count are separated.
5. Any persistent comparison is limited to supported SINGLE_CTA and interpreted only as a
   launch/runtime diagnostic.
6. The residual affects complete query latency and is not explained by mandatory distance
   math or by doing more search work.
7. Any later intervention starts from FlowANN/ALGAS/CAGRA as its nearest existing
   capability; it cannot assume future traversal addresses.

Failure of any item is a STOP or UNKNOWN, not architecture admission.

## 5. Round C bounded next-candidate audit

The post-A/B search did not qualify a second candidate.

- Syncopate directly covers fine-grained compute/communication overlap but requires
  multi-GPU communication, outside the single-4080 cheap-falsification boundary.
- DirectKV requires GH200/GB200 NVLink-C2C and already supplies the strong zero-copy
  software path.
- CoPilotIO, FlashANNS, GORIO, BANG, and FlowANN require storage, RDMA, GDRCopy, or
  offloaded indexes; a 4080-only first test would not represent their scientific input.
- GrAND and BOA have public workload paths, but they are already direct strong software
  systems for dynamic updates and filtered adaptive search.
- GPU checkpoint/restore and production data-pipeline papers require privileged runtime or
  production-scale traces and do not offer a low-cost node109 scientific boundary.
- Kairox-like hybrid neuron placement is already a full software system and would require
  a new large-model/end-to-end setup.

Accordingly:

NO_SECOND_CANDIDATE_QUALIFIED

No R18 preparation card or execution Goal is created.

## 6. Claim limits

No performance ranking is copied across different datasets, GPUs, recall targets, index
layouts, or residency assumptions. Paper speedups remain author-reported. Source API
presence is not node109 runtime qualification. FlowANN's offload result is not evidence of
a resident-graph speedup, and the 60-80% distance share in the 2026 study is not a universal
constant for q=1.
