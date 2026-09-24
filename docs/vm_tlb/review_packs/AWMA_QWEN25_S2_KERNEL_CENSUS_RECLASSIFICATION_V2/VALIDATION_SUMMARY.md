# Validation summary

| Check | Result |
|---|---|
| Accepted SQLite SHA verified | PASS |
| Accepted V1 inventory SHA verified | PASS |
| V1/V2 launch count: 34,677 | PASS |
| V2 count conservation | PASS |
| V2 GPU-duration conservation: 154,876,910 ns | PASS |
| Correlation-first phase rule used | PASS |
| GPU overlap used as decision rule | PASS — prohibited and not used |
| New GPU capture | PASS — none performed |
| V1 modified | PASS — no |
| Lane B modified | PASS — no |
| Q/K/V/layer/operator inference | PASS — none |

The script opens SQLite read-only (`mode=ro`) and rejects a V1/V2 launch-count
mismatch or an unexpected 1 Prefill + 32 Decode phase contract.
