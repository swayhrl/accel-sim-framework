# Response summary

## Semantic and engineering closure

- Qualification: 24/24 B0 records ended within 128 tokens, parsed as JSON,
  validated against the exact parameters schema, and terminated cleanly.
- Final cohort: first 12 qualifying hashes in canonical order; V0/V1/V2 are
  consecutive B4 partitions.
- Old C1 canary: 72 exact union counts, arm choices, and selected tokens.
- New semantic runs: B0 and M1 were exact for all 12 records; first mismatch is
  `NONE`.

## Local family response

The exact union statistic costs a median 0.073--0.089 ms per step. Despite that
charge, M1's three group-median LIVE_HEAD reductions are:

- V0: 24.16%, 24.48%, 23.98%;
- V1: 31.32%, 30.91%, 33.80%;
- V2: 15.72%, 15.52%, 15.52%.

Every group passes the required 3x-MAD separation. Therefore 3/3 batches are
stable positives; the cross-batch requirement was 2/3 with no stable regression.

## System safety

Complete wall time does not show the prohibited safety pattern. V0 and V1 have
no regression group median. V2 has one +1.12% M1 group, below 2% and not stable;
its other two groups favor M1. The count of stable complete-generation
regression batches above 2% is zero.

## Scope

This validates one exact policy, one exact CPU union algorithm, Qwen2.5-0.5B
BF16, B4, and 12 public parsed function-calling records. It is not a production
distribution, task-accuracy study, threshold study, kernel-tuning result, or
hardware opportunity claim.
