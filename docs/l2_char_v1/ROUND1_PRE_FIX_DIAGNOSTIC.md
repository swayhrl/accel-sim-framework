# Round-1 pre-fix diagnostic archive

`docs/l2_char_v1/round1_results/` contains preserved raw logs and parsed
artifacts collected with Core `c71c18a41b9a97eb3e62fce50827faf03b0fdbdc`.
The collector sampled DataPort/FillPort after `baseline_cache::cycle()` had
replenished bandwidth, so these results are classified **PRE_FIX_DIAGNOSTIC**.

They may be used for runtime/RSS estimates, parser stress tests, and
non-port preliminary investigation. They must not be included in a formal
Round-1 resource-pressure table or heatmap. Formal runs resume only after the
fixed Instrumentation v1 closeout is reviewed and explicitly unfrozen.
