# CODEX 109 — Formal Unattended Trace Campaign After Planning

Ownership: ChatGPT
Execution node: 109 / RTX4080
Status: execute only after ChatGPT accepts the final pre-capture planning review pack and freezes `CAPTURE_CAMPAIGN_V1.tsv`.

## Objective

Run the accepted first-wave formal trace campaign for several hours without operator intervention, using only the frozen model/input/runtime identities and frozen target/fallback portfolio.

## Read first

```text
TRACE_QUALITY_CONTRACT_V1.md
UNATTENDED_CAPTURE_POLICY_V1.md
accepted pre-capture planning review pack
accepted CAPTURE_CAMPAIGN_V1.tsv
accepted Pipeline V1 implementation / integration authority
```

## Execution rules

- One formal GPU action at a time.
- Exact frozen model/input/runtime only.
- No retokenization.
- No CPU offload.
- No dtype/context/batch/backend mutation to make a failed row fit.
- Only pre-frozen fallback targets are allowed.
- No arbitrary target discovery during formal execution.
- Every accepted run must be finalized and published through Pipeline V1.
- Failures are recorded and the campaign continues when scientifically safe.

## Per matrix row

1. exact identity/resource preflight;
2. native smoke and output identity check;
3. target identity canary;
4. tiny address-bearing canary;
5. representative-quality gate;
6. formal bounded NVBit capture;
7. local finalize/hash closure;
8. Pipeline V1 publish/verify/ACK;
9. continue next frozen row.

## Bounds

Default per target:

```text
max wall = 20 min
max raw = 4 GiB
```

Initial campaign total raw cap:

```text
64 GiB
```

Clean bound hit => `BOUNDED_PARTIAL`, preserve and publish.

## Failure behavior

Follow `UNATTENDED_CAPTURE_POLICY_V1.md` exactly. In particular:

- exact OOM => classify/skip; never change scientific inputs;
- transient runtime error => one identical fresh-process retry;
- output mismatch => one identical retry, then skip unstable row;
- target mismatch/zero trace => move only to next frozen fallback in same stratum;
- overflow => halve window once, then preserve incomplete diagnostic and continue;
- transfer failure => retain local READY and retry transport, never rerun GPU merely for transport;
- 174 unavailable => queue locally while disk budget is safe.

## Required campaign outputs

```text
FORMAL_CAMPAIGN_EXECUTION.tsv
FORMAL_CAMPAIGN_FAILURES.tsv
FORMAL_CAPTURE_RUN_INDEX.tsv
PIPELINE_PUBLICATION_INDEX.tsv
RESOURCE_ADMISSION_RESULTS.tsv
TARGET_CANARY_RESULTS.tsv
CAMPAIGN_STORAGE_TIME_SUMMARY.md
OPEN_ISSUES.md
```

Each attempted matrix row must appear exactly once in the execution/failure accounting.

## STOP boundary

STOP after all frozen first-wave matrix rows are either:

- formally captured/published;
- cleanly bounded/published;
- or explicitly classified as skipped/failed under the unattended policy.

Do not invent new scientific scenarios or targets after the matrix freeze.
