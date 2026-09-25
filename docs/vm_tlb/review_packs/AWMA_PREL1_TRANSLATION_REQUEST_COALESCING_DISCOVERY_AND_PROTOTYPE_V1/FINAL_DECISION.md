# Final decision

Decision: **PREL1_COALESCER_SUPPORTED_FOR_INDEPENDENT_VALIDATION**

Holdout status: **READY_FOR_INDEPENDENT_HOLDOUT_CAPTURE**

Evidence:

- all directed, full-pipeline and seven-target correctness gates pass;
- capacity is finite (2 entries/SID, 32 waiters/entry), with zero waiter-full
  events in development;
- every target shows actual L1 service suppression, not merely an existing
  MSHR count;
- grouping-only controls are exactly OFF for T0/T1/A2;
- follower head-block cycles are zero on all seven targets;
- A2 is +1.698% in the main model and avoids the proactive-owner pathology;
- same-cycle development has two isolated ~1% regressions (T2/A1), not a
  broad pattern; Level2 attributes them to schedule/pressure changes without a
  root-cause claim;
- +1-cycle compare remains viable: no tested point regresses by more than 1%
  versus OFF, so the mechanism is not marked timing-sensitive.

This is development evidence, not baseline promotion or a paper conclusion.
The source remains frozen at `2bbbceabb5261777fe385289ecb6579791e0f232`.
