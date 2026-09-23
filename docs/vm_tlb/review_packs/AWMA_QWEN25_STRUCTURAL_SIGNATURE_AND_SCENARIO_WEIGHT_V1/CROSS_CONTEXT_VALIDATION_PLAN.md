# Cross-context validation plan

This is a design only. It does **not** authorize node109, a GPU capture, or an
Accel-Sim replay.

## Fixed comparison contract

Hold model revision, runtime/container, CUDA/PyTorch dispatch policy, FP16,
SDPA, profiler schema, CUPTI correlation method, and the V2 phase assignment
rule fixed. Each future census must emit the same full launch inventory and
structural catalog fields as V2/V1, including `UNKNOWN` where a correlation is
not source-supported.

The current reference is B=1, TEXT S2, Prefill=2048, Decode=32.

## Minimum future census matrix

| Purpose | B | Prefill tokens | Decode tokens | Input | Why it is minimally distinct |
|---|---:|---:|---:|---|---|
| Short-context | 1 | 256 | 32 | frozen TEXT A | Tests short-context shape/dispatch regime. |
| Long-context | 1 | 8192 | 32 | frozen TEXT A | Tests long-context shape/dispatch regime. |
| Batch | 4 | 2048 | 32 | frozen TEXT A replicated | Separates batch-driven dispatch/shape changes. |
| Content | 1 | 2048 | 32 | frozen TEXT B | Tests input-dependent routing/length-preserving differences. |
| Decode horizon | 1 | 2048 | 128 | frozen TEXT A | Tests whether the 32-step recurrence remains through later decode. |

The existing S2 census is the T2048/B1/TEXT-A baseline; no duplicate baseline
capture is needed. Each proposed point is a full CPU-correlation-aware census,
not a kernel-name sample.

## Reweight gate

The selector may retain the existing structural strata and recompute only
scenario-specific weights when all of the following hold against S2:

1. The phase/family/exact-implementation/grid/block stratum set is identical.
2. Every Decode step has the same per-stratum recurrence vector (or any
   documented intentional horizon extension uses the same vector after a
   separately reported warm-up boundary).
3. No new `UNKNOWN` attribution appears and no existing exact match loses its
   correlation evidence.
4. Lane C asset linkage status does not weaken for a selected stratum.

## Restratifcation gate

The selector must re-stratify, not merely reweight, if a test introduces or
removes an exact implementation, grid/block shape, phase class, decode-step
recurrence variant, splitkv/combine ratio, or CPU-correlation status. Any
batch/context/content-driven dispatch switch is a new structural stratum even
when its family name matches an S2 row.

## Interpretation boundary

The present 1,052 launches/Decode step and the observed long/normal GEMV and
splitkv/combine recurrences are `OBSERVED_STABLE_WITHIN_S2` only. They are not
evidence of layer count, Q/K/V role, or model-intrinsic shares. Performance
weights are always `SCENARIO_SPECIFIC`; cross-context portability remains
`UNTESTED_ACROSS_CONTEXT` until the designed census matrix is actually
authorized and completed.
