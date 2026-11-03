# BICG closed-source DRAM controller read-work distribution

This read-only projection consumes the frozen four-source BICG packet. Counts are32B issued-read atoms, not latency or occupancy. CV uses the20 controller totals. No missing controller is imputed and every interval sum is checked against the source total.

| Design | F | Scope | Total reads | Min/controller | Max/controller | CV | Hottest share |
|---|---|---|---:|---:|---:|---:|---:|
| CH | P0 | K2_PRINT_INTERVAL | 13415640 | 136820 | 1211644 | 0.788317 | 9.032% |
| CH | P0 | CUMULATIVE_THROUGH_K2 | 15513224 | 241780 | 1316348 | 0.681721 | 8.485% |
| DH | F128 | K2_PRINT_INTERVAL | 15858500 | 100164 | 1491716 | 0.873363 | 9.406% |
| DH | F128 | CUMULATIVE_THROUGH_K2 | 17956084 | 205084 | 1596676 | 0.771335 | 8.892% |
| DH | P0 | K2_PRINT_INTERVAL | 15591280 | 91648 | 1472252 | 0.882278 | 9.443% |
| DH | P0 | CUMULATIVE_THROUGH_K2 | 17688864 | 196352 | 1577212 | 0.777652 | 8.916% |
| CH | F128 | K2_PRINT_INTERVAL | 12328204 | 121760 | 1118068 | 0.796474 | 9.069% |
| CH | F128 | CUMULATIVE_THROUGH_K2 | 14425788 | 226464 | 1222772 | 0.680657 | 8.476% |

The equal-share reference is5% per controller. These cumulative and print-boundary distributions alone do not establish a critical-path cause, actual queue contention, per-bank balance or scheduling fairness. Their limitations are listed in READ_DISTRIBUTION.json. Consume the original BICG packet together with its forward typed-field/active-path clarification. No experiment, input, owner, budget, historical file or manuscript is changed.
