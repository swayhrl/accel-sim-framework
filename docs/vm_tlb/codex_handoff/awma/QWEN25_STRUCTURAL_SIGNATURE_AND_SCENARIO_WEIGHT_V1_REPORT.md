# Qwen2.5 structural execution signature and scenario weight V1

Stage: `AWMA_QWEN25_STRUCTURAL_SIGNATURE_AND_SCENARIO_WEIGHT_V1`
Status: COMPLETE — offline analysis only; no capture and no Accel-Sim replay.

## Authorities

- Lane A V2: `hrl/awma-qwen25-s2-census-reclass-v2 @ 24f21db0aa921190ca40e4d3969aced7471347b6`.
  Its full inventory hash is
  `222d5dfeeb1e7aaae3423f13873053c37c27f5c6290d8a58bd3186a0803ca77a`.
- Lane C (read-only): `hrl/awma-existing-ai-sim-trace-coverage-audit-v1 @ 03924689da9c9691501d93567365c9265178b8a5`.
  Its `ASSET_INVENTORY.tsv` hash is
  `7041c0aedc6e5c066530f4a412192fee9011c69301018b15e4e829c963cdeed0`.

Every time weight in this result is bound to exactly
`B=1; Prefill=2048; Decode=32; FP16; SDPA; TEXT S2`. It is not a model-wide
or architecture-intrinsic performance share.

## A. Structural execution signature

The catalog has 100 observed exact phase/family/implementation/grid/block
strata and nine deliberately unjoined Lane C `NATIVE_ONLY` rows. The latter
have unknown exact implementation and shape, so they are preserved as
provenance rather than treated as simulator coverage for any V2 stratum.

- One observed Prefill pass contains **980** kernel launches.
- Every one of the 32 observed Decode steps contains **1,052** kernel launches.
- The decode total is therefore `33,664 = 1,052 × 32` launches. This is
  `OBSERVED_STABLE_WITHIN_S2`, not a layer or operator inference.
- Long GEMV (`grid=1216,1,1`, `block=16,4,1`) recurs **48/step** with count,
  implementation set, and shape set stable over all 32 S2 decode steps.
- The distinct 224×1×1 GEMV shape with block 16×4×1 recurs **24/step**; other
  observed GEMV shapes are separately cataloged and are not merged by name.
- Decode splitkv (`grid=1,9,14`, `block=128,1,1`) and combine
  (`grid=2,1,1`, `block=128,1,1`) each recur **24/step** across the 32 observed
  steps.

The recurrence of 24, 48, or any other count is only a measurement. The
catalog does not assign Q/K/V, transformer-layer, or operator semantics from
that pattern.

For Prefill there is one observed pass, so recurrence across passes is
`SCENARIO_SPECIFIC`; a single pass cannot establish structural stability. All
cross-context assertions are `UNTESTED_ACROSS_CONTEXT`. Auxiliary work is
retained but is `DATA_DEPENDENT_NOT_APPLICABLE_OR_UNKNOWN` for pass/step
recurrence.

## B. Scenario-specific performance weight

| S2 phase | GPU duration (ns) | Full-S2 GPU-time share |
|---|---:|---:|
| PREFILL | 32,229,639 | 20.809841% |
| DECODE | 122,454,407 | 79.065632% |
| AUXILIARY | 192,864 | 0.124527% |

Within Prefill, `CUBLAS_GEMM` accounts for 23,620,241 ns (73.287327% of
Prefill; 15.250976% of full S2) and `PYTORCH_FLASH_FWD` for 3,624,299 ns
(11.245236% of Prefill; 2.340116% full S2). Within Decode, `CUBLAS_GEMV`
accounts for 60,929,146 ns (49.756597% of Decode; 39.340368% full S2),
`PYTORCH_FLASH_FWD` for 12,088,660 ns (9.871968% Decode), and the material
elementwise/copy families remain separately represented in the catalog.

The per-stratum table supplies phase, family, and exact-function+shape weight
at the same scenario binding; it is the selector-facing input, not a claim of
portable workload proportions.

## Lane C asset linkage

The exact-safe join uses phase + normalized family + narrowly normalized
implementation kind + grid + block. It produces 3 `REUSABLE_NOW`, 2
`REQUIRES_REQUALIFICATION`, and 95 `MISSING_SIM_TRACE` structural rows. The
nine Lane C `NATIVE_ONLY` entries remain explicit unmapped catalog rows because
their exact function/shape fields are UNKNOWN; native evidence is not silently
converted into simulator-native coverage.

`REUSABLE_NOW` includes the accepted T0 Prefill Flash, T1 Prefill GEMM, and T2
long Decode GEMV shapes. Existing splitkv/combine and additional GEMV payloads
appear as `REQUIRES_REQUALIFICATION` only where their exact join fields match.

## What later scenarios must test

Features closer in theory to source/model structure include the declared
forward graph and supported tensor-rank/shape regimes, but this census alone
does not establish them as invariant. The S2-stable records above are empirical
only. Context length, decode horizon, batch size, and content can change tensor
shapes, implementation dispatch, shape variants, recurrence, and weights.

The minimum future census design, decision gates for reweight versus
restratification, and its explicit no-execution boundary are in
`CROSS_CONTEXT_VALIDATION_PLAN.md`.
