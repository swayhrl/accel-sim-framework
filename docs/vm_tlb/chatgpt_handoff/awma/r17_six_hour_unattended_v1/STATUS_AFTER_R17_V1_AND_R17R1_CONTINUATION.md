# Status after R17 V1 and authorized R17R1 continuation

Date: 2026-09-30

## Lane F R17 V1

Execution authority:
- branch: hrl/awma-r17-graph-search-native-109-v1
- commit: 78874fbfd767ec1321d41a04e4c51589a3c07298
- tree: cc327ceca36b4d7ee271ceffb92f3feed360c70f

Formal label:
R17_RECALL_GATE_NOT_QUALIFIED

Interpretation:
- real GloVe input and the first CAGRA index qualified;
- no formal performance conclusion was reached;
- the bounded Q1 quality grid peaked at recall@10=0.930078 <0.95;
- this is a baseline quality-qualification stop, not a graph-search negative.

Further source review found two baseline gaps:
1. the prior Q1 strong grid only extended MULTI_CTA to itopk=256 and search_width<=2, while official cuVS CAGRA search configuration uses itopk through 512 and search_width through 64;
2. the prior index used the Python runtime default IVF_PQ build, whereas stable cuVS benchmark base configuration uses NN_DESCENT.

Therefore one bounded R17R1 requalification is authorized without lowering recall.

R17R1 handoff:
- branch: hrl/awma-r17r1-quality-requalification-handoff-v1
- HEAD: 35ae51220bdde8adccfddde847356a65578d465d
- execution branch: hrl/awma-r17r1-quality-requalification-109-v1
- goal: docs/vm_tlb/chatgpt_handoff/awma/r17r1_quality_requalification_v1/LANE_F_R17R1_QUALITY_REQUALIFICATION_109_GOAL.md

## Lane G

Execution authority:
- branch: hrl/awma-r17-graph-search-related-work-cpu-v1
- commit: f72aca7938a1b2e8bb2f62953e308444babd8489

Final outcome:
NO_SECOND_CANDIDATE_QUALIFIED

Accepted novelty boundary:
- sequential discovery has direct prior work, especially FlowANN;
- CAGRA already addresses low-query parallelism via MULTI_CTA;
- ALGAS addresses query bubbles / persistent launch;
- resident R17 remains only a narrow empirical boundary after these capabilities.

Lane G remains STOP. Do not invent a second candidate merely because unattended time remains.

## Current lanes

- Lane F / 109: R17R1 authorized
- Lane G / CPU: STOP
- Lane E / 174-new: STOP

No hardware mechanism or simulator work is authorized.
