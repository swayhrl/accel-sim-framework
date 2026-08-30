# Line-MSHR causal supplement — not a primary matrix axis

| Configuration | Cycles |
| --- | ---: |
| D256 / M128 | 290,308 |
| D256 / M256 | 290,308 |
| D512 / M128 | 292,211 |
| D512 / M256 | 291,108 |

At D512, exact Line-MSHR-full falls `931,416 -> 0`, but cycles improve only
about `0.38%` and pressure moves toward MissQ/WAD/lower path. Classification:
`MSHR_ADMISSION_THROTTLE_DOWNSTREAM_LIMITED`; this does not mean MSHR capacity
is irrelevant. The spmv negative control stays exactly 23,560 cycles at M128
and M256, with no M128 exact-full block.
