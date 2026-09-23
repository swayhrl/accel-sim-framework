# REVIEW — RTX4080 Platform Qualification V1 + Mechanism-Sensitive Native V1

Date: 2026-09-23

## 1. Accepted node109 scientific closure

Authority:

`hrl/awma-109-mechanism-sensitive-native-calibration-v1 @ 6b75a3da3e3fedea6a359cd3657bf3e3fa2655d7`

The new `native_accessq_probe_v1` is accepted as a mechanism-sensitive calibration workload family.

Frozen primary Native medians:

```text
A1_CONTROL = 321 cycles/dependent warp-load step
A8         = 338
A32        = 388
A32_W8     = 393
```

Frozen relative Native behavior:

```text
A8/A1       = 1.0529595
A32/A1      = 1.2087227
A32_W8/A32  = 1.0128866
```

Trace-level mechanism opportunity is closed:

```text
A1  : 32 active lanes, 1 unique 128B line
A8  : 32 active lanes, 8 unique 128B lines
A32 : 32 active lanes, 32 unique 128B lines
A32_W8 : 32 unique 128B lines per warp instruction
```

Each configuration preserves:

`warmup occurrence0 → measurement occurrence1`

in one process/context, with zero drop/overflow, xz/grammar closure, and exact bracket counts.

Node109 did not run Accel-Sim.

This benchmark is ready for node174 simulator accessq-cardinality and Legacy/V1/V2R1 evaluation once the RTX4080 platform gate is recovered.

## 2. Node174 platform V1: engineering success, qualification evidence failure

Authority:

`hrl/awma-174-rtx4080-ada-platform-qualification-v1 @ 646844c513ba316eae4188cb517c2eef7282132d`

Implementation commit:

`aeec5b9a69865012b16ac0a6627143e29f1fee06`

Frozen final candidate config SHA256:

`de9ee8f30325c033e0de624640ffa8803f0eae40633eebaa0b3144f549f5ccb8`

The V1 decision:

`RTX4080_ADA_PLATFORM_NOT_QUALIFIED`

was correct under the predeclared gate, but it should be interpreted as:

`QUALIFICATION_EVIDENCE_INCOMPLETE_AND_ONE_VALID_OUTLIER`

rather than proof that the base model is grossly wrong.

Why:

- calibration P_L1 error = 4.50%;
- calibration P_L2 error = 21.78%;
- calibration P_DRAM error = 18.74%;
- hierarchy direction L1 < L2 < DRAM is correct;
- exercised SM89 subset terminates without unsupported opcode;
- exactly two bounded tuning passes were used;
- no research workload was used for tuning.

The held-out gate failed because:

- H_CACHE is valid and has 43.48% error;
- H_STREAM Native timing used 67,108,864 elements ×100 while its trace used 4,096 elements ×1;
- H_COMPUTE Native timing used 1,048,576 elements ×100 while its trace used 1,024 elements ×1.

Therefore 2/3 held-out error points are not scientifically comparable.

The V1 platform should NOT be retuned.

## 3. Minimal evidence repair

The cheapest scientifically clean repair is NOT to recapture giant traces.

The existing H_STREAM/H_COMPUTE trace kernels are already valid immutable scientific payloads.

Instead, node109 should measure Native execution for the exact existing trace-scale kernel launches:

- H_CACHE exact trace scale;
- H_STREAM exact trace scale = 4096 elements;
- H_COMPUTE exact trace scale = 1024 elements.

The host-side repetition count may be large (e.g. >=100) to stabilize the per-launch CUDA-event mean/median because repetition does not change the per-kernel launch semantics.

The same source/binary identity as the captured trace must be used.

This creates a matched Native-per-launch reference without changing or recapturing the trace.

## 4. No more platform tuning

After matched held-out Native timing exists, node174 must replay the frozen final candidate without changing any parameter.

Qualification then uses the original predeclared policy:

- median held-out absolute error <=25% → PASS;
- 25–35% → scoped PASS if trends remain credible and no essential point is >2× wrong;
- >35% median or gross trend mismatch → FAIL.

The existing H_CACHE 43.48% error is an outlier, not an automatic failure once three valid points exist. The gate is based primarily on median error plus gross-mismatch checks.

If PASS or scoped PASS is reached, immediately freeze:

`RTX4080_ADA_ACCELSIM_BASE_V1`

No further tuning is authorized.

## 5. Conditional science continuation

If and only if platform qualification becomes PASS/scoped PASS, node174 should continue in the SAME Goal to:

1. AWMA VM-overlay smoke;
2. exact M0–M3 contextual control cross-calibration on the RTX4080-like base;
3. actual accessq-cardinality closure for A1/A8/A32/A32_W8;
4. full mechanism-sensitive Legacy/V1/V2R1 matrix.

This avoids another infrastructure-only round.

The platform config must remain frozen throughout.

No parameter may be changed after looking at M0–M3 or A1/A8/A32/A32_W8.

