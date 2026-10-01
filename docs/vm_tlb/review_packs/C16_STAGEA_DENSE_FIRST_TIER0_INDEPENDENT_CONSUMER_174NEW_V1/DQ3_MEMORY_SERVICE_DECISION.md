# DQ3 — Tier0 memory/service screen

The independent screen uses only correlated raw CUDA family unions, the admitted native request endpoint, observed shape, and actual kernel names (FlashAttention, CUTLASS or Marlin). A name/weight layout is a **clue**, not measured service latency. The local candidate label does not distinguish L1, L2, DRAM or TLB.

| Point | Family | Graph-OFF family/full-request CUDA-union f | Kernel/layout clue | Local Tier0 screen |
|---|---|---:|---|---|
| MP01 | ACTIVATION | 2.092893% | NO | NO_MEMORY_SERVICE_CANDIDATE |
| MP01 | ATTENTION | 16.644119% | YES | MEMORY_SERVICE_CANDIDATE_FOR_TIER1_REVIEW |
| MP01 | DOWN_PROJECTION | 25.415299% | YES | MEMORY_SERVICE_CANDIDATE_FOR_TIER1_REVIEW |
| MP01 | GATE_UP_PROJECTION | 51.815746% | YES | MEMORY_SERVICE_CANDIDATE_FOR_TIER1_REVIEW |
| MP05 | ACTIVATION | 1.886937% | NO | NO_MEMORY_SERVICE_CANDIDATE |
| MP05 | ATTENTION | 21.379281% | YES | MEMORY_SERVICE_CANDIDATE_FOR_TIER1_REVIEW |
| MP05 | DOWN_PROJECTION | 18.356990% | YES | MEMORY_SERVICE_CANDIDATE_FOR_TIER1_REVIEW |
| MP05 | GATE_UP_PROJECTION | 35.447764% | YES | MEMORY_SERVICE_CANDIDATE_FOR_TIER1_REVIEW |

ATTENTION, GATE_UP_PROJECTION and DOWN_PROJECTION remain local *review* candidates at MP01/MP05; ACTIVATION is below the 3% screen. However MP02 and MP03 failed correctness, so the full DQ3 question is `QUESTION_INCOMPLETE`; no Tier1 is authorized or executed. The Graph-OFF f is not a Graph-ON local contribution, and the 2% whole-run ceiling is `WHOLE_RUN_CEILING_NOT_IDENTIFIABLE`. These rows are not bottleneck attributions or project-level survivors.
