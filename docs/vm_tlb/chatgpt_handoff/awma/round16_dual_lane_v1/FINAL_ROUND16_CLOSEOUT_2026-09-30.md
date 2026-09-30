# Round16 final closeout

Date: 2026-09-30

## Final lane status

### Lane F / VLA RTC-VJP
Formal execution label:
`VLA_VJP_RESULT_MIXED_NEEDS_REVIEW`

Project interpretation:
`VLA_VJP_WORKLOAD_REAL_ARCH_RESIDUAL_NOT_QUALIFIED`

The repaired full-network VJP is a real and material inference-time workload phenomenon, but the removable state/lifetime share was not isolated above the architecture-investment gate. No hardware line is admitted.

### Lane G / R102 real updates
Formal execution label:
`R102_REAL_UPDATE_INPUT_AUTHORITY_NOT_QUALIFIED_V2`

Project interpretation:
`R102_DORMANT_WAITING_FOR_REAL_UPDATE_AUTHORITY`

CUDA=0. This is not a GPU implementation negative. Reopen only when authoritative adjacent working-precision versions or an authoritative reconstructible real patch chain becomes public/available.

### Lane G side lane / exact loss
First-stage formal label:
`EXACT_LOSS_STATE_LIFETIME_RESIDUAL_PRESENT`

Follow-up software-counterfactual authority:
- branch: `hrl/awma-exact-loss-cce-zero-init-removal-109-v1`
- commit: `ec1ccad7bbcead8853cd97840a2007d96f325aa3`
- tree: `12c970119edc5ee68c08e7ac1e497ef8f603ada5`

Final formal label:
`CCE_ZERO_INIT_SOFTWARE_REMOVABLE`

Accepted facts:
- frozen real Qwen shape B=1,T=255,H=896,V=151936,BF16
- C1 reuses the existing 66,472-byte dC lock array
- no full-size shadow buffer
- all-ignore fallback preserves original zero semantics
- identical fixed CCE heuristic meta parameters and FP32 dC accumulation
- directed qualification and real full-gradient qualification pass
- C0 median 8.171520 ms
- C1 median 7.202816 ms
- paired improvement 0.968704 ms / 11.85 percent
- accepted 0.751779 ms zero-fill anchor recovery 128.85 percent
- NSYS proves the old full-dC zero fill is absent
- no equivalent full-size initialization pass appears
- small state reset is 864 ns
- mandatory FP32-to-BF16 cast, CCE backward and LSE remain

Scientific conclusion:

> The previously observed greater-than-5-percent classifier-gradient zero-initialization residual is primarily a software accumulation-organization artifact on the frozen real shape. A bounded first-contributor initialization protocol removes the full pre-zero and materially improves the complete operator while preserving the full-gradient contract.

Therefore the exact-loss state/lifetime hardware line is **closed in this scope**.

No second shape is required by the preregistered gate. A future separate study may revisit loss heads only if a new natural workload independently exposes a residual after this software organization; do not reopen merely to search for a positive shape.

## Round16 overall outcome

Round16 exercised three different stop paths:

1. real scientific input unavailable -> stop before GPU (R102)
2. real workload phenomenon present but architecture residual not isolated -> stop before mechanism (VLA VJP)
3. apparent architecture-sized residual survives strong baseline but is then removed by a bounded software counterfactual -> close as software organization (exact loss)

This reinforces the AWMA exploration rule:

```
real phenomenon / real input
-> semantic and identity qualification
-> ideal or bounded headroom
-> strong software baseline
-> bounded software counterfactual
-> only surviving residual may enter architecture review
```

Counts, traffic, state size, or profiler percentages do not by themselves qualify an architecture mechanism.

## Current execution state

- Lane E / 174-new: STOP
- Lane F / 109: STOP
- Lane G / 109: STOP
- no authorized hardware mechanism
- no authorized second shape/model
- no authorized Accel-Sim follow-up

Next work should return to problem discovery / literature-guided candidate selection rather than extend Round16.
