# Context-prefix diagnostic freeze

Classification: `RETROSPECTIVE_EXISTING_EVIDENCE_DIAGNOSTIC`.

Inputs are immutable files from authority
`2640c4368aea1dc44eb6c34fdc9bb5f738ec3fb2`:

- `WARM_PREFIX_RESULTS.tsv`;
- `Q05_TRANSLATION_RESULTS.tsv`;
- `Q05_DATA_CACHE_RESULTS.tsv`;
- `TRANSLATION_RELEVANT_PAGE_OVERLAP_4K.tsv`;
- `TRANSLATION_RELEVANT_PAGE_OVERLAP_64K.tsv`;
- `F0_KERNEL_BOUNDARY_STATE_MATRIX_FINAL.tsv`.

No simulator run, trace rewrite, parameter selection, or new capture is used.

Primary discriminators:

1. P2 versus P4: equal 4K overlap and equal walk count.
2. P8 versus P16: equal 4K overlap and equal walk count.
3. For each pair, compare cycle direction with L2-miss direction.

Falsifier: a pair with absolute cycle separation above 1% for which the row
with fewer L2 misses is not faster. This disproves the proposed observable set
as a sufficient localized explanation. The threshold marks a material target
response, not a tuning parameter.

Endpoint checks P1 and P34 may show range but cannot serve as independent
holdout because all rows predate this hypothesis.
