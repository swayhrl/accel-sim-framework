# EP-L2 Target Baseline interim (22 of 26)

This is a **provisional**, analysis-ready 850-MHz snapshot. It includes only
the 22 `COMPLETE_VALID` C5c-after-fix runs and explicitly excludes historical
blocked/diagnostic results and all raw logs.

## Source provenance

* Formal simulator Core: `200cb485c2fe27a7b0a867d2f173b63582fcaece`
* Formal simulator Framework: `81b9dfbc0c567590fc35724cbec94ade1d3f6aa9`
* Framework branch also contains the non-simulator packaging tool commit
  `7b1ebd0f6da84e8da346fa31a8525a4e21fbf8e5`.
* Frequency: 850 MHz only. No 1-GHz, Unified, RO, or TVD result is included.

## Important attribution hold

Do not treat B0-Banked cycle deltas or the historical `bank_conflicts`/
`block_bank` values as architecture evidence. The C6 audit found an
unconditional idle-bank staging/retry cycle that is counted as a conflict.
See [the hold](target_baseline_results_c5c/TARGET_BASELINE_INTERIM_BANKED_ATTRIBUTION_HOLD.md)
and the [C6 source/direct audit](target_baseline_results_c5c/C6_BANK_ARBITRATION_AUDIT.md).

## Browseable artifacts

* [Run status](target_baseline_results_c5c/TARGET_BASELINE_INTERIM_STATUS.tsv)
* [Paired comparison](target_baseline_results_c5c/target_baseline_interim_comparison.csv)
* [Resource pressure](target_baseline_results_c5c/target_resource_pressure.csv)
* [Blocking matrix](target_baseline_results_c5c/target_blocking_matrix.csv)
* [Bank pressure](target_baseline_results_c5c/target_bank_pressure.csv)
* [Lower path](target_baseline_results_c5c/target_lower_path.csv)
* [Bottleneck notes](target_baseline_results_c5c/TARGET_BASELINE_INTERIM_BOTTLENECKS.md)
* [Bank bookkeeping audit](target_baseline_results_c5c/target_banked_arbitration_audit_11pairs.csv)
* [Compressed review pack](review_packs/target_baseline_interim_22of26_analysis_pack.tar.gz)

The review pack includes the listed analysis artifacts, 22 run manifests,
statuses, summaries, parser/aggregation scripts, B0 overlays, schema note, and
SHA256SUMS; it contains no `raw.log` or `raw.log.gz` payload.
