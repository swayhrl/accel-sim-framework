# Native CUDA versus current M1 residency semantics

Claim boundary: verified code and frozen native receipts; not actual L2 residency.

| Budget | Requested B | Actual CUDA B | hitRatio | M1 lines/SP | M1 one-class max | 27-later conditional turns |
|---|---|---|---|---|---|---|
| B8 | 8388608 | 8388608 | 0.008825151682 | 4096 | 65536 | 109.265625 |
| B16 | 16777216 | 16777216 | 0.017650303365 | 8192 | 131072 | 54.632812 |
| B24 | 25165824 | 25165824 | 0.026475455047 | 12288 | 196608 | 36.421875 |
| BFULL | 33947648 | 37748736 | 0.035714285714 | 16576 | 265216 | 27.000000 |

Native CUDA overwrites one stream access-policy window immediately before each of 28 `up_proj` invocations in `PREFILL`, `D0`, `D1`, `D2`, and `D3` (140 updates). Each window covers the complete 33,947,648-byte qweight and uses the same budget-derived `hitRatio`, `Persisting` hit property, and `Streaming` miss property. Official CUDA documentation describes approximately random per-access classification, so this proves equal configured opportunity, not exact equal occupancy or survival.

M1 divides one exact protected-line quota over 16 subpartitions. It has no class quota. At full quota, a target can remain protected only by replacing a protected victim in the same set; the oldest protected candidate under baseline recency wins. Class identity is stored for metadata/telemetry but does not enter victim selection.
