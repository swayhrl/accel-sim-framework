# ChatGPT Review — V4 Incomplete Matrix Scientific Decision

Date: 2026-09-20

Reviewed evidence:

- node164 recovery/review commit:
  `46de0c35e2c26fdabd9fc691370bedf0cc5974f5`
- accepted repaired VM requalification:
  `a7110f789a2bc6761d8885a2ca5628b4acf50f69`
- V4 runtime-load forensics:
  `c8657cf637c5b54a0f40135248ff1eabcfd66696`

## 1. Decision

The six historical V4 lookup-matrix launches are NOT accepted scientific points.

Reason:

- no terminal marker;
- no per-access coverage marker;
- node164 immutable evidence contains launch PIDs only;
- no complete receipt exists.

Therefore classify:

`V4_LOOKUP_MATRIX_PARTIAL_NOT_ADMITTED`

and:

`V4_FULL_MATRIX_PUBLICATION_SUPERSEDED`

Do not continue trying to reconstruct or publish the six-point V4 matrix.

The V4 runtime-load forensic result itself remains valid.

## 2. What remains accepted

The repaired per-access runtime remains accepted.

From:

`AWMA_REPAIRED_VM_REQUALIFICATION_20H_174NEW_V1 @ a7110f...`

accepted isolated Q05 points are:

```text
FORMAL_ISOLATED_REPAIRED_R0
cycles   = 1,654,548
coverage = 3,090,304 / 3,090,304 translated
untranslated = 0

FORMAL_ISOLATED_REPAIRED_I0
cycles   = 674,179
coverage = 3,090,304 / 3,090,304 translated
untranslated = 0
```

Accepted contextual repaired anchors also remain valid:

```text
P34 R0      = 1,619,068
P34 Q05-I0  =   758,082
P8 R0       = 1,675,884
```

These do NOT rescue the missing V4 lookup-latency matrix.

## 3. Why a minimal requalification is required

Lookup-latency decomposition was explicitly classified by the repaired requalification as:

`NOT_YET_REQUALIFIED`

Changing lookup service latency changes execution timing/schedule.

Therefore one cannot infer that a partial point would have preserved:

- natural completion;
- admission count;
- translated coverage;
- miss/hit behavior.

A complete rerun is required for any lookup-latency point admitted into the repaired scientific evidence chain.

## 4. Why the old six-point matrix should NOT be rerun

The current AWMA mainline question only requires determining whether repaired L1 hit-path sensitivity appears across representative kernel classes.

It does not require reconstructing the full historical V4 sweep.

Required comparison is:

```text
T0 Attention
T1 Prefill GEMM
T2 Decode GEMV
```

with a minimal common matrix:

```text
10/80  repaired natural
0/80   L1 lookup-zero diagnostic
0/0    zero-lookup residual diagnostic
```

Thus historical points:

- 5/80
- 2/80
- 10/40
- 10/0

are not required for the current mainline.

## 5. T0 comparison scope change

For cross-target validity, T0 should use an ISOLATED repaired screen, not the contextual P34 matrix.

Reason:

- T1/T2 are isolated target screens;
- same context class improves interpretability;
- accepted isolated repaired R0/I0 authority already exists;
- it avoids conflating predecessor state with cross-kernel hit-path validity.

P34 remains a separate realism/context anchor.

## 6. T0 minimal requalification

Use the already-qualified repaired + target-only lookup-override runtime.

First run a fresh disabled-control:

`T0_ISOLATED_10_80`

It must reproduce the accepted isolated repaired R0 authority under the same exact trace/runtime contract.

Expected anchor:

`1,654,548 cycles`

Require exact terminal and coverage markers.

If exact deterministic reproduction fails, STOP before latency diagnostics.

Then run:

- `T0_ISOLATED_0_80`
- `T0_ISOLATED_0_0`

Both require:

- natural completion;
- exact target identity;
- complete coverage;
- zero untranslated/unobserved;
- stable instruction/CTA completion.

The accepted isolated I0 = 674,179 may be reused as an external reference; no new I0 run is required.

## 7. T1/T2 common screen

After T0 passes, apply the same repaired runtime and same minimal matrix to:

- T1 PREFILL_GEMM_PRIMARY_OCC0
- T2 DECODE_GEMV_PRIMARY_STEP16

Each target:

- 10/80
- 0/80
- 0/0

All results are:

`REPAIRED_ISOLATED_SCREEN`

No mechanism claim.

## 8. Mainline decision

After T0/T1/T2 complete, compare:

- L1 hit rate;
- walk density;
- lookup density;
- `(cycles_10_80 - cycles_0_80) / cycles_10_80`;
- `(cycles_10_80 - cycles_0_0) / cycles_10_80`.

For T0 only also report:

- `TOTAL_I0_GAP = 1,654,548 - 674,179`;
- fraction of the I0 gap explained by 10/80 -> 0/80;
- 0/0 residual vs accepted I0.

The result informs simulator-model validity only.

No TLB/PTW mechanism is authorized.
