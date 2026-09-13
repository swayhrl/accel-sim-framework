# Post-Llama cross-model comparability

Only Llama has an accepted target-qualified memory-trace dataset in this publication. Its prefill `indexSelectLargeIndex` target and decode `indexSelectSmallIndex` target are independently NVBit-mapped and are **not** interchangeable static ranges. The four other model rows are evidence-backed blockers, not zero-valued observations and not comparable measurements.

`STRUCTURAL_ZERO_TARGET_NOT_LAUNCHED` applies only to Llama's LargeIndex target during logical decode; the independent SmallIndex decode target demonstrates that this is not a claim that decode contains no memory accesses.
