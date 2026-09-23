# REVIEW — RTX4080 Platform + V1 Mechanism Validation

Date: 2026-09-23

Authority reviewed:

`hrl/awma-174-rtx4080-platform-requal-mechanism-v1 @ 8af2c00e6361c53eaf7b02d5dab3ef9021925774`

## 1. Platform decision

Accepted:

`RTX4080_ADA_ACCELSIM_BASE_V1`

Frozen config SHA256:

`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`

Matched held-out requalification:

```text
H_CACHE   44.19%
H_STREAM  12.11%
H_COMPUTE 12.21%
median    12.21%
```

No point exceeds 2x error.

This is sufficient for AWMA memory/translation research.

Paper scope must remain explicit:

`QUALIFIED_FOR_AWMA_MEMORY_TRANSLATION_STUDIES`

Do not claim a universally cycle-accurate RTX4080 simulator.

The matched H_STREAM/H_COMPUTE points are small and launch-dominated; they do not independently establish full RTX4080 streaming-bandwidth or compute-throughput fidelity. This is a claim-scope note, not a reason to reopen platform tuning.

No further base-platform tuning is authorized unless a future mechanism result is shown to depend critically on a currently unsupported platform dimension.

## 2. Mechanism-sensitive evidence

Native:

```text
A1_CONTROL = 321
A8         = 338
A32        = 388
A32_W8     = 393 cycles/dependent warp-load step
```

Native ratios:

```text
A8/A1       = 1.0529595
A32/A1      = 1.2087227
A32_W8/A32  = 1.0128866
```

Simulator accessq cardinality:

```text
A1_CONTROL = 4 sector entries
A8         = 8
A32        = 32
A32_W8     = 32 per warp
```

Important scope:

A1 is one 128B-line trace-level opportunity but four 32B sector entries in the simulator coalescing contract.

Do not describe A1 as accessq-cardinality=1.

## 3. Legacy → V1 external semantic result

10/80 ratios:

```text
                         Native      Legacy      V1/V2R1
A8/A1                    1.0530      1.4862      1.0960
A32/A1                   1.2087      4.4392      1.5751
A32_W8/A32               1.0129      6.8517      3.3139
```

V1 clearly removes a large accessq-cardinality-dependent artificial serialization component.

Legacy → V1 median latency changes:

```text
A1      95.1211 → 65.1211
A8     141.3711 → 71.3711
A32    422.2617 →102.5742
A32_W8 2893.2207→339.9219
```

The benefit increases with active multi-entry opportunity, consistent with V1's semantic axis.

Accepted classification:

`V1_EXTERNAL_SEMANTIC_SUPPORT_PARTIAL`

V2R1 is numerically identical to V1 on this suite.

Accepted:

`V2R1_ADDS_NO_EXTERNAL_ALIGNMENT_BENEFIT`

## 4. Residual multi-warp mismatch is not primarily the V1 lookup-latency issue

V1 0/80 medians:

```text
A1      = 55.1211
A8      = 61.3711
A32     = 92.5352
A32_W8  =259.9883
```

Derived 0/80 ratios:

```text
A8/A1       ≈ 1.1134
A32/A1      ≈ 1.6788
A32_W8/A32  ≈ 2.8097
```

Native A32_W8/A32 is only 1.0129.

Therefore a large multi-warp/concurrency residual remains even when the modeled L1 lookup latency is zero.

Freeze this as:

`BASE_CONCURRENCY_MODEL_RESIDUAL`

Do not continue modifying V1/V2R1 or RTX4080 base parameters to chase it.

For future paper claims:

- treat absolute multi-warp Native alignment as a known limitation;
- continue to report 0/80 sensitivity when a proposed mechanism's benefit could be explained by lookup-latency amplification;
- do not claim the simulator reproduces all RTX4080 warp-concurrency behavior.

## 5. M0–M3 control scope

Exact contextual controls remain mechanism-inactive.

They show that the base simulator does not reproduce all Native working-set / multi-warp shapes exactly.

This is expected to remain a scope limitation.

Do not tune the platform or VM model against these controls now.

## 6. Baseline promotion decision

V1 is now a credible promotion candidate because:

1. the RTX4080/Ada base is qualified for AWMA scope;
2. V1 has accepted internal causal evidence on T0/T1/T2;
3. V1 has direct external mechanism-sensitive support;
4. V2R1 adds no further alignment benefit;
5. controller/correctness/quiescence gates are closed.

One final promotion gate remains:

> requalify the actual AI targets T0/T1/T2 on the frozen RTX4080 platform under Legacy and V1.

This is not infrastructure polishing. It is the final workload-level regression required before all future research uses V1 as the project baseline.

If that gate passes, promote a named baseline while preserving runtime switches:

`AWMA_RTX4080_SIM_BASELINE_V1`

Do NOT make V1 unconditional/default source behavior.

Legacy must remain selectable as a historical/control mode.

V2R1 remains diagnostic-only.

