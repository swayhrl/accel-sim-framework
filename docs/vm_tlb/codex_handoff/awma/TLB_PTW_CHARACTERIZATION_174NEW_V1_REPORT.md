# AWMA TLB/PTW characterization report — 174-new

Result: `OPPORTUNITY_PRESENT` within `FIXED_WINDOW_PROGRESS_SENSITIVITY`.

RQ1: The R0 10k window contains L2 TLB port denial, merged translation requesters and PTE traffic. Doubling L2 ports reduces denial events but does not improve same-cycle progress; increasing shared-L2 merge capacity is also weak. These are internal pressure observations, not a proof of a single hardware bottleneck.

RQ2: Ideal identity translation increases completed active thread-instructions from 1,084,480 to 1,697,696 at 10k and from 11,587,872 to 20,458,400 at 50k. It is a diagnostic removal of the functional translation path, not a realizable architecture or full-kernel speedup.

RQ3: The sensitivity remains at 50k, so it is not merely eliminated by extending from 10k. The result remains bounded-window evidence because variants may execute different prefixes.

No mechanism sweep, capacity sweep, segment experiment, full-ROI claim, Native calibration, or new capture was performed.