# AWMA C1 nonblocking sharing causal ablation V1

Status: **COMPLETE / SUPPORTS_ACTUAL_READY_RESULT_REUSE_AS_INDEPENDENT_INCREMENTAL_VALUE**

## Matched intervention

The frozen candidate at `c0602ee06e647d9a3cf84b0adbb8d98075021f99`
is unchanged and was not rerun. The sole diagnostic intervention is
`NONBLOCKING_OWNER_ONLY_NO_SHARE_CONTROL`: same-page legality, group detection,
owner selection, proactive owner translation, nonblocking member fallback,
baseline V1 path, ordering/arbitration, and finite resources are retained;
only member consumption of an already-READY owner result is disabled.

No owner waits or is cancelled, no port/threshold/parameter changes, and every
control reports zero READY shares.

## Three-way development comparison

| target | OFF | OwnerOnly | Frozen candidate | Candidate - OwnerOnly | Candidate vs OwnerOnly |
|---|---:|---:|---:|---:|---:|
| T0 | 527,896 | 1,001,842 | 506,778 | -495,064 | -49.415% |
| T1 | 665,802 | 1,354,934 | 643,076 | -711,858 | -52.538% |
| T2 | 93,079 | 89,689 | 89,689 | 0 | 0.000% |
| SPLITKV | 73,923 | 85,796 | 74,361 | -11,435 | -13.328% |
| COMBINE | 10,480 | 14,153 | 10,484 | -3,669 | -25.924% |

`Candidate - OwnerOnly` is a matched causal contrast on the same
owner/prelaunch structure. It is **not** interpreted as an additive runtime
fraction.

## Attribution

- T0 and T1 are decisively faster with READY-result reuse enabled, supporting
  independent incremental value from actual sharing rather than attributing
  their development speedups only to owner/prelaunch/order effects.
- T2 has zero READY shares in both conditions. Candidate and OwnerOnly are
  exactly equal in cycles and every prespecified matching metric, validating
  the control construction.
- SPLITKV and COMBINE show the same direction: disabling result reuse while
  retaining proactive owners increases cycles and physical lookup work.
- OwnerOnly is much slower than OFF on four targets. Proactive owner work
  without result reuse is therefore a cost, not an alternative explanation
  for the candidate gains on those targets.

All control correctness, coverage, exactly-once, owner-wait/head-block zero,
fallback accounting, and full controller/candidate quiescence gates pass.
`CAUSAL_MATRIX.tsv` retains physical lookup requests, READY shares, fallback
and duplicate work, owner activity, MSHR merges, admissions/re-admissions,
probe counts, and downstream issue timing for both matched conditions.

## Scope and limits

These five targets remain development evidence. The result supports a causal
role for READY-result reuse but does not quantify an additive runtime fraction,
promote a baseline, or establish a final mechanism or paper claim. The
pre-frozen cross-context scientific holdout was not viewed or used. No further
tuning or experiment is authorized by this stage.
