# Post-review direct backend phase evidence

This addendum follows REVIEW_CLARIFICATION.md. It preserves the review timeline: the original phase claim was correctly narrowed when only virtual-relief preview phases and global backend counts were available. Agent A subsequently extracted existing actual backend PHASE counters under a separate Main-approved bounded read; this new evidence closes the specific missing phase measurement. Neither the original numerical comparison nor the CSV changed.

## Direct evidence now available

Agent A read three accepted diagnostic ON raw streams once, 70,235,553 logical bytes total, under Main's explicitly raised 72 MiB cap. Accepted point, exact Source/input/spec/raw identities and same-mode NI are referenced in its receipt. Agent B did not reread any raw; it verified the small summary SHA references, phase catalog and all-counter phase-to-slice-to-global closure reports. Agent D independently reviews these same summaries.

| Actual backend events during active-kernel interval | A F_MINUS_T | B LEGACY_F | C CORRECTED_F |
|---|---:|---:|---:|
| Rows detach_success |0|237|360|
| Columns detach_success |0|0|0|
| Rows triggering request accepted immediately after detach |0|237|353|
| Rows triggering request denied immediately after detach |0|0|7|
| Rows detached old transaction retired |0|237|360|

PROVEN: actual backend detach events all occur during the Rows single-active interval in these accepted applications. Columns has zero actual detach and zero RO admissions, merges, responses and retirements in its PHASE counters. This is direct backend phase evidence, not a conclusion inferred from preview/global count equality. Unassigned/overlap phases have zero detach, and phase totals close to slice/global counters.

The phase identifies the active execution interval, not the old RO owner's kernel or an end-to-end triggering UID chain. C's 353 immediate accepts plus 7 immediate denials follow 360 detaches; eventual completion of those exact triggering UIDs is still NOT_MEASURED. Full application drain remains accepted independently. No negative result is hidden by equating successful detach with immediate request acceptance.

## Remaining boundaries

- The 63 ordinary / 297 RO-candidate split remains a frontend virtual-relief preview classification. PHASE has no backend requester-class split; do not upgrade those two numbers to separately measured backend ordinary/RO detach counts.
- The 2954 issued / paid query exposure remains cumulative per-slice only. Its per-kernel distribution is NOT_INSTRUMENTED, and it cannot be subtracted from GPU cycles.
- All actual detach occurring in Rows while Rows slows654 and Columns improves3308 strengthens the indirect-state/scheduling interpretation of successor-kernel changes. The specific carrier (cache/TVD/queue/arrival order) and critical-path cost attribution remain UNKNOWN; zero Columns detach does not identify which carrier caused the improvement.
- No new Source, collector, application launch or resource modification was made for the phase read. This addendum reuses Agent A's new small summaries only. Earlier review files remain historical evidence of why the additional observation was necessary.

## Exact source references

- `/root/data/ep_l2_full_workload_performance_20261027_v1/research/mechanism_attribution_20261103_v1/agent_a/BOUNDED_PHASE_READ_RECEIPT.json` SHA256 `9b129714aaef2bc882a094a5fb108766d7a44c947c507586ebb67603cc1059ab`
- `/root/data/ep_l2_full_workload_performance_20261027_v1/research/mechanism_attribution_20261103_v1/agent_a/A_F_MINUS_T_ACCEPTED_FINAL_PHASE.json` SHA256 `558a152841ab73588041352cafdc95f9c1181c41e9b07ea49e87f27fb698b1fa`
- `/root/data/ep_l2_full_workload_performance_20261027_v1/research/mechanism_attribution_20261103_v1/agent_a/B_LEGACY_F_ACCEPTED_FINAL_PHASE.json` SHA256 `7a6f7c873f0544354f057ccada578d28fe8b1df4c627d43e9149fc0d3cb5f859`
- `/root/data/ep_l2_full_workload_performance_20261027_v1/research/mechanism_attribution_20261103_v1/agent_a/C_CORRECTED_F_ACCEPTED_FINAL_PHASE.json` SHA256 `a455a7bc2065fa56069ebc130e1e30ca2de5d3e27815b86263587bb4c5adb08c`
