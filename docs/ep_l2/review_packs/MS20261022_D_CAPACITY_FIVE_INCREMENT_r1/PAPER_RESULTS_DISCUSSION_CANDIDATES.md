# English candidates for EN-v22; mother manuscript unchanged

**Results.** On the same diagnostic binary, jointly enlarging designated finite L2 resources and bypassing L2 data service yields OFF/ON speedups of 1.0926× for Conv, 0.9919× for CFD, 1.0604× for DWT, 1.0013× for SAD, and 1.7224× for Vector. The geometric mean over these five fixed inputs is 1.1466×. CFD remains an adverse result. These diagnostic comparisons use separate identities and are not pooled with the main61 S/F measurements or the incomplete original-seven MAIN aggregate.

**Conv localization.** Conv decreases from 292,932 to 268,117 cycles. The row and column kernels save 2,330 and 22,485 cycles, respectively, with the latter accounting for 90.61% of the observed elapsed reduction. Both kernels eliminate nearly equal lower-read byte counts (37.76 and 37.75 MB), despite their very different timing changes. Across the application, copy reads and writes each fall from 546,865 to zero, physical bank grants from 9,217,033 to zero, and lower-read and writeback traffic from 75.50 and 69.79 MB to zero. These observations localize the timing response but do not identify copy, capacity, or bank-service causal shares.

**Discussion and limits.** The intervention couples capacity expansion, retained residency under untimed host prefill, and data-service bypass. It is neither an independently identifiable capacity effect nor a hardware performance upper bound. Although no covered resource is observed binding, all ON runs retain an UNKNOWN classification because MissQ full-check coverage is incomplete. Native ROP storage is also outside the expanded resource vector. Request-wait counters overlap across requests, slices, and causes; they cannot be summed into application stalls. The unchanged and adverse phases, CFD slowdown, separate MAIN negative results, and incomplete MAIN denominator must remain visible.

## Claim review

- Supported: five same-binary accepted OFF/ON pairs; fixed-five diagnostic GM; Conv elapsed phase localization; exact reported service/traffic counters.
- Source interpretation: untimed host prefill and enlarged residency can explain absence of lower reads; source excerpt is separately cited in E_SOURCE_INDEX.json.
- Unidentified: independent capacity-versus-data-service gains; copy-benefit fraction; per-request critical paths; V/RO contributions in this traditional-S diagnostic.
- Unsupported: limitless L2, hardware upper bound, all resources proven nonbinding, numerical-output correctness from drain alone, a complete seven-input MAIN GM, or substituting diagnostic ON for MAIN F.
