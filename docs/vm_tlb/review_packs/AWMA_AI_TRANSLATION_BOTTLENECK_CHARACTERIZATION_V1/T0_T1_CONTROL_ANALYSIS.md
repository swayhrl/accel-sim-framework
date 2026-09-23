# T0/T1 controls

| Target | V1 sensitivity | L1 hit rate | requester avg (cycles) | L1-service share | MSHR-wait share |
|---|---:|---:|---:|---:|---:|
| T0 Attention | 6.0099% | 97.835% | 21.42 | 46.69% | 31.65% |
| T1 GEMM | 0.1497% | 98.326% | 20.90 | 47.86% | 13.88% |
| T2 Decode GEMV | 10.3568% | 99.436% | 12.92 | 77.41% | 16.30% |

T1 generates far more translation completions than T2, yet only 0.15% of its global cycles disappear in the 0/80 control. The evidence therefore supports substantial latency overlap in the GEMM execution schedule; raw request volume is not a bottleneck proxy. T0 is intermediate: its 6.01% response is measurable, with both hit-path service and merged-request wait visible in the requester aggregate. T2 combines the largest global sensitivity with a 77.41% L1-service share, so decode exposes fixed hit-path latency more directly than either prefill control.

The overlap/scheduling interpretation is an inference from controlled cycle sensitivity plus source-identified aggregate counters. It does not alter the frozen `BASE_CONCURRENCY_MODEL_RESIDUAL` limitation.
