# Uninstrumented complete energy+force region

All 72 formal outputs passed the unchanged `5e-5` energy/force contract. Four groups, six samples per arm/group, five warmups per arm; wall and CUDA-event raw values are in `FORMAL_COMPLETE_TIMING.tsv`.

| Contrast | Median wall gap (baseline − candidate) | Median relative gain | Four-group classification |
|---|---:|---:|---|
| A0 → Aorder | -0.867 µs | -0.179% | MIXED |
| Aorder → Dready | 13.955 µs | 2.878% | CLEAR_FASTER |
| A0 → Dready | 14.845 µs | 3.065% | MIXED |

A0 → Dready has four favorable group directions but its median wall gap 14.845 µs is below 3× the larger-arm group-MAD estimate (15.469 µs). The CUDA-event comparison is CLEAR_FASTER but does not change the preregistered primary wall classification. Aorder isolates ready-state graph ordering: its A0 comparison is MIXED/near zero, not proof of no ordering effect. R21A's historical 4.7047% is retained separately and not pooled.
