# C11 C5 Prefill Provenance Closure — final report

## Final state

`C11_C5_INPUTS_CLOSED_READY_FOR_C5_REVIEW`

C11 closes the C5 full-ROI input/provenance gate for the frozen M4B candidate.
It does **not** authorize, start, or report a C5 performance replay.  The labels remain
`SPECULATIVE_CANDIDATE`; F1/F8 remain `REFERENCE_APPROX_SUBENTRY_16`.

## What is frozen

- Prefill list SHA-256 is
  `a40d6832219e5b0a6232875bb181754ac121bb5f867c9b13c84370e2a2cb6e6f`
  (692 entries); decode1 is
  `b6c42eb1932fcacefc2429b91a2015d38003a764a5319fe4bcbaf65b3d0cd0dc`
  (740 entries).  Each entry exists under its frozen A trace root; C owns
  byte-identical provenance-bound list manifests.
- The runtime binder sidecars prove a privileged `weight-flat-rank0` allocation for
  each ROI.  Only its 15,442 complete 64-KiB pages are registered.  The trailing
  4 KiB remains conventional.
- `C5_MODELED_PA_HIGH_UNUSED_BIT_V1` maps each admitted page with the fixed,
  non-performance-tuned offset `0x0000c00000000000`.  This is explicitly
  `MODELED_DRIVER_PA`, not measured hardware PA.  It is nonidentity, nonwrapping,
  contiguous, and proven placement-neutral for the frozen C5 decoder.
- The two C5 V2 registrations have independent ROI allocation/sidecar provenance
  and hashes: prefill `6ae0e18cc3bba29871002c4ff1877052489740163424723a845ead45c4a5f4b0`,
  decode1 `3dc77c1f348028ba7b8abfef3dc6c4cffa0c9678f003bc23bdc9158d62762b48`.
- The primary matrix has 22 points: F0/F1/F2/F5/F9 plus F7/F8 at Lseg 5/10/20,
  for prefill and decode1.  F6 remains an omitted diagnostic because C9 has no
  comparable approved 2-MiB driver PA mapping.  H0 is absent and rejected.

## Common-PA fix and proof

Audit exposed an invalid comparison risk: a non-Segment fair arm discarded the V2
registration path and could fall back to identity-like page-table mapping.  Core
commit `87ff9a3d0ca733c96ea8e526c3621b22a1b32eae` minimally makes V2 registration
the shared driver PA backend for conventional PTW and Segment, while the Segment
lifecycle still controls only the bypass.  It preserves the registration path when
fair-arm selectors disable Segment.  No C9 capacity, topology, timing point, or
fairness budget changed.  Test binding to the real full-ROI allocation starts is
`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`.

`COMMON_PA_FAIRNESS_VALIDATION.tsv` proves F0/PTW, F7 and F8 return the same
nonidentity modeled PPN for both ROIs without `OBJECT_WEIGHT`.  The object map
remains telemetry-only.

## Build and validation binding

Execution/config source anchor: Framework
`d64408a97d76a320a6d49468653d416e33677af8`; Core
`57bb71ecd015b6ec0ab32e45b0815e5beaf69172`; linked binary SHA-256
`2351f67bba60d333fdcc08b4cea81f39082958da67982d497ee8b4d83f321d3a`.

The input validator, full single-worker link, full-ROI common-PA directed test,
registered-Segment regression, fair-arm sanity, and object-attribution conservation
test all pass.  The only compile failure in C11 was a missing existing CUDA include
path for the object-attribution test; adding `-I/usr/local/cuda-11.8/include` fixed
the test harness invocation without source change.  Details and commands are in
`VALIDATION_RESULTS.tsv`.

## Required next gate

An independent C5 execution/review decision must first recheck the exact hashes in
`C5_ARM_MATRIX.tsv`, `C5_COMMAND_MANIFEST.tsv`, and `C5_ACCEPTANCE_MATRIX.md`.
It must obtain the shared resource slot and obey the declared resume and conservation
rules.  This C11 closeout neither creates a C5 output directory nor runs a simulator
trace.  KV segmentation, 12K, M5, and all Window A changes remain out of scope.
