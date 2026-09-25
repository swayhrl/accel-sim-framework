# Passive translation result reuse opportunity V1

Status: **COMPLETE / PASSIVE_REUSE_OPPORTUNITY_SUPPORTED**

Across all seven accepted targets, baseline execution naturally creates legal
instruction-local results that later same-page accesses could reuse. The
4-entry observer finds 9,936,902 validated hits from 11,714,081
logical decision-point lookups (84.829%). Relative to
the separately reported baseline physical-lookup counter, this is
11.579%; event definitions differ, so this ratio is
an opportunity indicator rather than an exact subtractive prediction.

One entry captures exactly the same hits as two or four entries on every
target. Every observed hit has zero intervening natural completions. T0/T1,
the dominant native instruction-weight targets, contribute millions of hits;
opportunity also appears in decode GEMV, SplitKV, Combine, and both Pair-A
contexts. This supports a broad, low-storage opportunity rather than a narrow
kernel exception.

Retrospectively, passive and proactive counts are not one-to-one: proactive
READY delivery changes translation timing, while passive hits are measured at
the unmodified baseline decision point after prior natural apply. Notably, T2
has 132,544 passive hits despite zero proactive READY deliveries, and Pair A
has 116,032 passive hits in each context despite zero proactive sharing.

Observer OFF and ON exactly preserve cycles, instructions, CTA, UID, coverage,
physical lookup requests, ICNT memory transactions, duplicate-application
count, terminal completion, and controller quiescence for every target. No
performance mechanism was implemented or run. V2 remains design-only.
