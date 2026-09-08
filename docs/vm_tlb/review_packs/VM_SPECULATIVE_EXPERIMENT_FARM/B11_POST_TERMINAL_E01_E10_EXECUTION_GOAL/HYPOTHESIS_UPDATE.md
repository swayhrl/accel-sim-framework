# B11 hypothesis update

All entries are **SPECULATIVE_DIAGNOSTIC**. E01–E06 are one-kernel simulator smokes; E09/E10 are metadata-matched static 16-kernel samples. Neither is full-ROI evidence.

| Hypothesis | B11 status | Evidence and limit |
|---|---|---|
| H1 phase structure | UNRESOLVED | Same-budget static samples differ descriptively (prefill/decode UNKNOWN 80.334728%/92.330575%; equal-width adjacency 41.368606%/67.940676%), but metadata matching is not dynamic matching or full-phase evidence. |
| H2 PWC/PTW sensitivity | WEAKENED | E01–E03 realize finite-32, finite-512, and ideal PWC, yet their registered ladder pair deltas are 0 for the reported performance/translation metrics. This weakens the prior one-kernel PWC sensitivity signal only at this smoke scope. |
| H3 Weight Segment coverage limit | SUPPORTED | Static classified Weight lanes are only 13.389121% prefill and 7.561405% decode while UNKNOWN is high. This supports an attribution/coverage ceiling, not a Segment performance claim. |
| H4 post-L1 sibling locality | UNRESOLVED | No B11 arm measures the C-owned post-L1 sibling occupancy falsifier. |
| H5 conventional VM importance | UNRESOLVED | VM-disabled/ideal controls change this smoke from 17390 to 13733 cycles (-21.029327%) and IPC from 116.1201 to 147.0420 (26.629240%), while the 2 MiB diagnostic cycle delta is 0.000000%. There is no full-ROI or candidate comparison to rank mechanisms. |
| H6 UNKNOWN attribution risk | SUPPORTED | E09 UNKNOWN lane fractions: prefill 80.334728%; decode1 92.330575%. UNKNOWN remains distinct and is not reassigned. |
