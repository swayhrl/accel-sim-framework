# R1 BICG queue-chain and DRAM-service matrix

Every R1 row below natural-exited and strict-PASSed.  All retain the default
DTC GPU-wide lower outstanding cap of 8192, the frozen Core/runtime/trace
identity, observer-on configuration, and 145,666,048 simulated instructions.
The comparator is the accepted default BICG evidence: IO 93,942,704 cycles and
OO 47,231,655 cycles.

| Config | Source-supported change from default | IO cycles | IO delta | OO cycles | OO delta |
|---|---|---:|---:|---:|---:|
| A | L2-to-DRAM queue `64:256:64:64` | 94,719,567 | +0.83% | 47,588,121 | +0.75% |
| B | scheduler queue 64 -> 256 | 95,999,800 | +2.19% | 48,487,452 | +2.66% |
| C | return queue `64:64:256:64`; return FIFO 192 -> 768 | 93,942,704 | +0.00% | 47,231,655 | +0.00% |
| D | 128-entry L2 miss queue plus full queue-chain expansion | 95,999,800 | +2.19% | 46,926,203 | -0.65% |
| E | DRAM clocks `1410:1410:1410:1700` only | 50,713,356 | -46.03% | 29,933,876 | -36.62% |
| F | D plus DRAM clocks `1410:1410:1410:1700` | 50,091,053 | -46.68% | 29,411,883 | -37.73% |

`A` exactly reproduces the accepted 128-entry L2-miss-queue rows under the
registered queue ordering; `C` exactly reproduces the default cycle totals.
The predeclared 5% eligibility condition is met by E and F only.  Fixed
priority selects F first and E second for the bounded GESUMMV validation; no
other configuration is eligible for that work.

The service timing is a simulator-model DRAM clock counterfactual, not a claim
about the physical clock of any particular GPU.
