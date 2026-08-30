# D512 preflight — interim

Status: **PENDING_RUNNING_SCAN**. B3 has passed, but B6 cannot pass until the
identical frozen Banked `scan` mirror row completes and validates.

| Required evidence | Current state | D512 result / observation |
|---|---|---|
| Banked `vectorAdd_4M` | COMPLETE_VALID | 73,873 cycles; descriptor p95/max 339/368; Line-MSHR p95/max 88/110 |
| Banked `scan` | RUNNING | required long preflight row; no provisional metric is consumed |
| Banked `spmv` | COMPLETE_VALID | 23,560 cycles; descriptor p95/max 382/403; Line-MSHR p95/max 116/125 |
| Banked `FWT_7_21` | COMPLETE_VALID | 495,811 cycles; descriptor p95/max 280/383; Line-MSHR p95/max 81/117 |
| Banked low-pressure `sad` | COMPLETE_VALID | 110,653 cycles; descriptor max 84; Line-MSHR max 7 |
| Legacy paired control `vectorAdd_4M` | COMPLETE_VALID | 73,873 cycles; same descriptor and Line-MSHR values as Banked |

The natural-workload telemetry requirement above 256 is already satisfied:
Banked `vectorAdd_4M` reaches descriptor max **368** and p95 **339**; Banked
`spmv` reaches max **403** and p95 **382**. `FWT_7_21` independently reaches
max 383 and p95 280. This demonstrates that the generalized histogram/parser
path represents values above the former 256 boundary.

Full exact-field pressure and lower-path values are in
`D512_INTERIM_RESOURCE_PRESSURE.csv` and `D512_INTERIM_COMPARISON.csv`.
