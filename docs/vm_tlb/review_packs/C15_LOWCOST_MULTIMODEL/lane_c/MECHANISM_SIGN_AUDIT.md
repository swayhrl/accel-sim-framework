# Mechanism sign audit

The final `CROSS_CONFIG_HOLDOUT.tsv` contains 432 rows using the same frozen sample plan on reference and candidate arms. They are historical retrospective tests. 426 rows are `INCONCLUSIVE`; 6 rows are `HISTORICAL_SIGN_AGREEMENT_ONLY`; 0 rows are `SIGN_DISAGREEMENT`; and 36 rows are explicitly confounded. The 48 `STRATIFIED_RANDOM_CHEAP_V1` rows are predeclared random-seed-envelope rows appended after the initial 384-row audit. C13 capacity rows remain tagged `CONFOUNDED_CAPACITY_AND_SEGMENT_NOT_SINGLE_VARIABLE`; no lookup-latency conclusion is made from them.
