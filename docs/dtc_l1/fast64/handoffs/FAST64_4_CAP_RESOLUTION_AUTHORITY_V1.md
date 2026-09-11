# FAST64.4 common lower-cap resolution authority

Status: **FROZEN FOR CAP-RESOLVED COLLECTION — candidate evidence only**

## Decision

The final common FAST64.4 lower-outstanding cap is **32768**.  This is the
smallest source-demonstrated non-binding common candidate; it is not selected
from IO/OO speedup.

The applicable source path is the global acquisition guard in
`src/gpgpu-sim/gpu-sim.cc`: it increments
`DTC_L1_lower_cap_full_events` and refuses a lower credit only when the
current global outstanding count is at the configured cap.  Therefore a
strict terminal row with zero events did not reach that guard and is
behaviorally cap-inert at every larger cap, provided payload, mode, Core,
runtime, observer, Framework, and all other config lines remain literal.
This is the sole reuse rule used below.

## Monotonic evidence

| workload / mode | cap | cap-full events | conclusion |
| --- | ---: | ---: | --- |
| 2DConvolution / IO | 8192 | 72,236 | bound diagnostic, excluded |
| 2DConvolution / IO | 16384 | 0 | inert at 16384 and above |
| Hotspot1 / IO | 16384 | 25,887 | still bound |
| Hotspot1 / OO | 16384 | 23,026 | still bound |
| Hotspot1 / IO | 32768 | 0 | non-binding |
| Hotspot1 / OO | 32768 | 0 | non-binding |
| Gaussian / Base, IO, OO | 16384 | 0 / 0 / 0 | inert at 16384 and above |
| LUD / Base, IO, OO | 16384 | 0 / 0 / 0 | inert at 16384 and above |

The two 16384 Hotspot records and the 8192 Core658 2D IO record remain
`CAP_BOUND_DIAGNOSTIC_NOT_PRIMARY_RESULT`; the 1048576 2D IO result remains a
control.  Neither enters the primary registry.

## Identity and reuse policy

The cap-resolution map has exactly 36 FAST12 Base/IO/OO cells and one formal
cap, 32768.  Each source is either:

- `REACQUIRED_AT_FINAL_CAP` for the two Hotspot modes; or
- `SOURCE_PROVEN_CAP_INERT_REUSE_TO_FINAL` from an observed smaller cap whose
  compact JSON records zero cap-full events.

No cap identity is implicit.  The collector pins this file's SHA and verifies
the literal source config ID and SHA per cell before it writes candidate
matrix output.

Triplet identity remains strict.  Core95/runtime462 is used for ATAX, BICG,
GESUMMV, Btree, Gaussian, Hotspot1, LUD, NN, and MRI-Q; Core658/runtime29a is
the narrow 2DConvolution triplet exception; GEMM and DWT2D retain their
complete literal bbcbb/runtime6a triplets under existing Stage3 source-reuse
authority.  No historical record is relabelled, and no Core95/Core658 or
historical/current identity is mixed within a triplet.

The Stage3 Base registry is historical characterization authority.  The
cap-resolved Stage4 registry below selects already strict terminal,
triplet-compatible evidence where that is required for formal performance
collection; it neither rewrites nor promotes a historical record by name.
