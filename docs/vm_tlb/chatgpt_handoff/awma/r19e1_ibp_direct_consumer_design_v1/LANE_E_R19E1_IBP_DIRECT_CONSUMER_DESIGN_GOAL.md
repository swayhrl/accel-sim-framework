# Codex Goal — Lane E / node174-new CPU/source only
## R19E1 IBP direct-consumer implementation-feasibility design V1

Date: 2026-10-01

Execution branch:
`hrl/awma-r19e1-ibp-direct-consumer-design-174new-v1`

Scientific parent:
`bdd85bde5fe7dab1555f52ec6201f7765bbacc2d`

CUDA=0. GPU lock=0. Accel-Sim=0.

This is a design-qualification follow-up, not a Native performance run.

## 0. Accepted parent facts

The parent qualified:
`R19_IBP_DIRECT_CONSUMER_CANDIDATE_QUALIFIED`

Narrow scope:
- Legion / Reddit GraphSAGE
- pinned host IBP rows / compressed GPU cache slab
- Legion transfer/cache kernel reconstructs sampled FP32 features
- complete sampled-feature dense buffer is written to GPU global memory
- trainer receives dense features through IPC
- first GraphSAGE SAGEConv consumes them afterward
- Figure 9 shows nonzero exposed next-batch wait, but does not isolate dense-buffer write/read cost.

Closest work already blocks broad claims:
- ZipServ
- tile-rANS/GEMM
- nvCOMP device APIs
- DFloat11
- UCCL-Zip.

## 1. Question

Can we define **one bounded, same-semantics Native diagnostic** on the parent Legion/Reddit path that removes or bypasses only the dense sampled-feature materialization/readback boundary without silently changing:
- sampled IDs/edges
- host/cache hit/miss decisions
- PCIe fetch work
- IBP decode work
- GraphSAGE mathematical work
- feature reuse count
- floating-point accumulation order beyond the explicitly frozen contract?

If yes, produce an execution-ready design and exact patch plan.
If no, stop before GPU and state why.

## 2. Audit first-layer GraphSAGE semantics

Pin exact parent Legion commit and inspect:
- GraphSAGE model definition
- DGL SAGEConv implementation/version actually used
- feature tensor shapes/layouts
- source/destination node reuse
- two-hop block structure
- where first-layer linear transforms and neighbor aggregation happen
- how many times a sampled source feature can be reused within the batch.

Determine whether a naive "decode row and immediately consume" would:
- duplicate decompression for reused nodes;
- change aggregation order;
- change memory layout expected by DGL;
- require cross-process fusion impossible under the existing IPC boundary.

Do not assume direct fusion is legal because a device decode helper exists.

## 3. Enumerate exactly three implementation classes

Evaluate feasibility, source changes and semantic risk for only these:

### P1 — same-process fused staging diagnostic

Move only the **first GraphSAGE layer** into the sampler-side process or a shared CUDA worker so decoded feature tiles are consumed before full dense-buffer publication.

Must preserve:
- same trained weights;
- same sampled graph block;
- same FP32 feature bits;
- same first-layer output tensor contract delivered to the trainer afterward.

This may remove the original cross-process raw-feature IPC but introduces first-layer-output IPC. Account for that explicitly.

### P2 — tile-sized dense staging

Keep sampler/trainer separation but replace whole sampled-feature materialization with a bounded tile/ring buffer:
- decode a deterministic subset of source-node feature rows;
- first-layer consumer processes the tile;
- reuse bookkeeping prevents re-decode of rows needed multiple times;
- only tile-sized staging lives at once.

This is allowed only if DGL/GraphSAGE first-layer semantics can be preserved without changing neighbor aggregation work/order beyond the frozen numerical contract.

### P3 — decode-inside-first-layer custom diagnostic

Integrate the existing IBP device decoder into a minimal custom first-layer GraphSAGE kernel or an equivalent decomposition:
- same sampled IDs/edges;
- decode each unique required feature no more than baseline's logical reconstruction count unless exact reuse is maintained;
- same first-layer mathematical operation.

