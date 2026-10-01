# R20R4 CPU-only decision

`R20R4_HYBRID_CANDIDATE_JUSTIFIED_FOR_REVIEW`

The accepted P1 selected-stage time was decomposed per outer solver iteration and joined to accepted P2 active counts with exact per-entry and four-entry closure (1024.802 µs total). Under the sole fixed switch `active_count<=304`, the late region holds 412.097 µs of selected-stage time (40.21% of that stage); its H+blocked-Cholesky targeted portion is 316.418 µs. Relative to accepted P2 formal B0 complete-solver medians, impossible O1 and targeted O2 ideal aggregate headrooms are 15.33% and 11.77%, respectively. O3 is unknown because completed-world overhead is not separately identifiable from aggregate kernel durations.

O2 exceeds the 5% review threshold in aggregate, is positive in all four entries and is not driven by one anomalous entry. The accepted candidate source shows `STRUCTURAL_EARLY_PHASE_SERIALIZATION_PRESENT` above 304 active worlds and exposes the current online device `nsolving` count before the selected stage; a single early-baseline/late-worklist design is therefore documented for review. This is **not** a measured hybrid response and does not overturn the accepted R20R3P2 result that the fixed always-worklist S1 was about 66.6% slower. No GPU operation, profiler, candidate, holdout, hardware mechanism or node174 task was executed in R20R4.
