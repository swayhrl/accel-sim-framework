# REVIEW — AWMA RTX4080 V1 Baseline Final Acceptance

Date: 2026-09-23

Final authority:

`hrl/awma-174-rtx4080-v1-baseline-promotion-v1 @ 8d1f14a32f5538660d74da86ccb03a2c504c5735`

## 1. Final baseline decision

Accepted and frozen:

`AWMA_RTX4080_SIM_BASELINE_V1_PROMOTED_WITH_SCOPE`

Named baseline:

`AWMA_RTX4080_SIM_BASELINE_V1`

Definition:

- platform: `RTX4080_ADA_ACCELSIM_BASE_V1`
- platform config SHA256:
  `de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`
- primary VM overlay: model-relative `10/80`
- V1 frontend:
  `GPGPUSIM_PIPELINED_ACCESSQ_TRANSLATION_LAUNCH=1`
- READY-application V2:
  `GPGPUSIM_READY_APPLICATION_V2=0`
- Legacy remains a selectable historical/control mode
- `0/80` remains the diagnostic companion
- V2R1 remains diagnostic-only
- Segment F0 remains dormant
- source-wide unconditional defaults remain unchanged

From this point onward, new AWMA mechanism experiments must use this baseline authority unless a new correctness contradiction is discovered.

Do not re-open the platform/V1/10-80 baseline merely because a later proposed mechanism has disappointing performance.

## 2. AI promotion matrix

All 12 T0/T1/T2 × Legacy/V1 × 10/80/0/80 points pass correctness/identity/coverage/quiescence.

Accepted cycles:

| Target | Legacy 10/80 | Legacy 0/80 | V1 10/80 | V1 0/80 |
|---|---:|---:|---:|---:|
| T0 | 1,035,626 | 475,330 | 527,896 | 496,170 |
| T1 | 1,413,880 | 622,016 | 665,802 | 664,805 |
| T2 | 95,835 | 83,665 | 93,079 | 83,439 |

Sensitivity:

| Target | Legacy | V1 |
|---|---:|---:|
| T0 | 54.10% | 6.01% |
| T1 | 56.01% | 0.15% |
| T2 | 12.70% | 10.36% |

Legacy→V1 10/80 improvement:

```text
T0 = 49.03%
T1 = 52.91%
T2 =  2.88%
```

Interpretation:

- T0/T1 Legacy behavior was strongly dominated by the artificial accessq-head translation-launch serialization corrected by V1.
- T2 contains little of that artifact and therefore remains the most interesting current AI target for genuine post-baseline translation characterization.
- The V1 improvement is a simulator-baseline correction, not a proposed architecture-mechanism speedup. Do not report it as the final paper contribution.

## 3. Scoped zero-latency divergence

T0/T1:

```text
T0 Legacy0→V10 delta = 4.38%
T1 Legacy0→V10 delta = 6.88%
```

Accepted attribution:

`V1_PRELAUNCH_READY_UNAPPLIED_ORDERING_RESIDUAL`

V1 launches resident translations before head consumption but does not consume READY results.

This increases lookup activity while preserving:

- accepted unique UID;
- complete translated coverage;
- zero untranslated/unobserved;
- zero side-effect duplication;
- Segment dormancy;
- terminal quiescence.

This residual is part of the baseline scope and is not a reason to reopen V1.

## 4. Known simulator limitations

Freeze:

`BASE_CONCURRENCY_MODEL_RESIDUAL`

Mechanism-sensitive Native vs V1 still differs strongly for the high-concurrency A32_W8/A32 ratio, including under 0/80.

Therefore:

- do not claim universal RTX4080 warp-concurrency fidelity;
- when a future mechanism gains mostly under high warp concurrency, explicitly check whether the gain persists under the 0/80 diagnostic and is not merely amplifying this residual;
- do not tune the base platform or V1 to chase the A32_W8 Native ratio.

Platform scope:

`QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`

not universal cycle-accurate RTX4080 fidelity.

## 5. Important paper framing

The completed infrastructure should appear in a paper as methodology / validation, not as the architecture contribution.

A clean paper story is:

1. qualify a scoped RTX4080/Ada simulation platform;
2. identify and remove a simulator frontend serialization artifact;
3. freeze a validated research baseline;
4. characterize translation behavior under AI workloads;
5. propose a mechanism only if the characterized bottleneck is substantial and reproducible;
6. evaluate the mechanism against the frozen V1 baseline.

Do not claim speedup against Legacy as mechanism benefit.

## 6. Next scientific question

The baseline phase is complete.

The next question is:

> under the corrected V1 baseline, where is translation latency actually exposed in representative AI kernels, and is the remaining opportunity large/structured enough to justify a new TLB/PTW mechanism?

This should be answered before mechanism implementation.

