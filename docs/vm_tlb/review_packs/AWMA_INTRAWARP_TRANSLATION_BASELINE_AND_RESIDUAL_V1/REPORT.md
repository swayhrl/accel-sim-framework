# AWMA_INTRAWARP_TRANSLATION_BASELINE_AND_RESIDUAL_V1

Status: **COMPLETE**

Judgement: **CLASSIC_INTRAWARP_CAPABILITY_COVERS_CURRENT_BENEFIT**

The single classic same-dynamic-warp-instruction VPN de-duplication reference covers exactly the same frozen PREL1 follower request set on all seven accepted targets; it matches PREL1 cycles on A1/A2/T2 and is faster on T0/T1/SPLITKV/COMBINE, with timing-induced service interleaving differences explicitly retained. This is a result for the current RTX4080/V1 evidence set, not a theorem of equivalence to any paper or all LLM workloads.

## Equal-condition results

| Target | OFF | Reference | Frozen PREL1 | Ref reduction | PREL1 reduction | Intersection / PREL1 | Residual cycles |
|---|---:|---:|---:|---:|---:|---:|---:|
| T0 | 527896 | 488559 | 499441 | 7.452% | 5.390% | 2722464 / 2722464 | -10882 |
| T1 | 665802 | 619514 | 647437 | 6.952% | 2.758% | 6629952 / 6629952 | -27923 |
| T2 | 93079 | 94034 | 94034 | -1.026% | -1.026% | 132544 / 132544 | 0 |
| SPLITKV | 73923 | 72817 | 73915 | 1.496% | 0.011% | 218862 / 218862 | -1098 |
| COMBINE | 10480 | 10462 | 10480 | 0.172% | 0.000% | 1016 / 1016 | -18 |
| A1 | 114123 | 115415 | 115415 | -1.132% | -1.132% | 116032 / 116032 | 0 |
| A2 | 117698 | 115700 | 115700 | 1.698% | 1.698% | 116032 / 116032 | 0 |

Cycle reduction is `(OFF-reference)/OFF`; negative values are regressions. Structural coverage is not independently interpreted as performance savings.

## Identity and observer boundary

The accepted passive observer at `6441fe9f91266220a52587c0313fb767007b5d92` supplies the reused instrumented-OFF evidence. Exact PREL1/reference membership is computed in one PREL1 observer run per target, so it does not infer set equality from aggregate counts or raw cross-run UIDs. The auxiliary CTA/warp/ordinal digest is diagnostic only and differs on T0/T1/SPLITKV under changed scheduling; target trace hashes, logical instruction/CTA coverage, co-observed membership, and functional mapping digests are the authoritative identities.

## Boundaries

No gem5, CAC, LATPC, extra paper mechanism, trace recapture, 109 run, platform change, or frozen PREL1 change was performed. The reference is an AWMA simulator adaptation. It retains V1 translation ports, latencies, MSHR/PTW/PWC/PTE behavior and only changes same-instruction request generation.

## Consumer consequence

There is no positive PREL1 performance increment beyond the classic reference in these seven targets. The reference is faster on four targets, so timing/service differences remain measured symptoms rather than a novel residual benefit. The accepted conclusion is the bounded `CLASSIC_INTRAWARP_CAPABILITY_COVERS_CURRENT_BENEFIT`; it does not establish novelty or literature equivalence.
