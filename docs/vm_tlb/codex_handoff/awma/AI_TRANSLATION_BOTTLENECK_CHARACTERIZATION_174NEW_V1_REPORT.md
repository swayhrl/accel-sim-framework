# AI Translation Bottleneck Characterization

## Outcome

Under the permanently frozen `AWMA_RTX4080_SIM_BASELINE_V1`, T2 Decode GEMV is classified `HIT_PATH_EXPOSURE_DOMINANT`; modeled-page behavior supports `PAGE_REUSE_OPPORTUNITY_SUPPORTED`. The evidence does not support L2-miss, PTW-service, translation-queueing, or walker-concurrency dominance. No mechanism was designed or implemented.

## Frozen authority and matrix

- platform config SHA256: `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- V1: pipeline launch=1, READY Application V2=0
- primary VM: 10/80; diagnostic companion: 0/80
- formal matrix: T0/T1/T2 × V1 10/80 and V1 0/80 = six accepted terminal points
- ideal control: not included; no accepted source-identified ideal/near-ideal latency control was found
- all target identities, instructions, CTA, UID coverage, zero untranslated/unobserved, dormant Segment F0, and controller quiescence remain PASS

No platform, VM, TLB, or V1 semantic parameter was changed.

## Controlled sensitivity

| Target | 10/80 cycles | 0/80 cycles | sensitivity |
|---|---:|---:|---:|
| T0 Attention | 527,896 | 496,170 | 6.0099% |
| T1 GEMM | 665,802 | 664,805 | 0.1497% |
| T2 Decode GEMV | 93,079 | 83,439 | 10.3568% |

T2 is the largest exposed translation-latency target, T0 is a measurable secondary control, and T1 is a low-sensitivity overlap control.

## T2 attribution

At 10/80, T2 has a 99.436% L1 hit rate. L1 service contributes 77.41% of aggregate requester latency; MSHR wait contributes 16.30%; L2 service and queueing together contribute 4.23%. Walk starts/completions are 134/134, MSHR high-water mark is 9, and both MSHR-full and PWQ-full events are zero. This supports hit-path exposure with secondary merged-request wait. It does not support a PTW-, queue-, or walker-dominant label.

T1 has much larger aggregate request volume but only 0.15% global sensitivity, supporting strong GEMM scheduling overlap. T0's 6.01% sensitivity is intermediate. These comparisons explain why request volume alone does not predict exposed translation time.

## Page behavior and evidence limits

At modeled 64KiB, T2 touches 134 pages and its busiest 10% of pages carry 54.91% of references. This supports reuse/concentration as a behavioral opportunity. The 4KiB companion is not a real-RTX4080 page-size assertion.

The accepted aggregate telemetry does not expose cycle-window burst histograms, per-PC stall attribution, or PWQ/walker/lookup occupancy high-water marks. Those categories are explicitly marked `NOT_AVAILABLE_WITHOUT_SEMANTIC_INVENTION`; zeros are used only for actual source counters such as full events or final quiescence. T0 and T2 diagnostics OFF/ON scientific signatures match exactly.

## Stop boundary

Characterization is complete. Mechanism design is intentionally deferred to ChatGPT/user review.