This is the most invasive option and should be chosen only if P1/P2 cannot provide a cleaner same-semantics test.

Do not implement any of P1/P2/P3 in this CPU-only Goal.

## 4. Choose exactly one future Native diagnostic

Pick the **least invasive** option that can isolate the parent boundary while preserving semantics.

Selection criteria in order:
1. scientific identity/semantics;
2. avoids changing decode work and feature reuse;
3. bounded code change;
4. measurable full-step effect;
5. feasible on RTX4080/109.

If none satisfies all:
`R19E1_IBP_DIRECT_CONSUMER_DIAGNOSTIC_NOT_QUALIFIED`
STOP.

If one qualifies:
`R19E1_IBP_DIRECT_CONSUMER_DIAGNOSTIC_READY`

## 5. Numerical contract

The parent preparation card's blanket "first-layer output bitwise identical" may be too strong if the existing DGL path is nondeterministic or if legal kernel reordering changes FP32 reduction order.

Do not silently weaken it.

Determine from pinned implementation:
- whether baseline first-layer output is bitwise deterministic across repeated identical replays;
- if yes, keep bitwise identity;
- if no, freeze a source-/repeat-derived engineering tolerance **before** any future performance run and preserve sampled graph, feature bits and operation definition.

Feature reconstruction itself remains bitwise lossless:
- every decoded FP32 feature must match original 32-bit pattern.

The future diagnostic cannot change model quality/algorithm.

## 6. Future 109 replay contract

Produce an exact plan, not execution.

Freeze:
- one real Reddit batch with real sampled IDs/edges;
- one real cache snapshot with at least one host miss;
- model/optimizer/RNG state;
- sampler/trainer process topology;
- MPS/stream settings;
- feature tensor hash;
- first-layer weights hash;
- baseline first-layer output hash/statistics.

Future arms:

### B0
Accepted Legion+IBP(C/M) parent path.

### D1
Chosen direct-consumer diagnostic changing only the dense sampled-feature boundary.

Formal future timing:
- 10 warmups
- 30 matched replays
- exact state restore between replays
- same batch/cache snapshot.

Primary metrics:
- complete training-step latency;
- exposed `get_next` wait;
- producer->first-layer-complete interval;
- bytes written/read for sampled dense feature staging;
- any new IPC bytes;
- first-layer output equivalence.

5% complete-step median improvement remains the future investment screen, not a universal law.

## 7. Required patch plan

Create:
- exact files/functions to modify;
- data/control-flow before and after;
- required new structs/buffers;
- synchronization points;
- how feature reuse is preserved;
- how cross-process costs are accounted;
- estimated code footprint;
- build/dependency risks.

Classify each change:
- measurement instrumentation
- semantic-preserving diagnostic
- engineering support.

No hardware mechanism.

## 8. Deliverables

Under:
`docs/vm_tlb/review_packs/AWMA_R19E1_IBP_DIRECT_CONSUMER_DESIGN_V1/`

At minimum:
- README.md
- PARENT_AUTHORITY.json
- GRAPH_SAGE_SEMANTICS.md
- THREE_IMPLEMENTATION_OPTIONS.md
- SELECTED_DIAGNOSTIC.md
- NUMERICAL_CONTRACT.md
- FUTURE_REPLAY_CONTRACT.md
- PATCH_PLAN.md
- RISK_REGISTER.md
- FINAL_DECISION.md
- SOURCE_RECEIPTS.tsv
- SHA256SUMS

If diagnostic qualifies, also update:
`docs/vm_tlb/literature_notes/awma/problem_cards/R19_IBP_DIRECT_CONSUMER_PREPARATION.md`
with the exact selected design and its limits.

Push/fetch-back verify and clean worktree, then STOP.

Do not:
- run CUDA
- compile GPU code
- download Reddit dataset bytes
- start 109
- start Accel-Sim
- design hardware
- create another candidate.
