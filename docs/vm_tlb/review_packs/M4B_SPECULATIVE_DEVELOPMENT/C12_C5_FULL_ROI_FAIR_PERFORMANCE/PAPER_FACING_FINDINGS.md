# C12 / C5 paper-facing findings

## MEASURED_FULL_ROI_FACT

- 22/22 frozen C5 arms terminally passed the parser/conservation contract.
- All reported speedups are relative only to the same-ROI C5 F0 baseline in `SPEEDUP_SUMMARY.tsv`.
- Full counters are preserved in `ARM_RESULTS.tsv`, `TRANSLATION_MECHANISM_SUMMARY.tsv`, and `CROSS_LAYER_SUMMARY.tsv`.

## SUPPORTED_MECHANISM_SIGNAL

- Any mechanism interpretation must be based on concordant TLB, MSHR/PTW/PWC/PTE, requester, cache/queue, and DRAM telemetry; no single counter is causal proof.

## UNRESOLVED

- `REFERENCE_APPROX_SUBENTRY_16` remains a speculative reference approximation.
- `SPECULATIVE_CANDIDATE` and modeled driver-PA semantics do not establish a fabricated hardware cost or causal optimum.
