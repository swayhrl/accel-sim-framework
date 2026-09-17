# Bottleneck decision

`OPPORTUNITY_PRESENT` within `FIXED_WINDOW_PROGRESS_SENSITIVITY`.

RQ1: R0 exposes nonzero L2 TLB port denial, same-translation MSHR merges, and PTE traffic. P2 substantially reduces port-denial events but has no measurable 10k progress change; M8 is also weak. The evidence therefore does not identify either knob as a sufficient single bottleneck remedy.

RQ2: I0 raises completed active thread-instructions by 56.55% at 10k and 76.55% at 50k. This is translation-path diagnostic sensitivity, not a realizable hardware speedup claim.

RQ3: The I0-vs-R0 difference persists at 50k. It is not explained away as only a 10k cold-start effect, but fixed-window prefixes can execute different CTA/warp prefixes and do not establish full-kernel behavior.

No optional probe was selected: P2/M8 are weak and do not provide the evidence trigger for an additional sensitivity experiment.