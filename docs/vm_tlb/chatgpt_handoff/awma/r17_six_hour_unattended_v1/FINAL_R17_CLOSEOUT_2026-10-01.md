# R17 final closeout

Date: 2026-10-01

## Lane F execution authority

R17 V1:
- branch: `hrl/awma-r17-graph-search-native-109-v1`
- commit: `78874fbfd767ec1321d41a04e4c51589a3c07298`
- formal label: `R17_RECALL_GATE_NOT_QUALIFIED`

Interpretation of V1:
- input/runtime/index identity qualified;
- bounded quality grid did not reach recall@10 >= 0.95;
- no formal performance conclusion was made.

R17R1:
- branch: `hrl/awma-r17r1-quality-requalification-109-v1`
- commit: `29ecc6e5e37005046b1a563c830bed9ae58af656`
- tree: `ce106b3b16978ae39468b8ba16eddcd5025877da`
- formal label: `R17_CAGRA_EXISTING_SOFTWARE_SUFFICIENT`

## Accepted R17R1 facts

Fixed scope:
- normalized GloVe-100-angular
- same accepted IVF-PQ CAGRA index
- RTX4080 / SM89
- cuVS 26.8.1
- k=10
- recall@10 >= 0.95
- fully resident single-GPU search
- discovery queries 0..255
- holdout remained sealed

Quality repair on the same index:
- SINGLE_CTA 512/1 recall@10 = 0.959766
- MULTI_CTA 512/1 recall@10 = 0.961328
- no NN_DESCENT second index was required

Formal Q1 paired timing:
- SINGLE_CTA 512/1: 704.184787 ms per 256 individual Q1 searches
- MULTI_CTA 512/1: 56.110419 ms per 256 individual Q1 searches
- Q1_STRONG_V2 = explicit MULTI_CTA 512/1

Matched strong-mode characterization:
- complete Q1 request median = 0.215450 ms
- complete Q32 batch median = 0.530881 ms
- Q32 time was never divided by 32 and presented as single-query latency

## Scientific interpretation

The graph traversal still has iterative discovery/feedback semantics. R17R1 does not claim that dependency disappeared.

The accepted conclusion is narrower:

> For the fixed, quality-qualified, fully resident GloVe/CAGRA/RTX4080 scope, mature CAGRA MULTI_CTA execution plus reusable resources leaves no material unexplained **complete-request low-concurrency latency residual** that warrants GPU-local traversal-state localization.

This is why the experiment stopped before C fallback, persistent control, NSYS/NCU, or holdout.

The result does not establish:
- universal CAGRA optimality
- zero host overhead
- zero memory latency
- zero opportunity in graph search generally
- a statement about filtered, dynamic, offloaded, multi-GPU, or other datasets

It does establish that the specific R17 question should not be rescued with profiling or hardware design.

## Lane G related-work authority

- branch: `hrl/awma-r17-graph-search-related-work-cpu-v1`
- commit: `f72aca7938a1b2e8bb2f62953e308444babd8489`
- conclusion: `NO_SECOND_CANDIDATE_QUALIFIED`

Accepted novelty boundary:
- sequential discovery has direct prior work, especially FlowANN
- CAGRA already targets low-query parallelism with MULTI_CTA
- ALGAS covers small-batch query bubbles / persistent launch suppression
- Jasper is a strong fused per-query software neighbor
- optimized GPU-native graph search may be distance-compute dominated in some regimes

This literature result is consistent with the R17R1 Native closeout and does not create a new execution task.

## Final R17 state

- R17 fully-resident low-concurrency traversal line: CLOSED IN CURRENT SCOPE
- Lane F / 109: STOP
- Lane G / CPU: STOP
- Lane E / 174-new: STOP
- no authorized profiler rescue
- no authorized second dataset/index
- no authorized Jasper port
- no authorized Accel-Sim or hardware mechanism

Next work returns to problem discovery. Reopen graph search only if a new natural workload independently presents a materially different boundary after mature software baselines; do not reopen by parameter fishing on this same GloVe scope.
