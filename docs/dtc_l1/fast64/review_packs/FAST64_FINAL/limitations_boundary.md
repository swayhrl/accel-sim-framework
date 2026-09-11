# FAST64 limitations and evidence boundary

Status: **FROZEN FINAL-SYNTHESIS INPUT — NOT A NEW PERFORMANCE RESULT**

FAST64 evaluates the implemented DTC mechanism and its causal performance
trends on a frozen trace-driven Accel-Sim platform.  It is not a numerical
reproduction of the dissertation's original Unified-Cache GPGPU platform or a
claim of any published aggregate percentage.

## Explicit platform and workload differences

- The thesis scaling anchor is the original 2-SM Unified-Cache GPGPU.  FAST64
  uses a frozen 64 clusters × 1 core trace-replay shell with 20 memory
  partitions and a 16-KiB/4-way/128-B DTC Base model; see
  `handoffs/FAST64_1_PLATFORM.md`.
- FAST64's primary payload is the frozen 12-member FAST12 set of exact ordered
  C2P canonical trace members.  Its provenance label is
  `C2P_CANONICAL_TRACE_REUSED_FOR_DTC_FAST64`; it must never be relabelled as
  a dissertation-exact workload/input payload.
- The primary performance result is exactly the accepted FAST12 Base/IO/OO
  matrix and `GM-FAST12`.  Heavy M5 ATAX, SYR2K, 2MM, SpMV, and Extended-20
  evidence is retained under Tier A/C dispositions and is never numerically
  merged into FAST64 aggregates.
- Core-95 is the formal repaired identity for new non-2D rows.  The
  source-backed Core658 exception is limited to the common 2DConvolution
  triplet.  Historical telemetry Core rows retain their original identity and
  are not silently relabelled.

## Claim boundary

FAST64 supports mechanism correctness, structural-pressure characterization,
and bounded Base/IO/OO trend evidence under these frozen identities.  It does
not support a claim of dissertation-exact absolute cycles, platform match, or
published `+22%`/`+30%` numerical reproduction.  Negative and zero results are
retained in the accepted matrices and are not filtered from aggregates.

Tier A may support implementation and observer confidence; Tier C may support
auxiliary robustness discussion.  Neither tier becomes a FAST64 result without
an explicit exact-identity acceptance path.
