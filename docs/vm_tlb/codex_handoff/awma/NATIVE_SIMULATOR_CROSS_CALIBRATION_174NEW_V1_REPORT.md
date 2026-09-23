# Native ↔ Simulator Cross-Calibration 174-new V1 Report


Native establishes strong M0→M1 working-set exposure and an exact M1→M2 relative change of -4.5840%. All three simulator semantics produced identical scientific results in this matrix. At 10/80 their captured-bracket means were M0=80.601562, M1=672.851562, and M2=1255.004089 cycles/dependent-step: M1/M0=8.347872, but M1→M2=86.5202%. The working-set direction is Native-consistent; the large positive concurrency change contradicts the Native exact pair's modest negative change.

The controlled microtraces do not distinguish Legacy, V1, and V2R1. Existing accepted AI-target evidence still shows that V1 removes most Legacy frontend amplification for T0/T1, while V2R1 adds no benefit beyond V1 for T2. Combined evidence is mixed rather than a basis for fitting parameters.

Classifications:

- `MIXED_NATIVE_SIMULATOR_ALIGNMENT`
- `V1_NATIVE_ALIGNMENT_PARTIAL`
- `V2R1_ADDS_NO_NATIVE_ALIGNMENT_BENEFIT`
- `LEGACY_FRONTEND_AMPLIFICATION_EXTERNALLY_SUPPORTED=PARTIAL`

No `BASELINE_PROMOTION_CANDIDATE` is issued because the exact controlled concurrency shape remains inconsistent. No Native ns↔simulator-cycle fit, RTX4080 TLB latency/capacity claim, hardware page-size claim, or latency tuning is made.

Publication scope: calibration/validation only. Baseline promotion was not performed.
