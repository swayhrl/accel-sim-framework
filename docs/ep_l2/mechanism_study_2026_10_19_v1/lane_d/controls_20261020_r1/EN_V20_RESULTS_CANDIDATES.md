# Standalone English candidates for EN-v20

These are insertion candidates, not edits to the current mother manuscript. Measurements are the four current E-accepted full-application pairs on main61. Controls pending E acceptance have no numerical conclusions here. Speedup is `100(C_S/C_F−1)`; cycle change is `100(C_F/C_S−1)` and must not be substituted for speedup.

## Compact results paragraph

Across the four currently accepted full-application pairs, the complete scheme changes performance by +0.502% for Conv, −0.081% for CFD, −0.670% for DWT, and +0.928% for SAD relative to the traditional organization on the same simulator binary. The geometric-mean speedup of this interim subset is 1.001679×. The preregistered seven-input campaign remains incomplete; this subset mean is not its final aggregate. Reduced cache service demand does not consistently translate into lower program execution time.

## Mechanism paragraph

Conv eliminates 546865 copy reads and 546865 copy writes and reduces physical bank services by 11.923%, while total lower-read bytes change by only −0.0028%. CFD serves 49962 victim-read responses and avoids 51678 line-MSHR allocations, but takes 64 more GPU cycles. DWT serves 23305 victim-read responses and avoids 9965 allocations; despite 13.845% fewer physical bank services and 5.575% fewer lower-read bytes, it takes 1124 more cycles. These event counts measure mechanism activation and service demand, not avoided critical-path stalls. Lower traffic is measured at L2 lower acceptance, rather than at external DRAM service.

## Timing and attribution paragraph

DWT's regressions concentrate in kernels 5 and 8 (+768 and +599 cycles), whereas 98.9% of its landing-wait snapshot increments occur in the faster first kernel. The two regressing kernels have no new RO queries in their corresponding counter windows. This pattern does not identify direct RO lookup delay as the cause of those regressions; earlier state changes and V-path effects remain possible. SAD's first kernel improves by 989 cycles while both runs still report zero cumulative copies; F also records zero victim-read responses and zero RO admissions. Consequently, dynamic copy removal alone does not explain the SAD improvement. Wait counts overlap across requests, slices, reasons, and modules and are not summed into program stall time.

## Tag-detach boundary

All four complete-scheme runs enable Tag detachment but report zero successful detach events across the 64 L2 slices. The current application results therefore do not demonstrate performance gains from executed Tag detachment. This observation does not imply that the enabled path incurs no cost or that its timing equals a disabled implementation. RO transaction admission and line-allocation avoidance are distinct events and must not be reported as successful Tag detachment.

## Control interpretation text, usable before numerical completion

We compare each accepted control against its original valid same-input S/F anchors. On Conv, the W-only and remove-one comparisons measure conditional net effects, including changes in lookup cost, queue timing, allocation, retention, and traffic. The WV-background T/M grid reports both conditional effects and a signed cycle interaction, rather than an additive breakdown of GPU stalls. On DWT, the approved copy-free and W-only controls separate a diagnostic copy-service counterfactual from W organization and the joint effect of V plus RO; they do not identify separate V and RO contributions. On CFD, removing V with RO enabled and removing RO with V enabled probe different backgrounds, so their effects cannot be summed as independent mechanism savings.

## Figure and table insertion map

| Candidate asset | Intended use | Caption boundary |
|---|---|---|
| `accepted_snapshot_01/CURRENT_ACCEPTED_PERFORMANCE.pdf` | Current main performance | Four-input subset; original denominator 7; adverse outcomes retained |
| `FOUR_PAIR_PERFORMANCE_TABLE.tex` | Compact measured cycles and speedup table | Speedup denominator is F cycles |
| `FOUR_PAIR_MECHANISM_TABLE.tex` | Activation/service table | Counters are not causal cycle contributions; lower bytes are not DRAM bandwidth |
| `FOUR_PAIR_MECHANISM_SUMMARY.csv` | Exact raw counts for numerical editing | Signed and zero values retained; waits are nonexclusive |
| `PAIRED_KERNEL_TIMING.pdf` | Where CFD/DWT/SAD elapsed deltas occur | Named duration plus final residual equals whole-program elapsed delta |
| `DWT_STAGE_MECHANISMS.pdf` | DWT timing vs service/query/landing evidence | Counter snapshot increments are not exclusive kernel stalls |
| `accepted_snapshot_01/INCREMENTAL_CONTROL_CONDITIONS.pdf` | Current control coverage/conditional endpoint view | Pending means unmeasured, never zero; COPY_FREE diagnostic; cycle-change axis differs from speedup |

The copied tables and phase figures are byte-identical to the hash-verified prior accepted-data pack. Use the latest incremental snapshot at insertion time. No confidence intervals, significance or repeatability claim is supported by these single paired executions. No control-derived numbers should be inserted until E's corresponding current acceptance is present.
