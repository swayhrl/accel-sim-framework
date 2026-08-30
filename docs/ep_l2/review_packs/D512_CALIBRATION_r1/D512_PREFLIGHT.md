# D512 natural preflight (B6): PASS

The six required/paired frozen rows are `COMPLETE_VALID` and promoted:

| Row | D256 cycles | D512 cycles | Descriptor p95/max at D512 | Line-MSHR p95/max at D512 |
|---|---:|---:|---:|---:|
| Banked vectorAdd_4M | 73,325 | 73,873 | 339 / 368 | 88 / 110 |
| Banked scan | 2,157,997 | 2,163,356 | 322 / 399 | 95 / 128 |
| Banked spmv | 23,453 | 23,560 | 382 / 403 | 116 / 125 |
| Banked FWT_7_21 | 493,466 | 495,811 | 280 / 383 | 81 / 117 |
| Banked sad | 110,653 | 110,653 | 0 / 84 | 0 / 7 |
| Legacy vectorAdd_4M | 73,325 | 73,873 | 339 / 368 | 88 / 110 |

Natural telemetry above the former 256 capacity is unequivocally represented:
vectorAdd p95/max=339/368, spmv=382/403, scan=322/399, and FWT_7_21=280/383.
All required terminal invariants and payload consistency checks are one.
