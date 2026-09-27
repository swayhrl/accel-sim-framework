# C16_E1_M1F_STABLE_ADMISSION_PROTOTYPE_V1

Qualification: `M1F_STABLE_ADMISSION_IMPLEMENTATION_QUALIFIED_FOR_TIMING_REVIEW`. This label permits timing review only and does not
authorize a timing run.

The frozen selector enumerated 7,426,048 target lines and selected
130,571, which is
-501 versus the 131,072-line
quota (0.996178x). Existing
hard admission handles actual quota/set constraints; the quota was not changed.

Static selection is approximately distributed, not exact occupancy and not a
survival floor. Global set selected counts have mean
3.984711, p99
9, and max
14; no set has 16 or more
selected lines. Per-class and per-subpartition tables are included.

The CPU-only toy records old-address survival and next-round hits, but omits
L1 filtering, real transaction arrival order, and timing. It is not a C16
performance result. No full C16 replay, GPU collection, or Lane 4 mutation was
performed.
