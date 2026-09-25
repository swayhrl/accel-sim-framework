# Passive last translation result forwarding V2

Status: **COMPLETE / PASSIVE_V2_SUPPORTED_FOR_INDEPENDENT_VALIDATION**

The source and fixed one-entry/same-cycle timing contract were committed at
`7f9167f9c...` before any development performance run. The future independent
holdout was separately preregistered at `d450b2a06...` and was neither captured
nor executed.

| target | OFF | V2 | speedup | forward hits | lookup suppression |
|---|---:|---:|---:|---:|---:|
| T0 | 527,896 | 522,549 | 1.013% | 2,722,464 | 98.261% |
| T1 | 665,802 | 648,003 | 2.673% | 6,629,952 | 99.128% |
| T2 | 93,079 | 92,362 | 0.770% | 132,544 | 49.170% |
| SPLITKV | 73,923 | 73,915 | 0.011% | 218,862 | 99.238% |
| COMBINE | 10,480 | 10,480 | 0.000% | 1,016 | 99.057% |
| A1 | 114,123 | 115,066 | -0.826% | 116,032 | 46.281% |
| A2 | 117,698 | 112,145 | 4.718% | 116,032 | 46.276% |

A2 is repaired: proactive V1 changed cycles by +6.567% and added 1,100,032
admissions, while V2 changes cycles by -4.718%,
reduces admissions by 331,694,
uses zero proactive owner attempts/duplicate lookups, and reduces physical
lookup requests from 545,916 to
293,289.

All correctness, coverage, exactly-once, controller/memo quiescence, identity,
and zero-wait gates pass. Actual V2 hits happen to equal the prior observer
upper-bound counts on these targets, but this is reported as an empirical
result, not an assumption or required invariant. A1 has the sole regression
(0.826%); it remains below 1% and is not a broad failure pattern.

Physical lookup-request reduction is larger than the forward-hit count because
V2 also removes frozen-V1 resident-access prelaunch and its retry attempts.
Accordingly, `LOOKUP_SUPPRESSION.tsv` reports both quantities separately; the
full request reduction is not mechanically attributed one-for-one to hits.

The same-cycle one-entry compare/forward datapath is a simulator timing model,
not a free lookup claim. Independent validation and later paper qualification
must include timing/PPA sensitivity. No future holdout or node109 capture was
run, and no development result was used to tune the frozen mechanism.
