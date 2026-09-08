# B11 final report

**Status: `B11_E01_E10_COMPLETE_READY_FOR_REVIEW`**
**Evidence label: `SPECULATIVE_DIAGNOSTIC`**

B11 executed the frozen E01–E10 package with effective B heavy concurrency one, a 10-second `ADAPTIVE_RESOURCE_V2` gate, per-quantum shared heavy-slot locking, and `/usr/bin/time -v` sidecars. All 12 simulator arms, two one-kernel calibrations, and two 16-kernel static mining tasks pass their recorded completion/conservation contracts.

The PWC finite-32/finite-512/ideal ladder and the 2 MiB diagnostic were realized but showed zero registered cycle deltas in this one-kernel smoke; the VM-disabled/ideal controls instead reduce cycles by -21.029327% and raise IPC by 26.629240%. This is a control-boundary observation, not a full-ROI performance conclusion and not a hit/miss-only conclusion.

E09/E10 static samples contain 16 kernels each. Prefill/decode UNKNOWN lane mass is 80.334728%/92.330575%; Weight is 13.389121%/7.561405%. Those attribution facts are retained as static evidence only. The pack intentionally does not promote any result into full-workload, formal, or candidate-performance evidence.

See `E01_E06_TRANSLATION_AND_PERF.tsv` for joint performance/translation observables, `E07_E08_RSS_CALIBRATION.tsv` for calibration, `E09_E10_STATIC_MINING_SUMMARY.tsv` for static scope, and `HYPOTHESIS_UPDATE.md` for the bounded H1–H6 update.
