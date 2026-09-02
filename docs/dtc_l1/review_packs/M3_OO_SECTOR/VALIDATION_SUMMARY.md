# M3 HARD-gate validation summary

| Gate | Evidence | Result |
| --- | --- | --- |
| O01/O02 | deterministic older-pending/younger-ready path selects oldest ready; one retirement per model cycle | PASS |
| O03–O06 | valid and pending 128B references contribute one Ref; divergent refs and transition-time shadow checks agree | PASS |
| O07–O09 | Tag eviction clears visibility only; live refs protect physical storage; final and zero-ref reclaim paths are tested | PASS |
| O10/O11 | two pending readers share one lower fill and each waiter wakes exactly once | PASS |
| O12 | slot reuse increments generation; stale waiter cannot name a new PIB entry | PASS |
| O13 | `dtc_l1_bad_generation_test` forks stale fill injection and accepts only child `SIGABRT` | PASS |
| IO-vs-OO causal HOL | same long/short pair blocks FIFO IO while OO retires younger-ready UID first; both retire two identities | PASS |
| Whole-line pre-sector gate | whole-line O01–O13 CTest and PAPER_OO VecAdd strict summary pass before sector implementation | PASS |
| S01–S09 | deterministic sector front-end verifies Valid/Pending/Invalid, one line Ref, two waits/independent fills, stale physical routing, protection, exact masks | PASS |
| sector runtime | mode 4 VecAdd PASS: line misses=16, sector requests/responses/wakeups=64, dependencies=16/16, inflight/PIB/refs/credits drain | PASS |
| regressions | mode 2 and 3 VecAdd PASS after dedicated-mode admission fix; strict parser accepts all modes | PASS |
| hygiene | release build, two CTests, parser bytecode, `git diff --check`; branch clean at review-pack staging | PASS |

The VecAdd pattern reaches all four sectors of each of 16 logical lines, so it
proves real 32B lower request/response cardinality. Pending/valid sector merge
and eviction cases are deterministic directed tests because this workload does
not generate concurrent same-line readers.
