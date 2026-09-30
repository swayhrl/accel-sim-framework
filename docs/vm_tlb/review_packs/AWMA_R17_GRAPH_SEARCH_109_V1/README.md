# AWMA R17 Lane F / 109 resident graph-search qualification

Stage `AWMA_R17_GRAPH_SEARCH_109_V1`, execution branch `hrl/awma-r17-graph-search-native-109-v1`, starting HEAD `3e5041f8a04275270fe39032252ea318a368a773`.

Primary decision: **`R17_RECALL_GATE_NOT_QUALIFIED`**. The official normalized GloVe-100-angular input and stable cuVS/CAGRA index qualified, but the frozen six-point Q1 quality grid peaked at recall@10=0.930078 <0.95. The scientific gate stopped before formal latency, persistent, wrapper fallback, profiler and holdout work. `FINAL_DECISION.md` gives raw facts and scope.

Authority: `SOURCE_RUNTIME_RECEIPT.json`, `SOURCE_CAPABILITY_AUDIT.md`, `DATASET_RECEIPT.json`, `QUERY_SPLIT.tsv`, `INDEX_RECEIPT.json`, `PLAN_IDENTITY.tsv`, `QUALITY_CALIBRATION.tsv`, `DISCOVERY_TIMING.tsv`, `STRONG_Q1_SELECTION.md`, `WRAPPER_ACCOUNTING.md`, `FINAL_DECISION.md`, `RUN_RECEIPTS.json`, `RAW_DATA_INDEX.tsv`, `SHA256SUMS`. Large original/derived dataset, one serialized index and detailed raw samples are under the node164 path in `RAW_DATA_INDEX.tsv`; active env/cache remain node109. All actual CUDA/build/search used the shared GPU campaign lock and completed.
