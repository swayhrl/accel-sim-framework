# AWMA C1 A2 nonsharing regression attribution V1

Status: `COMPLETE`

Decision:
`SUPPORTS_PROACTIVE_OWNER_PATH_AS_NONSHARING_REGRESSION_MEDIATOR`

## Authorities

- observability: `b85d388abe98e5da70b749b52075c33fad7cede4`
- frozen mechanism: `c0602ee06e647d9a3cf84b0adbb8d98075021f99`
- Pair-A evidence: `9e7e6e3bbe3f3867dbf089ec3b97d5d51507776f`
- diagnostic binary SHA-256:
  `85be8041f590340cf58a9239d941f722d32f25cd7cc633aec855fbd4c33d4d0c`

The mechanism is unchanged.  Reverse-patching the observer transplant restores
every touched frozen file byte-for-byte, while `vm_translation.cc/.h` remain
identical throughout.

## Result

| target | OFF | candidate | response | extra admissions | extra LDST resource stalls |
|---|---:|---:|---:|---:|---:|
| A1 / S2-T2048 | 114123 | 112023 | -1.840% | 76752 | 76752 |
| A2 / T8192 | 117698 | 125427 | +6.567% | 1100032 | 1100032 |

Both contexts have READY-share `0`, fallback `116032`, duplicate physical
lookups `116032`, and zero owner waiting/head blocking.  Result reuse therefore
cannot explain either response.

The proactive path produces extra retry/readmission work in both contexts, and
the additional coverage admissions equal additional source-enum LDST resource
stalls exactly.  A2 amplifies this link by 14.33x versus A1.  In A2 it propagates
to larger L1 pressure, longer ICNT latency, scheduler dependency/structural
blockage, and later progress.  A1 is the matched control: its much smaller
amplification is outweighed by lower cache/scheduler pressure and earlier
progress.

## Hypothesis outcome

- H1 proactive owner retry/readmission amplification: `SUPPORTED_MEDIATOR`
- H2 translation timing to memory backpressure: `SUPPORTED_MEDIATOR`
- H3 translation timing to scheduler dependency/idle: `SUPPORTED_MEDIATOR`
- H4 context dependence remains local to controller ordering:
  `NOT_SUPPORTED_AS_SOLE_LOCATION`
- H5 not localized with available observatory: `REJECTED`

Observed location and mediator are not an additive runtime decomposition.  The
physical context/history condition that converts similar owner attempts into the
14.33x larger A2 amplification remains unresolved.

Level 3 was not run: Level 1/2 already close the differentiating chain, while
Level 3 cannot expose time-windowed repeated-admission attempts or the unresolved
physical context trigger.

## V2 requirements only

- no extra proactive physical lookup when no reusable result exists;
- no added retry/readmission amplification;
- no waiting and no future information;
- no-opportunity behavior should approach frozen OFF semantics.

No V2 was designed or run in this stage.

## Review entry points

- `ATTRIBUTION_REPORT.md`
- `A1_A2_LEVEL1_TRIAGE.tsv`
- `A1_A2_WINDOWED_COMPARISON.tsv`
- `MECHANISM_TELEMETRY_COMPARISON.tsv`
- `PROGRESS_COMPARISON.tsv`
- `HYPOTHESIS_DECISION.tsv`
- `CANDIDATE_SOURCE_FREEZE.tsv`
- `OBSERVATORY_TRANSPLANT_AUDIT.md`
- `VALIDATION_GATES.tsv`
- `RAW_DATA_INDEX.tsv`
- `SHA256SUMS`

No Lane F trace, Lane E modification, passive-reuse V2, or 109 GPU run was used.
